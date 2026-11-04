"""Book copy schemas."""

from datetime import date

from pydantic import Field

from app.models.book_copy import CopyStatus
from app.schemas.book import BookBrief
from app.schemas.branch import BranchBrief
from app.schemas.common import ORMBase


class CopyCreate(ORMBase):
    book_id: int
    branch_id: int
    inventory_code: str = Field(min_length=1, max_length=40, examples=["BC-0001"])
    acquired_at: date | None = None
    notes: str | None = Field(default=None, max_length=1000)


class CopyUpdate(ORMBase):
    branch_id: int | None = None
    status: CopyStatus | None = None
    notes: str | None = Field(default=None, max_length=1000)


class CopyRead(ORMBase):
    id: int
    inventory_code: str
    book_id: int
    branch_id: int
    status: CopyStatus
    acquired_at: date | None = None
    notes: str | None = None


class CopyReadDetailed(CopyRead):
    book: BookBrief
    branch: BranchBrief
