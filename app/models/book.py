"""Book entity (the bibliographic record, not the physical copies)."""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.associations import book_authors
from app.models.book_copy import CopyStatus

if TYPE_CHECKING:
    from app.models.author import Author
    from app.models.book_copy import BookCopy
    from app.models.publisher import Publisher
    from app.models.reservation import Reservation


class Book(Base, TimestampMixin):
    """A title held by the library system.

    A ``Book`` describes the work itself. The physical items that can be lent
    are :class:`~app.models.book_copy.BookCopy` instances.
    """

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    isbn: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    publication_year: Mapped[int | None]
    summary: Mapped[str | None] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(10), default="es")
    pages: Mapped[int | None]
    cover_url: Mapped[str | None] = mapped_column(String(500))
    publisher_id: Mapped[int | None] = mapped_column(
        ForeignKey("publishers.id", ondelete="SET NULL"), index=True
    )

    publisher: Mapped["Publisher | None"] = relationship(back_populates="books")
    authors: Mapped[list["Author"]] = relationship(
        secondary=book_authors,
        back_populates="books",
    )
    copies: Mapped[list["BookCopy"]] = relationship(
        back_populates="book",
        cascade="all, delete-orphan",
    )
    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="book",
        cascade="all, delete-orphan",
    )

    @property
    def total_copies(self) -> int:
        """Number of physical copies registered for this title."""
        return len(self.copies)

    @property
    def available_copies(self) -> int:
        """Number of copies that can currently be lent."""
        return sum(1 for copy in self.copies if copy.status == CopyStatus.AVAILABLE)
