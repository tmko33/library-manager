"""Book copy entity (a single physical item)."""

from datetime import date
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.branch import Branch
    from app.models.loan import Loan


class CopyStatus(StrEnum):
    """Lifecycle states of a physical copy."""

    AVAILABLE = "available"
    ON_LOAN = "on_loan"
    RESERVED = "reserved"
    LOST = "lost"
    MAINTENANCE = "maintenance"


copy_status_enum = SAEnum(
    CopyStatus,
    name="copy_status",
    native_enum=False,
    length=20,
    values_callable=lambda enum: [member.value for member in enum],
)


class BookCopy(Base, TimestampMixin):
    """A single lendable copy of a :class:`~app.models.book.Book`."""

    __tablename__ = "book_copies"

    id: Mapped[int] = mapped_column(primary_key=True)
    inventory_code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), index=True)
    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id", ondelete="RESTRICT"), index=True
    )
    status: Mapped[CopyStatus] = mapped_column(
        copy_status_enum, default=CopyStatus.AVAILABLE, index=True
    )
    acquired_at: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)

    book: Mapped["Book"] = relationship(back_populates="copies")
    branch: Mapped["Branch"] = relationship(back_populates="copies")
    loans: Mapped[list["Loan"]] = relationship(back_populates="copy")
