"""Branch schemas."""

from pydantic import Field

from app.schemas.common import ORMBase
from app.schemas.country import CountryRead


class BranchBase(ORMBase):
    name: str = Field(min_length=2, max_length=150, examples=["Biblioteca Central"])
    address: str = Field(min_length=2, max_length=255, examples=["Calle 10 # 5-20"])
    city: str = Field(min_length=2, max_length=100, examples=["Bogotá"])
    country_id: int | None = None
    is_active: bool = True


class BranchCreate(BranchBase):
    pass


class BranchUpdate(ORMBase):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    address: str | None = Field(default=None, min_length=2, max_length=255)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    country_id: int | None = None
    is_active: bool | None = None


class BranchBrief(ORMBase):
    id: int
    name: str
    city: str


class BranchRead(BranchBase):
    id: int
    country: CountryRead | None = None
