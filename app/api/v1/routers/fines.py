"""Fine endpoints."""

from fastapi import APIRouter

from app.api.deps import (
    AdminMember,
    CurrentMember,
    PageDep,
    SessionDep,
    StaffMember,
    is_staff,
)
from app.core.exceptions import ForbiddenError
from app.core.pagination import Page
from app.models.fine import FineStatus
from app.schemas.fine import FineRead
from app.services.fine_service import FineService

router = APIRouter(prefix="/fines", tags=["fines"])


@router.get("", response_model=Page[FineRead], summary="List fines")
async def list_fines(
    session: SessionDep,
    params: PageDep,
    current: CurrentMember,
    member_id: int | None = None,
    status_filter: FineStatus | None = None,
) -> Page[FineRead]:
    target_member = member_id
    if not is_staff(current):
        target_member = current.id

    fines, total = await FineService(session).list_fines(
        offset=params.offset,
        limit=params.limit,
        member_id=target_member,
        status=status_filter,
    )
    return Page.from_orm_items(fines, total, params, FineRead)


@router.get("/{fine_id}", response_model=FineRead, summary="Get a fine")
async def get_fine(fine_id: int, session: SessionDep, current: CurrentMember) -> FineRead:
    fine = await FineService(session).get_fine(fine_id)
    if not is_staff(current) and fine.loan.member_id != current.id:
        raise ForbiddenError("You can only read your own fines.")
    return FineRead.model_validate(fine)


@router.post("/{fine_id}/pay", response_model=FineRead, summary="Mark a fine as paid")
async def pay_fine(fine_id: int, session: SessionDep, _: StaffMember) -> FineRead:
    fine = await FineService(session).pay_fine(fine_id)
    return FineRead.model_validate(fine)


@router.post("/{fine_id}/waive", response_model=FineRead, summary="Waive a fine (admin only)")
async def waive_fine(fine_id: int, session: SessionDep, _: AdminMember) -> FineRead:
    fine = await FineService(session).waive_fine(fine_id)
    return FineRead.model_validate(fine)
