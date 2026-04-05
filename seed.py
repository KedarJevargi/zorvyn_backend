import asyncio
from app.database import async_session
from app.models.user import User, UserRole
from app.core.security import hash_password
from sqlalchemy import select


from app.models import user, record, refresh_token  # noqa: F401

async def seed():
    async with async_session() as db:
        # check if admin already exists
        result = await db.execute(select(User).where(User.email == "admin@zorvyn.com"))
        if result.scalar_one_or_none():
            print("Admin already exists")
            return
        
        admin = User(
            name="Admin",
            email="admin@zorvyn.com",
            hashed_password=hash_password("admin123"),
            role=UserRole.admin
        )
        db.add(admin)
        await db.commit()
        print("Admin created successfully")

if __name__ == "__main__":
    asyncio.run(seed())