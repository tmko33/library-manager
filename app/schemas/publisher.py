"""Publisher schemas."""

from pydantic import Field

from app.schemas.common import ORMBase


class PublisherBase(ORMBase):
    name: str = Field(min_length=2, max_length=150, examples=["Penguin Random House"])
    website: str | None = Field(default=None, max_length=500)


class PublisherCreate(PublisherBase):
    pass


class PublisherUpdate(ORMBase):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    website: str | None = Field(default=None, max_length=500)


class PublisherBrief(ORMBase):
    id: int
    name: str


class PublisherRead(PublisherBase):
    id: int
