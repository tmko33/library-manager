"""Reservation endpoints."""

from fastapi import APIRouter, status

from app.api.deps import CurrentMember, PageDep, SessionDep, StaffMember, is_staff
from app.core.exceptions import ForbiddenError
from app.core.pagination import Page
from app.models.reservation import ReservationStatus
from app.schemas.reservation import ReservationCreate, ReservationRead
from app.services.reservation_service import ReservationService

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("", response_model=Page[ReservationRead], summary="List reservations")
async def list_reservations(
    session: SessionDep,
    params: PageDep,
    current: CurrentMember,
    member_id: int | None = None,
    book_id: int | None = None,
    status_filter: ReservationStatus | None = None,
) -> Page[ReservationRead]:
    target_member = member_id
    if not is_staff(current):
        target_member = current.id

    reservations, total = await ReservationService(session).list_reservations(
        offset=params.offset,
        limit=params.limit,
        member_id=target_member,
        book_id=book_id,
        status=status_filter,
    )
    return Page.from_orm_items(reservations, total, params, ReservationRead)


@router.post(
    "",
    response_model=ReservationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Reserve a book",
)
async def create_reservation(
    data: ReservationCreate, session: SessionDep, current: CurrentMember
) -> ReservationRead:
    target_member = data.member_id or current.id
    if data.member_id is not None and data.member_id != current.id and not is_staff(current):
        raise ForbiddenError("You cannot reserve books on behalf of another member.")

    reservation = await ReservationService(session).create_reservation(
        member_id=target_member, book_id=data.book_id
    )
    return ReservationRead.model_validate(reservation)


@router.post(
    "/expire",
    summary="Expire stale holds (staff only)",
    status_code=status.HTTP_200_OK,
)
async def expire_reservations(session: SessionDep, _: StaffMember) -> dict[str, int]:
    expired = await ReservationService(session).expire_stale()
    return {"expired": expired}


@router.get("/{reservation_id}", response_model=ReservationRead, summary="Get a reservation")
async def get_reservation(
    reservation_id: int, session: SessionDep, current: CurrentMember
) -> ReservationRead:
    reservation = await ReservationService(session).get_reservation(reservation_id)
    if not is_staff(current) and reservation.member_id != current.id:
        raise ForbiddenError("You can only read your own reservations.")
    return ReservationRead.model_validate(reservation)


@router.delete(
    "/{reservation_id}",
    response_model=ReservationRead,
    summary="Cancel a pending reservation",
)
async def cancel_reservation(
    reservation_id: int, session: SessionDep, current: CurrentMember
) -> ReservationRead:
    service = ReservationService(session)
    reservation = await service.get_reservation(reservation_id)
    if not is_staff(current) and reservation.member_id != current.id:
        raise ForbiddenError("You can only cancel your own reservations.")
    updated = await service.cancel_reservation(reservation_id)
    return ReservationRead.model_validate(updated)
