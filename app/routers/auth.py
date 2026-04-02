from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import UserRegister, UserLogin, UserResponse
from app.services.auth_service import register_user, login_user, refresh_access_token, logout_user
from app.core.dependencies import get_current_user
from app.models.user import User

from app.schemas.token import RefreshRequest, LogoutRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])




@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    return await register_user(db, data)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await login_user(db, data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await refresh_access_token(db, data.refresh_token)


@router.post("/logout", status_code=204)
async def logout(data: LogoutRequest, db: AsyncSession = Depends(get_db)):
    await logout_user(db, data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user