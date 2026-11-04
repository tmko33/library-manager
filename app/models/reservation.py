"""Reservation entity."""

from datetime import date
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.member import Member


class ReservationStatus(StrEnum):
    """Lifecycle states of a reservation."""

    PENDING = "pending"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


reservation_status_enum = SAEnum(
    ReservationStatus,
    name="reservation_status",
    native_enum=False,
    length=20,
    values_callable=lambda enum: [member.value for member in enum],
)


class Reservation(Base, TimestampMixin):
    """A member's place in the waiting queue for a book."""

    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"), index=True)
    status: Mapped[ReservationStatus] = mapped_column(
        reservation_status_enum, default=ReservationStatus.PENDING, index=True
    )
    expires_at: Mapped[date | None] = mapped_column(Date)

    book: Mapped["Book"] = relationship(back_populates="reservations")
    member: Mapped["Member"] = relationship(back_populates="reservations")
