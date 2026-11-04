"""Shared schema helpers."""

from pydantic import BaseModel, ConfigDict, Field

from app.core.pagination import Page, PageParams

__all__ = ["Message", "ORMBase", "Page", "PageParams"]


class ORMBase(BaseModel):
    """Base schema that can be built from ORM instances."""

    model_config = ConfigDict(from_attributes=True)


class Message(BaseModel):
    """Simple message payload."""

    message: str = Field(examples=["Operation completed successfully."])
