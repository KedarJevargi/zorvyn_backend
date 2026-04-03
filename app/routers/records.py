from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.record import RecordCreate, RecordUpdate, RecordFilter, RecordResponse
from app.services.record_service import create_record, get_records, get_record_by_id, restore_record, update_record, delete_record
from app.core.dependencies import get_current_admin, get_current_analyst_or_admin

router = APIRouter(prefix="/records", tags=["Records"])


@router.get("/", response_model=list[RecordResponse])
async def list_records(
    type: str | None = None,
    category: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = 1,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_analyst_or_admin)
):
    filters = RecordFilter(type=type, category=category, date_from=date_from, date_to=date_to, page=page, limit=limit)
    return await get_records(db, filters)


@router.get("/{record_id}", response_model=RecordResponse)
async def get_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_analyst_or_admin)
):
    return await get_record_by_id(db, record_id)


@router.post("/", response_model=RecordResponse, status_code=201)
async def create_new_record(
    data: RecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return await create_record(db, data, current_user.id)


@router.patch("/{record_id}", response_model=RecordResponse)
async def update_existing_record(
    record_id: int,
    data: RecordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return await update_record(db, record_id, data)


@router.delete("/{record_id}", status_code=204)
async def delete_existing_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    await delete_record(db, record_id)

@router.patch("/{record_id}/restore", response_model=RecordResponse)
async def restore_existing_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return await restore_record(db, record_id)    