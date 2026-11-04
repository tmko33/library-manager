"""Publisher repository."""

from sqlalchemy import func, or_, select

from app.models.publisher import Publisher
from app.repositories.base import BaseRepository


class PublisherRepository(BaseRepository[Publisher]):
    model = Publisher

    async def get_by_name(self, name: str) -> Publisher | None:
        return await self.session.scalar(select(Publisher).where(Publisher.name == name))

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
        q: str | None = None,
    ) -> tuple[list[Publisher], int]:
        statement = select(Publisher)
        count_statement = select(func.count()).select_from(Publisher)
        if q:
            condition = or_(Publisher.name.ilike(f"%{q}%"))
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)

        total = int(await self.session.scalar(count_statement) or 0)
        statement = statement.order_by(Publisher.name).offset(offset).limit(limit)
        result = await self.session.scalars(statement)
        return list(result.all()), total
