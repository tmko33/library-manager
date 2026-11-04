"""Member repository."""

from sqlalchemy import func, or_, select

from app.models.member import Member
from app.repositories.base import BaseRepository


class MemberRepository(BaseRepository[Member]):
    model = Member

    async def get_by_email(self, email: str) -> Member | None:
        return await self.session.scalar(
            select(Member).where(func.lower(Member.email) == email.lower())
        )

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
        q: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[Member], int]:
        statement = select(Member)
        count_statement = select(func.count()).select_from(Member)

        if q:
            condition = or_(
                Member.full_name.ilike(f"%{q}%"),
                Member.email.ilike(f"%{q}%"),
            )
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)
        if is_active is not None:
            statement = statement.where(Member.is_active == is_active)
            count_statement = count_statement.where(Member.is_active == is_active)

        total = int(await self.session.scalar(count_statement) or 0)
        statement = statement.order_by(Member.full_name).offset(offset).limit(limit)
        result = await self.session.scalars(statement)
        return list(result.all()), total
