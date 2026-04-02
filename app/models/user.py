import enum
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, func, Enum

from app.database import Base


class UserRole(str, enum.Enum):
    viewer = "viewer"
    analyst = "analyst"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False),
        default=UserRole.viewer,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

    records: Mapped[list["FinancialRecord"]] = relationship(
    "FinancialRecord",
    back_populates="user"
)

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )