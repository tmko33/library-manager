"""Publisher entity."""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.book import Book


class Publisher(Base, TimestampMixin):
    """A company that publishes books."""

    __tablename__ = "publishers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    website: Mapped[str | None] = mapped_column(String(500))

    books: Mapped[list["Book"]] = relationship(back_populates="publisher")
