from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
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
    role: UserRole


class StatusUpdateRequest(BaseModel):
    is_active: bool


