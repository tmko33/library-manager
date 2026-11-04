"""Book repository."""

from typing import Any, Literal

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import selectinload

from app.models.author import Author
from app.models.book import Book
from app.models.book_copy import BookCopy, CopyStatus
from app.repositories.base import BaseRepository

SortField = Literal["title", "publication_year", "created_at"]


class BookRepository(BaseRepository[Book]):
    model = Book

    @staticmethod
    def _with_relations(statement: Select[Any]) -> Select[Any]:
        return statement.options(
            selectinload(Book.authors),
            selectinload(Book.publisher),
            selectinload(Book.copies),
        )

    @staticmethod
    def _apply_filters(
        statement: Select[Any],
        *,
        q: str | None = None,
        author_id: int | None = None,
        publisher_id: int | None = None,
        year: int | None = None,
        available: bool | None = None,
    ) -> Select[Any]:
        if q:
            pattern = f"%{q}%"
            statement = statement.where(or_(Book.title.ilike(pattern), Book.isbn.ilike(pattern)))
        if author_id is not None:
            statement = statement.where(Book.authors.any(Author.id == author_id))
        if publisher_id is not None:
            statement = statement.where(Book.publisher_id == publisher_id)
        if year is not None:
            statement = statement.where(Book.publication_year == year)
        if available is True:
            statement = statement.where(Book.copies.any(BookCopy.status == CopyStatus.AVAILABLE))
        elif available is False:
            statement = statement.where(~Book.copies.any(BookCopy.status == CopyStatus.AVAILABLE))
        return statement

    async def get_detailed(self, book_id: int) -> Book | None:
        statement = self._with_relations(select(Book).where(Book.id == book_id))
        return await self.session.scalar(statement)

    async def get_by_isbn(self, isbn: str) -> Book | None:
        statement = self._with_relations(select(Book).where(Book.isbn == isbn))
        return await self.session.scalar(statement)

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
        q: str | None = None,
        author_id: int | None = None,
        publisher_id: int | None = None,
        year: int | None = None,
        available: bool | None = None,
        sort: SortField = "title",
        order: Literal["asc", "desc"] = "asc",
    ) -> tuple[list[Book], int]:
        count_statement = self._apply_filters(
            select(func.count()).select_from(Book),
            q=q,
            author_id=author_id,
            publisher_id=publisher_id,
            year=year,
            available=available,
        )
        total = int(await self.session.scalar(count_statement) or 0)

        column = getattr(Book, sort)
        ordering = column.asc() if order == "asc" else column.desc()

        statement = self._apply_filters(
            select(Book),
            q=q,
            author_id=author_id,
            publisher_id=publisher_id,
            year=year,
            available=available,
        )
        statement = (
            self._with_relations(statement).order_by(ordering, Book.id).offset(offset).limit(limit)
        )

        result = await self.session.scalars(statement)
        return list(result.unique().all()), total
