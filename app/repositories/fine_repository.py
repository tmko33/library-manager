"""Fine repository."""

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.models.fine import Fine, FineStatus
from app.models.loan import Loan
from app.repositories.base import BaseRepository


class FineRepository(BaseRepository[Fine]):
    model = Fine

    async def get_by_loan(self, loan_id: int) -> Fine | None:
        return await self.session.scalar(select(Fine).where(Fine.loan_id == loan_id))

    async def get_detailed(self, fine_id: int) -> Fine | None:
        statement = select(Fine).options(joinedload(Fine.loan)).where(Fine.id == fine_id)
        return await self.session.scalar(statement)

    async def count_unpaid_for_member(self, member_id: int) -> int:
        statement = (
            select(func.count())
            .select_from(Fine)
            .join(Loan, Loan.id == Fine.loan_id)
            .where(
                Loan.member_id == member_id,
                Fine.status == FineStatus.PENDING,
            )
        )
        return int(await self.session.scalar(statement) or 0)

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
        member_id: int | None = None,
        status: FineStatus | None = None,
    ) -> tuple[list[Fine], int]:
        statement = select(Fine)
        count_statement = select(func.count()).select_from(Fine)

        conditions = []
        if member_id is not None:
            statement = statement.join(Loan, Loan.id == Fine.loan_id)
            count_statement = count_statement.join(Loan, Loan.id == Fine.loan_id)
            conditions.append(Loan.member_id == member_id)
        if status is not None:
            conditions.append(Fine.status == status)
        if conditions:
            statement = statement.where(*conditions)
            count_statement = count_statement.where(*conditions)

        total = int(await self.session.scalar(count_statement) or 0)
        statement = statement.order_by(Fine.id.desc()).offset(offset).limit(limit)
        result = await self.session.scalars(statement)
        return list(result.unique().all()), total
