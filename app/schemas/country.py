"""Country schemas."""

from pydantic import Field

from app.schemas.common import ORMBase


class CountryBase(ORMBase):
    name: str = Field(min_length=2, max_length=100, examples=["Colombia"])
    iso_code: str | None = Field(default=None, min_length=2, max_length=2, examples=["CO"])


class CountryCreate(CountryBase):
    pass


class CountryUpdate(ORMBase):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    iso_code: str | None = Field(default=None, min_length=2, max_length=2)


class CountryRead(CountryBase):
    id: int
