"""Book copy service."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BookNotFoundError,
    BranchNotFoundError,
    BusinessRuleError,
    CopyNotFoundError,
    DuplicateInventoryCodeError,
)
from app.models.book_copy import BookCopy, CopyStatus
from app.repositories.book_repository import BookRepository
from app.repositories.branch_repository import BranchRepository
from app.repositories.copy_repository import CopyRepository
from app.schemas.copy import CopyCreate, CopyUpdate
from app.services.base import BaseService


class CopyService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.copies = CopyRepository(session)
        self.books = BookRepository(session)
        self.branches = BranchRepository(session)

    async def list_copies(
        self,
        *,
        offset: int,
        limit: int,
        book_id: int | None = None,
        branch_id: int | None = None,
        status: CopyStatus | None = None,
    ) -> tuple[list[BookCopy], int]:
        return await self.copies.list_paginated(
            offset=offset,
            limit=limit,
            book_id=book_id,
            branch_id=branch_id,
            status=status,
        )

    async def get_copy(self, copy_id: int) -> BookCopy:
        copy = await self.copies.get_detailed(copy_id)
        if copy is None:
            raise CopyNotFoundError(f"Copy {copy_id} does not exist.")
        return copy

    async def create_copy(self, data: CopyCreate) -> BookCopy:
        if await self.books.get(data.book_id) is None:
            raise BookNotFoundError(f"Book {data.book_id} does not exist.")
        if await self.branches.get(data.branch_id) is None:
            raise BranchNotFoundError(f"Branch {data.branch_id} does not exist.")
        if await self.copies.get_by_inventory_code(data.inventory_code):
            raise DuplicateInventoryCodeError(
                f"Inventory code {data.inventory_code} is already in use."
            )

        copy = BookCopy(**data.model_dump())
        await self.copies.add(copy)
        await self.commit()
        return await self.get_copy(copy.id)

    async def update_copy(self, copy_id: int, data: CopyUpdate) -> BookCopy:
        copy = await self.get_copy(copy_id)
        changes = data.model_dump(exclude_unset=True)

        new_status = changes.get("status")
        if new_status == CopyStatus.AVAILABLE and await self.copies.has_active_loan(copy_id):
            raise BusinessRuleError(
                "The copy cannot be marked as available while it is on loan.",
                code="copy_on_loan",
                status_code=409,
            )
        if (
            "branch_id" in changes
            and changes["branch_id"] is not None
            and await self.branches.get(changes["branch_id"]) is None
        ):
            raise BranchNotFoundError(f"Branch {changes['branch_id']} does not exist.")

        for field, value in changes.items():
            setattr(copy, field, value)
        await self.commit()
        return await self.get_copy(copy_id)

    async def delete_copy(self, copy_id: int) -> None:
        copy = await self.get_copy(copy_id)
        if await self.copies.has_active_loan(copy_id):
            raise BusinessRuleError(
                "Cannot delete a copy that is currently on loan.",
                code="copy_on_loan",
                status_code=409,
            )
        await self.copies.delete(copy)
        await self.commit()
