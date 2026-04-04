from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from app.models.record import FinancialRecord, RecordType
from app.schemas.record import RecordCreate, RecordUpdate, RecordFilter


async def create_record(db: AsyncSession, data: RecordCreate, user_id: int) -> FinancialRecord:
    """Create a new financial record assigned to the given user."""
    record = FinancialRecord(
        user_id=user_id,
        amount=data.amount,
        type=data.type,
        category=data.category,
        notes=data.notes,
        date=data.date or datetime.now(timezone.utc)
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_records(db: AsyncSession, filters: RecordFilter) -> list[FinancialRecord]:
    """Fetch paginated financial records with optional filtering by type, category, date and notes search."""
    query = select(FinancialRecord).where(FinancialRecord.is_deleted == False)
    
    if filters.type:
        query = query.where(FinancialRecord.type == filters.type)
    if filters.category:
        query = query.where(FinancialRecord.category == filters.category)
    if filters.date_from:
        query = query.where(FinancialRecord.date >= filters.date_from)
    if filters.date_to:
        query = query.where(FinancialRecord.date <= filters.date_to)
    if filters.search:
        query = query.where(FinancialRecord.notes.ilike(f"%{filters.search}%"))
    
    offset = (filters.page - 1) * filters.limit
    query = query.offset(offset).limit(filters.limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_record_by_id(db: AsyncSession, record_id: int) -> FinancialRecord:
    """Fetch a single financial record by ID. Raises 404 if not found or soft deleted."""
    result = await db.execute(
        select(FinancialRecord).where(
            FinancialRecord.id == record_id,
            FinancialRecord.is_deleted == False
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


async def update_record(db: AsyncSession, record_id: int, data: RecordUpdate) -> FinancialRecord:
    """Partially update a financial record by ID."""
    record = await get_record_by_id(db, record_id)
    
    if data.amount is not None:
        record.amount = data.amount
    if data.type is not None:
        record.type = data.type
    if data.category is not None:
        record.category = data.category
    if data.notes is not None:
        record.notes = data.notes
    if data.date is not None:
        record.date = data.date
    
    await db.commit()
    await db.refresh(record)
    return record


async def delete_record(db: AsyncSession, record_id: int) -> None:
    """Soft delete a financial record by setting is_deleted=True."""
    record = await get_record_by_id(db, record_id)
    record.is_deleted = True
    record.deleted_at = datetime.now(timezone.utc)
    await db.commit()

async def restore_record(db: AsyncSession, record_id: int) -> FinancialRecord:
    """Restore a soft deleted financial record."""
    result = await db.execute(
        select(FinancialRecord).where(
            FinancialRecord.id == record_id,
            FinancialRecord.is_deleted == True
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found or not deleted")
    
    record.is_deleted = False
    record.deleted_at = None
    await db.commit()
    await db.refresh(record)
    return record    