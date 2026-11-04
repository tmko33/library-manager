"""Loan service: the core lending workflow."""

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    BookNotFoundError,
    BusinessRuleError,
    HasOverdueLoansError,
    HasUnpaidFinesError,
    InactiveMemberError,
    LoanAlreadyReturnedError,
    LoanLimitReachedError,
    LoanNotFoundError,
    MemberNotFoundError,
    NoCopiesAvailableError,
    RenewalLimitReachedError,
)
from app.models.book_copy import CopyStatus
from app.models.fine import Fine, FineStatus
from app.models.loan import Loan, LoanStatus
from app.models.reservation import ReservationStatus
from app.repositories.book_repository import BookRepository
from app.repositories.copy_repository import CopyRepository
from app.repositories.fine_repository import FineRepository
from app.repositories.loan_repository import LoanRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.reservation_repository import ReservationRepository
from app.services.base import BaseService

MAX_RENEWALS = 2


class LoanService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.loans = LoanRepository(session)
        self.copies = CopyRepository(session)
        self.books = BookRepository(session)
        self.members = MemberRepository(session)
        self.fines = FineRepository(session)
        self.reservations = ReservationRepository(session)

    # ------------------------------------------------------------------ #
    # Queries
    # ------------------------------------------------------------------ #
    async def list_loans(
        self,
        *,
        offset: int,
        limit: int,
        member_id: int | None = None,
        status: LoanStatus | None = None,
        overdue: bool | None = None,
    ) -> tuple[list[Loan], int]:
        return await self.loans.list_paginated(
            offset=offset,
            limit=limit,
            member_id=member_id,
            status=status,
            overdue=overdue,
            today=date.today(),
        )

    async def get_loan(self, loan_id: int) -> Loan:
        loan = await self.loans.get_detailed(loan_id)
        if loan is None:
            raise LoanNotFoundError(f"Loan {loan_id} does not exist.")
        return loan

    # ------------------------------------------------------------------ #
    # Commands
    # ------------------------------------------------------------------ #
    async def borrow(
        self, *, member_id: int, book_id: int, loaned_by_id: int | None = None
    ) -> Loan:
        today = date.today()
        member = await self.members.get(member_id)
        if member is None:
            raise MemberNotFoundError(f"Member {member_id} does not exist.")
        self._ensure_membership_active(member, today)

        if await self.loans.has_overdue_for_member(member_id, today):
            raise HasOverdueLoansError("The member has overdue loans and cannot borrow new books.")
        if await self.fines.count_unpaid_for_member(member_id):
            raise HasUnpaidFinesError("The member has unpaid fines and cannot borrow new books.")
        active_loans = await self.loans.count_active_for_member(member_id)
        if active_loans >= settings.max_active_loans:
            raise LoanLimitReachedError(
                f"The member already has {settings.max_active_loans} active loans."
            )

        book = await self.books.get_detailed(book_id)
        if book is None:
            raise BookNotFoundError(f"Book {book_id} does not exist.")

        await self._release_expired_holds(today)

        queue = await self.reservations.get_pending_for_book(book_id, lock=True)
        if queue and queue[0].member_id != member_id:
            raise BusinessRuleError(
                "This title is reserved for another member in the waiting queue.",
                code="book_reserved",
                status_code=409,
            )

        copy = await self.copies.get_available_copy(book_id)
        if copy is None:
            raise NoCopiesAvailableError(f"There are no available copies of '{book.title}'.")

        loan = Loan(
            copy_id=copy.id,
            member_id=member_id,
            loaned_by_id=loaned_by_id,
            loan_date=today,
            due_date=today + timedelta(days=settings.loan_period_days),
            status=LoanStatus.ACTIVE,
        )
        self.session.add(loan)

        copy.status = CopyStatus.ON_LOAN

        if queue and queue[0].member_id == member_id:
            queue[0].status = ReservationStatus.FULFILLED

        await self.commit()
        return await self.get_loan(loan.id)

    async def return_loan(self, loan_id: int, *, returned_by_id: int | None = None) -> Loan:
        today = date.today()
        loan = await self.get_loan(loan_id)

        if loan.status == LoanStatus.RETURNED or loan.returned_at is not None:
            raise LoanAlreadyReturnedError(f"Loan {loan_id} has already been returned.")

        late_days = max(0, (today - loan.due_date).days)
        loan.returned_at = today
        loan.status = LoanStatus.RETURNED
        loan.copy.status = CopyStatus.AVAILABLE

        if late_days > 0:
            await self._register_fine(loan, late_days)

        await self._hold_copy_for_next_reservation(loan, today)
        await self.commit()
        return await self.get_loan(loan_id)

    async def renew_loan(self, loan_id: int) -> Loan:
        today = date.today()
        loan = await self.get_loan(loan_id)

        if loan.status == LoanStatus.RETURNED:
            raise LoanAlreadyReturnedError(f"Loan {loan_id} has already been returned.")
        if loan.renewals >= MAX_RENEWALS:
            raise RenewalLimitReachedError(f"A loan can only be renewed {MAX_RENEWALS} times.")
        if loan.due_date < today:
            raise HasOverdueLoansError("Overdue loans cannot be renewed; return the book first.")

        queue = await self.reservations.get_pending_for_book(loan.copy.book_id)
        if any(reservation.member_id != loan.member_id for reservation in queue):
            raise BusinessRuleError(
                "The title is reserved by another member and cannot be renewed.",
                code="book_reserved",
                status_code=409,
            )

        loan.due_date = today + timedelta(days=settings.loan_period_days)
        loan.renewals += 1
        await self.commit()
        return await self.get_loan(loan_id)

    async def refresh_overdue(self) -> int:
        """Flag active loans whose due date has passed."""
        today = date.today()
        overdue = await self.loans.get_overdue_active(today)
        for loan in overdue:
            loan.status = LoanStatus.OVERDUE
        if overdue:
            await self.commit()
        return len(overdue)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _ensure_membership_active(member: object, today: date) -> None:
        if not getattr(member, "is_active", False):
            raise InactiveMemberError("This account has been deactivated.")
        expires_at = getattr(member, "membership_expires_at", None)
        if expires_at is not None and expires_at < today:
            raise InactiveMemberError("This membership has expired.")

    async def _release_expired_holds(self, today: date) -> None:
        expired = await self.reservations.get_expired_pending(today)
        for reservation in expired:
            reservation.status = ReservationStatus.EXPIRED

    async def _register_fine(self, loan: Loan, late_days: int) -> None:
        if await self.fines.get_by_loan(loan.id) is not None:
            return
        amount = (Decimal(late_days) * Decimal(str(settings.fine_per_day))).quantize(
            Decimal("0.01")
        )
        self.session.add(
            Fine(
                loan_id=loan.id,
                amount=amount,
                reason=f"{late_days} day(s) overdue",
                status=FineStatus.PENDING,
            )
        )

    async def _hold_copy_for_next_reservation(self, loan: Loan, today: date) -> None:
        queue = await self.reservations.get_pending_for_book(loan.copy.book_id)
        if queue and queue[0].expires_at is None:
            queue[0].expires_at = today + timedelta(days=settings.reservation_hold_days)
