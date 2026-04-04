from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, field_validator
from app.models.record import RecordType


class RecordCreate(BaseModel):
    """Schema for creating a new financial record."""
    amount: Decimal
    type: RecordType
    category: str
    notes: Optional[str] = None
    date: Optional[datetime] = None

    @field_validator("category")
    def normalize_category(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("amount")
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class RecordUpdate(BaseModel):
    """Schema for partially updating a financial record. All fields optional."""
    amount: Optional[Decimal] = None
    type: Optional[RecordType] = None
    category: Optional[str] = None
    notes: Optional[str] = None
    date: Optional[datetime] = None

    @field_validator("category")
    def normalize_category(cls, v: str) -> str:
        return v.strip().lower()


class RecordResponse(BaseModel):
    """Schema for returning financial record data in API responses."""
    id: int
    user_id: int
    amount: Decimal
    type: RecordType
    category: str
    notes: Optional[str] = None
    date: datetime
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}




class RecordFilter(BaseModel):
    """Query parameters for filtering and paginating financial records."""
    type: Optional[RecordType] = None
    category: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None
    page: int = 1
    limit: int = 10

    @field_validator("type", mode="before")
    def strip_type(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v