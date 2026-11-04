"""Loan endpoints."""

from fastapi import APIRouter, status

from app.api.deps import CurrentMember, PageDep, SessionDep, StaffMember, is_staff
from app.core.exceptions import ForbiddenError
from app.core.pagination import Page
from app.models.loan import LoanStatus
from app.schemas.loan import LoanCreate, LoanRead
from app.services.loan_service import LoanService

router = APIRouter(prefix="/loans", tags=["loans"])


@router.get("", response_model=Page[LoanRead], summary="List loans")
async def list_loans(
    session: SessionDep,
    params: PageDep,
    current: CurrentMember,
    member_id: int | None = None,
    status_filter: LoanStatus | None = None,
    overdue: bool | None = None,
) -> Page[LoanRead]:
    target_member = member_id
    if not is_staff(current):
        target_member = current.id

    loans, total = await LoanService(session).list_loans(
        offset=params.offset,
        limit=params.limit,
        member_id=target_member,
        status=status_filter,
        overdue=overdue,
    )
    return Page.from_orm_items(loans, total, params, LoanRead)


@router.post(
    "",
    response_model=LoanRead,
    status_code=status.HTTP_201_CREATED,
    summary="Borrow a book",
)
async def borrow_book(data: LoanCreate, session: SessionDep, current: CurrentMember) -> LoanRead:
    target_member = data.member_id or current.id
    if data.member_id is not None and data.member_id != current.id and not is_staff(current):
        raise ForbiddenError("You cannot borrow books on behalf of another member.")

    loan = await LoanService(session).borrow(
        member_id=target_member,
        book_id=data.book_id,
        loaned_by_id=current.id,
    )
    return LoanRead.model_validate(loan)


@router.post(
    "/overdue/refresh",
    summary="Flag overdue loans (staff only)",
    status_code=status.HTTP_200_OK,
)
async def refresh_overdue(session: SessionDep, _: StaffMember) -> dict[str, int]:
    updated = await LoanService(session).refresh_overdue()
    return {"updated": updated}


@router.get("/{loan_id}", response_model=LoanRead, summary="Get a loan")
async def get_loan(loan_id: int, session: SessionDep, current: CurrentMember) -> LoanRead:
    loan = await LoanService(session).get_loan(loan_id)
    if not is_staff(current) and loan.member_id != current.id:
        raise ForbiddenError("You can only read your own loans.")
    return LoanRead.model_validate(loan)


@router.post("/{loan_id}/return", response_model=LoanRead, summary="Return a borrowed book")
async def return_loan(loan_id: int, session: SessionDep, current: CurrentMember) -> LoanRead:
    service = LoanService(session)
    loan = await service.get_loan(loan_id)
    if not is_staff(current) and loan.member_id != current.id:
        raise ForbiddenError("You can only return your own loans.")
    updated = await service.return_loan(loan_id, returned_by_id=current.id)
    return LoanRead.model_validate(updated)


@router.post("/{loan_id}/renew", response_model=LoanRead, summary="Renew a loan")
async def renew_loan(loan_id: int, session: SessionDep, current: CurrentMember) -> LoanRead:
    service = LoanService(session)
    loan = await service.get_loan(loan_id)
    if not is_staff(current) and loan.member_id != current.id:
        raise ForbiddenError("You can only renew your own loans.")
    updated = await service.renew_loan(loan_id)
    return LoanRead.model_validate(updated)
