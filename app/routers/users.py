from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, RoleUpdateRequest, StatusUpdateRequest
from app.services.user_service import get_all_users, get_user_by_id, update_user_role, update_user_status
from app.core.dependencies import get_current_admin, get_current_analyst_or_admin

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
async def list_users(
    is_active: bool | None = None,
    is_deleted: bool | None = None,
    role: UserRole | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return await get_all_users(db, is_active, is_deleted, role)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return await get_user_by_id(db, user_id)


@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_role(
    user_id: int,
    data: RoleUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return await update_user_role(db, user_id, data.role)


@router.patch("/{user_id}/status", response_model=UserResponse)
async def update_status(
    user_id: int,
    data: StatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return await update_user_status(db, user_id, data.is_active)