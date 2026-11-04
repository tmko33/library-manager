"""Reusable pagination primitives."""

import math
from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T", bound=BaseModel)


class PageParams(BaseModel):
    """Pagination query parameters."""

    page: int = Field(default=1, ge=1, description="Page number, starting at 1")
    size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        return self.size


def pagination_params(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
) -> PageParams:
    """FastAPI dependency that parses pagination query parameters."""
    return PageParams(page=page, size=size)


class Page(BaseModel, Generic[T]):
    """A paginated collection of items."""

    model_config = ConfigDict(from_attributes=True)

    items: list[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(cls, items: list[T], total: int, params: PageParams) -> "Page[T]":
        pages = math.ceil(total / params.size) if total else 0
        return cls(
            items=items,
            total=total,
            page=params.page,
            size=params.size,
            pages=pages,
        )

    @classmethod
    def from_orm_items(
        cls,
        items: Sequence[Any],
        total: int,
        params: PageParams,
        schema: type[T],
    ) -> "Page[T]":
        """Build a page by validating ORM instances into ``schema``."""
        pages = math.ceil(total / params.size) if total else 0
        return cls(
            items=[schema.model_validate(item) for item in items],
            total=total,
            page=params.page,
            size=params.size,
            pages=pages,
        )
