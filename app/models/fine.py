"""Fine entity."""

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.loan import Loan


class FineStatus(StrEnum):
    """Lifecycle states of a fine."""

    PENDING = "pending"
    PAID = "paid"
    WAIVED = "waived"


fine_status_enum = SAEnum(
    FineStatus,
    name="fine_status",
    native_enum=False,
    length=20,
    values_callable=lambda enum: [member.value for member in enum],
)


class Fine(Base, TimestampMixin):
    """A monetary penalty associated with an overdue loan."""

    __tablename__ = "fines"

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_id: Mapped[int] = mapped_column(
        ForeignKey("loans.id", ondelete="CASCADE"), unique=True, index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    reason: Mapped[str] = mapped_column(String(255))
    status: Mapped[FineStatus] = mapped_column(
        fine_status_enum, default=FineStatus.PENDING, index=True
    )
    paid_at: Mapped[date | None] = mapped_column(Date)

    loan: Mapped["Loan"] = relationship(back_populates="fine")
