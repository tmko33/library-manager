"""Scheduled maintenance: overdue loans and expired reservations."""

import asyncio
import logging

from app.db.session import AsyncSessionLocal
from app.services.loan_service import LoanService
from app.services.reservation_service import ReservationService

logger = logging.getLogger("app.maintenance")


async def run_maintenance() -> tuple[int, int]:
    """Flag overdue loans and expire stale holds. Returns (loans, holds)."""
    async with AsyncSessionLocal() as session:
        overdue = await LoanService(session).refresh_overdue()
        expired = await ReservationService(session).expire_stale()
    logger.info("maintenance: %d overdue loans, %d expired holds", overdue, expired)
    return overdue, expired


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    overdue, expired = asyncio.run(run_maintenance())
    print(f"Overdue loans flagged: {overdue}")
    print(f"Expired reservations: {expired}")


if __name__ == "__main__":
    main()
