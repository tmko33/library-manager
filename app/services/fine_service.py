"""Fine service."""

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleError, FineNotFoundError
from app.models.fine import Fine, FineStatus
from app.repositories.fine_repository import FineRepository
from app.services.base import BaseService


class FineService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.fines = FineRepository(session)

    async def list_fines(
        self,
        *,
        offset: int,
        limit: int,
        member_id: int | None = None,
        status: FineStatus | None = None,
    ) -> tuple[list[Fine], int]:
        return await self.fines.list_paginated(
            offset=offset, limit=limit, member_id=member_id, status=status
        )

    async def get_fine(self, fine_id: int) -> Fine:
        fine = await self.fines.get_detailed(fine_id)
        if fine is None:
            raise FineNotFoundError(f"Fine {fine_id} does not exist.")
        return fine

    async def pay_fine(self, fine_id: int) -> Fine:
        fine = await self.get_fine(fine_id)
        if fine.status != FineStatus.PENDING:
            raise BusinessRuleError(
                "Only pending fines can be paid.",
                code="fine_not_pending",
                status_code=409,
            )
        fine.status = FineStatus.PAID
        fine.paid_at = date.today()
        await self.commit()
        return fine

    async def waive_fine(self, fine_id: int) -> Fine:
        fine = await self.get_fine(fine_id)
        if fine.status != FineStatus.PENDING:
            raise BusinessRuleError(
                "Only pending fines can be waived.",
                code="fine_not_pending",
                status_code=409,
            )
        fine.status = FineStatus.WAIVED
        await self.commit()
        return fine
