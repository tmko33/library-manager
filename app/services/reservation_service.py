"""Reservation service."""

from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    BookNotFoundError,
    BusinessRuleError,
    ConflictError,
    InactiveMemberError,
    MemberNotFoundError,
    ReservationLimitReachedError,
    ReservationNotFoundError,
)
from app.models.reservation import Reservation, ReservationStatus
from app.repositories.book_repository import BookRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.reservation_repository import ReservationRepository
from app.services.base import BaseService

MAX_PENDING_RESERVATIONS = 3


class ReservationService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.reservations = ReservationRepository(session)
        self.books = BookRepository(session)
        self.members = MemberRepository(session)

    async def list_reservations(
        self,
        *,
        offset: int,
        limit: int,
        member_id: int | None = None,
        book_id: int | None = None,
        status: ReservationStatus | None = None,
    ) -> tuple[list[Reservation], int]:
        return await self.reservations.list_paginated(
            offset=offset,
            limit=limit,
            member_id=member_id,
            book_id=book_id,
            status=status,
        )

    async def get_reservation(self, reservation_id: int) -> Reservation:
        reservation = await self.reservations.get_detailed(reservation_id)
        if reservation is None:
            raise ReservationNotFoundError(f"Reservation {reservation_id} does not exist.")
        return reservation

    async def create_reservation(self, *, member_id: int, book_id: int) -> Reservation:
        today = date.today()
        member = await self.members.get(member_id)
        if member is None:
            raise MemberNotFoundError(f"Member {member_id} does not exist.")
        if not member.is_active or (
            member.membership_expires_at is not None and member.membership_expires_at < today
        ):
            raise InactiveMemberError("This membership is not active.")

        book = await self.books.get_detailed(book_id)
        if book is None:
            raise BookNotFoundError(f"Book {book_id} does not exist.")

        if await self.reservations.get_pending_for_member(member_id, book_id):
            raise ConflictError("You already have a pending reservation for this book.")
        if await self.reservations.count_pending_for_member(member_id) >= (
            MAX_PENDING_RESERVATIONS
        ):
            raise ReservationLimitReachedError(
                f"A member cannot hold more than {MAX_PENDING_RESERVATIONS} reservations."
            )
        if book.available_copies > 0:
            raise BusinessRuleError(
                "Copies are available right now, borrow the book instead of reserving it.",
                code="book_available",
                status_code=409,
            )

        reservation = Reservation(
            book_id=book_id,
            member_id=member_id,
            status=ReservationStatus.PENDING,
        )
        await self.reservations.add(reservation)
        await self.commit()
        return await self.get_reservation(reservation.id)

    async def cancel_reservation(self, reservation_id: int) -> Reservation:
        reservation = await self.get_reservation(reservation_id)
        if reservation.status != ReservationStatus.PENDING:
            raise BusinessRuleError(
                "Only pending reservations can be cancelled.",
                code="reservation_not_pending",
                status_code=409,
            )
        reservation.status = ReservationStatus.CANCELLED
        await self.commit()
        return await self.get_reservation(reservation_id)

    async def expire_stale(self, today: date | None = None) -> int:
        """Mark expired holds and return how many were released."""
        reference = today or date.today()
        expired = await self.reservations.get_expired_pending(reference)
        for reservation in expired:
            reservation.status = ReservationStatus.EXPIRED
        if expired:
            await self.commit()
        return len(expired)

    @staticmethod
    def hold_window_start(today: date | None = None) -> date:
        reference = today or date.today()
        return reference + timedelta(days=settings.reservation_hold_days)
