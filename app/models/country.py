"""Country entity."""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.author import Author


class Country(Base, TimestampMixin):
    """A country of origin, used for authors and branches."""

    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    iso_code: Mapped[str | None] = mapped_column(String(2), unique=True)

    authors: Mapped[list["Author"]] = relationship(back_populates="country")
