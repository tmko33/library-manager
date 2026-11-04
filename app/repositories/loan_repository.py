"""Loan repository."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.models.book_copy import BookCopy
from app.models.loan import Loan, LoanStatus
from app.repositories.base import BaseRepository


class LoanRepository(BaseRepository[Loan]):
    model = Loan

    async def get_detailed(self, loan_id: int) -> Loan | None:
        statement = (
            select(Loan)
            .options(
                joinedload(Loan.copy).joinedload(BookCopy.book),
                joinedload(Loan.member),
            )
            .where(Loan.id == loan_id)
        )
        return await self.session.scalar(statement)

    async def count_active_for_member(self, member_id: int) -> int:
        statement = (
            select(func.count())
            .select_from(Loan)
            .where(
                Loan.member_id == member_id,
                Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE]),
            )
        )
        return int(await self.session.scalar(statement) or 0)

    async def has_overdue_for_member(self, member_id: int, today: date) -> bool:
        statement = (
            select(func.count())
            .select_from(Loan)
            .where(
                Loan.member_id == member_id,
                Loan.status == LoanStatus.ACTIVE,
                Loan.due_date < today,
            )
        )
        return bool(await self.session.scalar(statement))

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
        member_id: int | None = None,
        status: LoanStatus | None = None,
        overdue: bool | None = None,
        today: date | None = None,
    ) -> tuple[list[Loan], int]:
        statement = select(Loan).options(
            joinedload(Loan.copy).joinedload(BookCopy.book),
            joinedload(Loan.member),
        )
        count_statement = select(func.count()).select_from(Loan)

        conditions = []
        if member_id is not None:
            conditions.append(Loan.member_id == member_id)
        if status is not None:
            conditions.append(Loan.status == status)
        if overdue is True and today is not None:
            conditions.append(Loan.due_date < today)
            conditions.append(Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE]))
        if conditions:
            statement = statement.where(*conditions)
            count_statement = count_statement.where(*conditions)

        total = int(await self.session.scalar(count_statement) or 0)
        statement = statement.order_by(Loan.id.desc()).offset(offset).limit(limit)
        result = await self.session.scalars(statement)
        return list(result.unique().all()), total

    async def get_active_for_copy(self, copy_id: int) -> Loan | None:
        statement = (
            select(Loan)
            .where(
                Loan.copy_id == copy_id,
                Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE]),
            )
            .order_by(Loan.id.desc())
            .limit(1)
        )
        return await self.session.scalar(statement)

    async def get_overdue_active(self, today: date) -> list[Loan]:
        """Active loans whose due date has already passed."""
        statement = (
            select(Loan)
            .options(joinedload(Loan.copy).joinedload(BookCopy.book), joinedload(Loan.member))
            .where(Loan.status == LoanStatus.ACTIVE, Loan.due_date < today)
        )
        result = await self.session.scalars(statement)
        return list(result.unique().all())
