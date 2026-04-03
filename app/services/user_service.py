from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User, UserRole


async def get_all_users(
    db: AsyncSession,
    is_active: bool | None = None,
    is_deleted: bool | None = None,
    role: UserRole | None = None
) -> list[User]:
    query = select(User)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    if is_deleted is not None:
        query = query.where(User.is_deleted == is_deleted)
    if role is not None:
        query = query.where(User.role == role)
    result = await db.execute(query)
    return result.scalars().all()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def update_user_role(db: AsyncSession, user_id: int, role: UserRole) -> User:
    user = await get_user_by_id(db, user_id)
    user.role = role
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_status(db: AsyncSession, user_id: int, is_active: bool) -> User:
    user = await get_user_by_id(db, user_id)
    user.is_active = is_active
    await db.commit()
    await db.refresh(user)
    return user