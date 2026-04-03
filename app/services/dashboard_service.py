from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.record import FinancialRecord, RecordType
from datetime import datetime


async def get_summary(
    db: AsyncSession,
    date_from: datetime | None = None,
    date_to: datetime | None = None
) -> dict:
    query = select(
        func.coalesce(func.sum(FinancialRecord.amount).filter(FinancialRecord.type == RecordType.income), 0).label("total_income"),
        func.coalesce(func.sum(FinancialRecord.amount).filter(FinancialRecord.type == RecordType.expense), 0).label("total_expenses"),
    ).where(FinancialRecord.is_deleted == False)

    if date_from:
        query = query.where(FinancialRecord.date >= date_from)
    if date_to:
        query = query.where(FinancialRecord.date <= date_to)

    result = await db.execute(query)
    row = result.one()
    return {
        "total_income": row.total_income,
        "total_expenses": row.total_expenses,
        "net_balance": row.total_income - row.total_expenses
    }


async def get_category_totals(
    db: AsyncSession,
    date_from: datetime | None = None,
    date_to: datetime | None = None
) -> list[dict]:
    query = select(
        FinancialRecord.category,
        FinancialRecord.type,
        func.sum(FinancialRecord.amount).label("total")
    ).where(FinancialRecord.is_deleted == False)

    if date_from:
        query = query.where(FinancialRecord.date >= date_from)
    if date_to:
        query = query.where(FinancialRecord.date <= date_to)

    query = query.group_by(FinancialRecord.category, FinancialRecord.type).order_by(func.sum(FinancialRecord.amount).desc())
    result = await db.execute(query)
    return [{"category": r.category, "type": r.type, "total": r.total} for r in result.all()]


async def get_trends(
    db: AsyncSession,
    period: str = "monthly",
    date_from: datetime | None = None,
    date_to: datetime | None = None
) -> list[dict]:
    trunc = func.date_trunc("month" if period == "monthly" else "week", FinancialRecord.date)

    query = select(
        trunc.label("period"),
        FinancialRecord.type,
        func.sum(FinancialRecord.amount).label("total")
    ).where(FinancialRecord.is_deleted == False)

    if date_from:
        query = query.where(FinancialRecord.date >= date_from)
    if date_to:
        query = query.where(FinancialRecord.date <= date_to)

    query = query.group_by(trunc, FinancialRecord.type).order_by(trunc)
    result = await db.execute(query)
    return [{"period": str(r.period), "type": r.type, "total": r.total} for r in result.all()]


async def get_recent_activity(
    db: AsyncSession,
    limit: int = 10,
    date_from: datetime | None = None,
    date_to: datetime | None = None
) -> list[FinancialRecord]:
    query = select(FinancialRecord).where(FinancialRecord.is_deleted == False)

    if date_from:
        query = query.where(FinancialRecord.date >= date_from)
    if date_to:
        query = query.where(FinancialRecord.date <= date_to)

    query = query.order_by(FinancialRecord.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()