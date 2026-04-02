from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.user import UserRegister, UserLogin
from app.schemas.token import TokenResponse
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token
)


async def register_user(db: AsyncSession, data: UserRegister) -> User:
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login_user(db: AsyncSession, data: UserLogin) -> TokenResponse:
    result = await db.execute(
        select(User).where(User.email == data.email, User.is_deleted == False, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    db_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    db.add(db_token)
    await db.commit()
    
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> TokenResponse:
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError()
        user_id = int(payload.get("sub"))
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == refresh_token,
            RefreshToken.is_revoked == False
        )
    )
    db_token = result.scalar_one_or_none()
    if not db_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked or not found")
    
    new_access_token = create_access_token(subject=user_id)
    return TokenResponse(access_token=new_access_token, refresh_token=refresh_token)


async def logout_user(db: AsyncSession, refresh_token: str) -> None:
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token)
    )
    db_token = result.scalar_one_or_none()
    if db_token:
        db_token.is_revoked = True
        await db.commit()