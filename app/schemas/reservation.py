"""Reservation schemas."""

from datetime import date, datetime

from pydantic import Field

from app.models.reservation import ReservationStatus
from app.schemas.book import BookBrief
from app.schemas.common import ORMBase
from app.schemas.member import MemberBrief


class ReservationCreate(ORMBase):
    book_id: int
    member_id: int | None = Field(
        default=None,
        description="Only librarians may reserve on behalf of another member.",
    )


class ReservationRead(ORMBase):
    id: int
    book_id: int
    member_id: int
    book: BookBrief | None = None
    member: MemberBrief | None = None
    status: ReservationStatus
    expires_at: date | None = None
    created_at: datetime
