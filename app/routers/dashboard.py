from enum import Enum
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.record import RecordResponse
from app.services.dashboard_service import get_summary, get_category_totals, get_trends, get_recent_activity
from app.core.dependencies import get_current_active_user


class TrendPeriod(str, Enum):
    monthly = "monthly"
    weekly = "weekly"


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])



@router.get("/summary")
async def summary(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await get_summary(db, date_from, date_to)


@router.get("/categories")
async def category_totals(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await get_category_totals(db, date_from, date_to)


@router.get("/trends")
async def trends(
    period: TrendPeriod = TrendPeriod.monthly,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await get_trends(db, period.value, date_from, date_to)


@router.get("/recent", response_model=list[RecordResponse])
async def recent_activity(
    limit: int = 10,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await get_recent_activity(db, limit, date_from, date_to)