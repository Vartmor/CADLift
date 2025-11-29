from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any, Dict
from uuid import uuid4

from jose import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(subject: str, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload: Dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "jti": uuid4().hex,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str) -> str:
    expires = timedelta(minutes=settings.access_token_expire_minutes)
    return _create_token(subject, expires)


def create_refresh_token(subject: str) -> str:
    expires = timedelta(minutes=settings.refresh_token_expire_minutes)
    return _create_token(subject, expires)


def hash_refresh_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()
