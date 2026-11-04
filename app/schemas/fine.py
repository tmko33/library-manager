"""Fine schemas."""

from datetime import date, datetime
from decimal import Decimal

from app.models.fine import FineStatus
from app.schemas.common import ORMBase


class FineRead(ORMBase):
    id: int
    loan_id: int
    amount: Decimal
    reason: str
    status: FineStatus
    paid_at: date | None = None
    created_at: datetime
