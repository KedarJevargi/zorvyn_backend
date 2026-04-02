import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Boolean, DateTime, func, Enum
from datetime import datetime
from app.database import Base




class RecordType(str, enum.Enum):
    income = "income"
    expense = "expense"



class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[float] = mapped_column()
    type: Mapped[RecordType] = mapped_column(Enum(RecordType))
    category: Mapped[str] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="records")    
