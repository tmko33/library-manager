"""Book copy repository."""

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.models.book_copy import BookCopy, CopyStatus
from app.models.loan import Loan, LoanStatus
from app.repositories.base import BaseRepository


class CopyRepository(BaseRepository[BookCopy]):
    model = BookCopy

    async def get_detailed(self, copy_id: int) -> BookCopy | None:
        statement = (
            select(BookCopy)
            .options(joinedload(BookCopy.book), joinedload(BookCopy.branch))
            .where(BookCopy.id == copy_id)
        )
        return await self.session.scalar(statement)

    async def get_by_inventory_code(self, inventory_code: str) -> BookCopy | None:
        return await self.session.scalar(
            select(BookCopy).where(BookCopy.inventory_code == inventory_code)
        )

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
        book_id: int | None = None,
        branch_id: int | None = None,
        status: CopyStatus | None = None,
    ) -> tuple[list[BookCopy], int]:
        statement = select(BookCopy).options(joinedload(BookCopy.book), joinedload(BookCopy.branch))
        count_statement = select(func.count()).select_from(BookCopy)

        conditions = []
        if book_id is not None:
            conditions.append(BookCopy.book_id == book_id)
        if branch_id is not None:
            conditions.append(BookCopy.branch_id == branch_id)
        if status is not None:
            conditions.append(BookCopy.status == status)
        if conditions:
            statement = statement.where(*conditions)
            count_statement = count_statement.where(*conditions)

        total = int(await self.session.scalar(count_statement) or 0)
        statement = statement.order_by(BookCopy.inventory_code).offset(offset).limit(limit)
        result = await self.session.scalars(statement)
        return list(result.unique().all()), total

    async def get_available_copy(
        self, book_id: int, branch_id: int | None = None
    ) -> BookCopy | None:
        """Lock and return a lendable copy, skipping rows locked by other transactions."""
        statement = (
            select(BookCopy)
            .where(
                BookCopy.book_id == book_id,
                BookCopy.status == CopyStatus.AVAILABLE,
            )
            .order_by(BookCopy.id)
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        if branch_id is not None:
            statement = statement.where(BookCopy.branch_id == branch_id)
        return await self.session.scalar(statement)

    async def count_by_branch(self, branch_id: int) -> int:
        statement = (
            select(func.count()).select_from(BookCopy).where(BookCopy.branch_id == branch_id)
        )
        return int(await self.session.scalar(statement) or 0)

    async def has_active_loan(self, copy_id: int) -> bool:
        statement = (
            select(func.count())
            .select_from(Loan)
            .where(
                Loan.copy_id == copy_id,
                Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE]),
            )
        )
        return bool(await self.session.scalar(statement))

    async def exists_inventory_code(self, inventory_code: str) -> bool:
        return (await self.get_by_inventory_code(inventory_code)) is not None
