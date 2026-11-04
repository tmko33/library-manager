"""Loan schemas."""

from datetime import date, datetime

from pydantic import Field

from app.models.loan import LoanStatus
from app.schemas.book import BookBrief
from app.schemas.common import ORMBase
from app.schemas.member import MemberBrief


class LoanCreate(ORMBase):
    book_id: int
    member_id: int | None = Field(
        default=None,
        description="Only librarians may lend on behalf of another member.",
    )


class LoanRead(ORMBase):
    id: int
    copy_id: int
    member_id: int
    loaned_by_id: int | None = None
    book: BookBrief | None = None
    member: MemberBrief | None = None
    loan_date: date
    due_date: date
    returned_at: date | None = None
    status: LoanStatus
    renewals: int
    created_at: datetime
