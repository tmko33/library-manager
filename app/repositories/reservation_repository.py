"""Reservation repository."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.models.reservation import Reservation, ReservationStatus
from app.repositories.base import BaseRepository


class ReservationRepository(BaseRepository[Reservation]):
    model = Reservation

    async def get_detailed(self, reservation_id: int) -> Reservation | None:
        statement = (
            select(Reservation)
            .options(joinedload(Reservation.book), joinedload(Reservation.member))
            .where(Reservation.id == reservation_id)
        )
        return await self.session.scalar(statement)

    async def get_pending_for_book(self, book_id: int, *, lock: bool = False) -> list[Reservation]:
        """Return the waiting queue for a book, oldest first."""
        statement = (
            select(Reservation)
            .where(
                Reservation.book_id == book_id,
                Reservation.status == ReservationStatus.PENDING,
            )
            .order_by(Reservation.created_at, Reservation.id)
        )
        if lock:
            statement = statement.with_for_update()
        result = await self.session.scalars(statement)
        return list(result.all())

    async def get_pending_for_member(self, member_id: int, book_id: int) -> Reservation | None:
        statement = select(Reservation).where(
            Reservation.member_id == member_id,
            Reservation.book_id == book_id,
            Reservation.status == ReservationStatus.PENDING,
        )
        return await self.session.scalar(statement)

    async def count_pending_for_member(self, member_id: int) -> int:
        statement = (
            select(func.count())
            .select_from(Reservation)
            .where(
                Reservation.member_id == member_id,
                Reservation.status == ReservationStatus.PENDING,
            )
        )
        return int(await self.session.scalar(statement) or 0)

    async def get_expired_pending(self, today: date) -> list[Reservation]:
        statement = select(Reservation).where(
            Reservation.status == ReservationStatus.PENDING,
            Reservation.expires_at.is_not(None),
            Reservation.expires_at < today,
        )
        result = await self.session.scalars(statement)
        return list(result.all())

    async def list_paginated(
        self,
        *,
        offset: int,
        limit: int,
        member_id: int | None = None,
        book_id: int | None = None,
        status: ReservationStatus | None = None,
    ) -> tuple[list[Reservation], int]:
        statement = select(Reservation).options(
            joinedload(Reservation.book), joinedload(Reservation.member)
        )
        count_statement = select(func.count()).select_from(Reservation)

        conditions = []
        if member_id is not None:
            conditions.append(Reservation.member_id == member_id)
        if book_id is not None:
            conditions.append(Reservation.book_id == book_id)
        if status is not None:
            conditions.append(Reservation.status == status)
        if conditions:
            statement = statement.where(*conditions)
            count_statement = count_statement.where(*conditions)

        total = int(await self.session.scalar(count_statement) or 0)
        statement = statement.order_by(Reservation.id.desc()).offset(offset).limit(limit)
        result = await self.session.scalars(statement)
        return list(result.unique().all()), total
