"""Author schemas."""

from pydantic import Field

from app.schemas.common import ORMBase
from app.schemas.country import CountryRead


class AuthorBase(ORMBase):
    name: str = Field(min_length=2, max_length=150, examples=["Gabriel García Márquez"])
    bio: str | None = Field(default=None, max_length=5000)
    birth_year: int | None = Field(default=None, ge=1000, le=2100)
    country_id: int | None = None


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(ORMBase):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    bio: str | None = Field(default=None, max_length=5000)
    birth_year: int | None = Field(default=None, ge=1000, le=2100)
    country_id: int | None = None


class AuthorBrief(ORMBase):
    id: int
    name: str


class AuthorRead(AuthorBase):
    id: int
    country: CountryRead | None = None
