import asyncio
from app.services.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select

async def reset_password():
    email = "test@email.com"
    new_password = "password123"
    hashed = hash_password(new_password)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user:
            user.password_hash = hashed
            await session.commit()
            print(f"Password for {email} reset to: {new_password}")
        else:
            print(f"User {email} not found")

if __name__ == "__main__":
    asyncio.run(reset_password())
