"""Book schemas."""

from pydantic import Field

from app.schemas.author import AuthorBrief
from app.schemas.common import ORMBase
from app.schemas.publisher import PublisherBrief


class BookBase(ORMBase):
    isbn: str = Field(min_length=10, max_length=20, examples=["9780307474728"])
    title: str = Field(min_length=1, max_length=255, examples=["Cien años de soledad"])
    publication_year: int | None = Field(default=None, ge=1000, le=2100)
    summary: str | None = Field(default=None, max_length=5000)
    language: str = Field(default="es", min_length=2, max_length=10)
    pages: int | None = Field(default=None, ge=1)
    cover_url: str | None = Field(default=None, max_length=500)
    publisher_id: int | None = None


class BookCreate(BookBase):
    author_ids: list[int] = Field(default_factory=list)


class BookUpdate(ORMBase):
    isbn: str | None = Field(default=None, min_length=10, max_length=20)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    publication_year: int | None = Field(default=None, ge=1000, le=2100)
    summary: str | None = Field(default=None, max_length=5000)
    language: str | None = Field(default=None, min_length=2, max_length=10)
    pages: int | None = Field(default=None, ge=1)
    cover_url: str | None = Field(default=None, max_length=500)
    publisher_id: int | None = None
    author_ids: list[int] | None = None


class BookBrief(ORMBase):
    id: int
    isbn: str
    title: str


class BookRead(BookBase):
    id: int
    authors: list[AuthorBrief] = Field(default_factory=list)
    publisher: PublisherBrief | None = None
    total_copies: int = 0
    available_copies: int = 0
