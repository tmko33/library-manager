"""Loan entity."""

from datetime import date
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.book_copy import BookCopy
    from app.models.fine import Fine
    from app.models.member import Member


class LoanStatus(StrEnum):
    """Lifecycle states of a loan."""

    ACTIVE = "active"
    RETURNED = "returned"
    OVERDUE = "overdue"


loan_status_enum = SAEnum(
    LoanStatus,
    name="loan_status",
    native_enum=False,
    length=20,
    values_callable=lambda enum: [member.value for member in enum],
)


class Loan(Base, TimestampMixin):
    """A copy lent to a member."""

    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    copy_id: Mapped[int] = mapped_column(
        ForeignKey("book_copies.id", ondelete="RESTRICT"), index=True
    )
    member_id: Mapped[int] = mapped_column(
        ForeignKey("members.id", ondelete="RESTRICT"), index=True
    )
    loaned_by_id: Mapped[int | None] = mapped_column(ForeignKey("members.id", ondelete="SET NULL"))
    loan_date: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date] = mapped_column(Date, index=True)
    returned_at: Mapped[date | None] = mapped_column(Date)
    status: Mapped[LoanStatus] = mapped_column(
        loan_status_enum, default=LoanStatus.ACTIVE, index=True
    )
    renewals: Mapped[int] = mapped_column(Integer, default=0)

    copy: Mapped["BookCopy"] = relationship(back_populates="loans")
    member: Mapped["Member"] = relationship(
        back_populates="loans",
        foreign_keys=[member_id],
    )
    loaned_by: Mapped["Member | None"] = relationship(foreign_keys=[loaned_by_id])
    fine: Mapped["Fine | None"] = relationship(back_populates="loan", uselist=False)

    @property
    def book(self) -> "Book | None":
        """Convenience accessor for the borrowed title."""
        return self.copy.book if self.copy is not None else None
