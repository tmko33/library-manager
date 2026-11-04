"""Branch repository."""

from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from app.models.branch import Branch
from app.repositories.base import BaseRepository


class BranchRepository(BaseRepository[Branch]):
    model = Branch

    async def get_detailed(self, branch_id: int) -> Branch | None:
        statement = (
            select(Branch).options(selectinload(Branch.country)).where(Branch.id == branch_id)
        )
        return await self.session.scalar(statement)

    async def get_by_name(self, name: str) -> Branch | None:
        return await self.session.scalar(select(Branch).where(Branch.name == name))

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
        q: str | None = None,
        city: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[Branch], int]:
        statement = select(Branch).options(selectinload(Branch.country))
        count_statement = select(func.count()).select_from(Branch)

        if q:
            condition = or_(Branch.name.ilike(f"%{q}%"), Branch.city.ilike(f"%{q}%"))
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)
        if city:
            statement = statement.where(Branch.city == city)
            count_statement = count_statement.where(Branch.city == city)
        if is_active is not None:
            statement = statement.where(Branch.is_active == is_active)
            count_statement = count_statement.where(Branch.is_active == is_active)

        total = int(await self.session.scalar(count_statement) or 0)
        statement = statement.order_by(Branch.name).offset(offset).limit(limit)
        result = await self.session.scalars(statement)
        return list(result.unique().all()), total
