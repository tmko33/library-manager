"""Author repository."""

from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import selectinload

from app.models.author import Author
from app.repositories.base import BaseRepository


class AuthorRepository(BaseRepository[Author]):
    model = Author

    @staticmethod
    def _with_relations(statement: Select[Any]) -> Select[Any]:
        return statement.options(selectinload(Author.country))

    async def get_detailed(self, author_id: int) -> Author | None:
        statement = self._with_relations(select(Author).where(Author.id == author_id))
        return await self.session.scalar(statement)

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
        q: str | None = None,
    ) -> tuple[list[Author], int]:
        statement = select(Author)
        count_statement = select(func.count()).select_from(Author)
        if q:
            pattern = f"%{q}%"
            condition = or_(Author.name.ilike(pattern))
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)

        total = int(await self.session.scalar(count_statement) or 0)
        statement = (
            self._with_relations(statement).order_by(Author.name).offset(offset).limit(limit)
        )
        result = await self.session.scalars(statement)
        return list(result.unique().all()), total

    async def get_many(self, author_ids: list[int]) -> list[Author]:
        if not author_ids:
            return []
        statement = select(Author).where(Author.id.in_(author_ids))
        result = await self.session.scalars(statement)
        return list(result.unique().all())
