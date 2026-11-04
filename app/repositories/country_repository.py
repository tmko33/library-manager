"""Country repository."""

from sqlalchemy import func, select

from app.models.country import Country
from app.repositories.base import BaseRepository


class CountryRepository(BaseRepository[Country]):
    model = Country

    async def get_by_name(self, name: str) -> Country | None:
        return await self.session.scalar(select(Country).where(Country.name == name))

    async def list_paginated(
        self, *, offset: int, limit: int, q: str | None = None
    ) -> tuple[list[Country], int]:
        statement = select(Country)
        count_statement = select(func.count()).select_from(Country)
        if q:
            condition = Country.name.ilike(f"%{q}%")
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)

        total = int(await self.session.scalar(count_statement) or 0)
        statement = statement.order_by(Country.name).offset(offset).limit(limit)
        result = await self.session.scalars(statement)
        return list(result.all()), total
