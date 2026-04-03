import enum
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    ForeignKey, String, Boolean, DateTime, func,
    Enum, Numeric, Index, CheckConstraint
)
from app.database import Base

class RecordType(str, enum.Enum):
    income = "income"
    expense = "expense"

class FinancialRecord(Base):
    __tablename__ = "financial_records"
    __table_args__ = (
        Index("idx_user_date", "user_id", "date"),
        Index("idx_user_type", "user_id", "type"),
        Index("idx_user_category", "user_id", "category"),
        CheckConstraint("amount >= 0", name="check_amount_positive"),
        CheckConstraint(
            "(is_deleted = FALSE AND deleted_at IS NULL) OR "
            "(is_deleted = TRUE AND deleted_at IS NOT NULL)",
            name="check_soft_delete_consistency"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    type: Mapped[RecordType] = mapped_column(Enum(RecordType, native_enum=False), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=func.now(),nullable=False,index=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="records")