"""Author entity."""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.associations import book_authors

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.country import Country


class Author(Base, TimestampMixin):
    """A person who wrote one or more books."""

    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    bio: Mapped[str | None] = mapped_column(Text)
    birth_year: Mapped[int | None]
    country_id: Mapped[int | None] = mapped_column(
        ForeignKey("countries.id", ondelete="SET NULL"), index=True
    )

    country: Mapped["Country | None"] = relationship(back_populates="authors")
    books: Mapped[list["Book"]] = relationship(
        secondary=book_authors,
        back_populates="authors",
    )
