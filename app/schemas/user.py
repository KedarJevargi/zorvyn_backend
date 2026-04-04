from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class UserRegister(BaseModel):
    """Schema for user registration request."""
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Schema for user login request."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for returning user data in API responses. Excludes sensitive fields like password."""
    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RoleUpdateRequest(BaseModel):
    """Schema for updating a user's role. Admin only."""
    role: UserRole


class StatusUpdateRequest(BaseModel):
    """Schema for activating or deactivating a user. Admin only."""
    is_active: bool


