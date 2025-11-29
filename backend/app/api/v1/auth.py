from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import deps
from app.core.config import get_settings
from app.models import User, RefreshToken
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshRequest,
    LogoutRequest,
)
from app.schemas.user import UserRead
from app.services.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    hash_refresh_token,
)

from jose import jwt

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


async def issue_tokens(
    user: User,
    session: AsyncSession,
    request: Request,
) -> TokenResponse:
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    session.add(token_record)
    await session.commit()
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.model_validate(user),
    )


@router.post("/register", response_model=TokenResponse)
async def register_user(
    payload: RegisterRequest,
    request: Request,
    session: AsyncSession = Depends(deps.get_db),
):
    result = await session.execute(select(User).where(User.email == payload.email.lower()))
    if result.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
        locale=payload.locale,
        theme=payload.theme,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return await issue_tokens(user, session, request)


@router.post("/login", response_model=TokenResponse)
async def login_user(
    payload: LoginRequest,
    request: Request,
    session: AsyncSession = Depends(deps.get_db),
):
    result = await session.execute(select(User).where(User.email == payload.email.lower()))
    user = result.scalars().first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return await issue_tokens(user, session, request)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    payload: RefreshRequest,
    request: Request,
    session: AsyncSession = Depends(deps.get_db),
):
    try:
        decoded = jwt.decode(payload.refresh_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = decoded.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    token_hash_value = hash_refresh_token(payload.refresh_token)
    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash_value,
            RefreshToken.revoked_at.is_(None),
        )
    )
    stored_token = result.scalars().first()
    if not stored_token or stored_token.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    stored_token.revoked_at = datetime.now(timezone.utc)
    await session.commit()

    user_result = await session.execute(select(User).where(User.id == user_id))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return await issue_tokens(user, session, request)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: LogoutRequest,
    session: AsyncSession = Depends(deps.get_db),
):
    if not payload.refresh_token:
        return
    token_hash_value = hash_refresh_token(payload.refresh_token)
    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash_value,
            RefreshToken.revoked_at.is_(None),
        )
    )
    stored_token = result.scalar_one_or_none()
    if stored_token:
        stored_token.revoked_at = datetime.now(timezone.utc)
        await session.commit()
