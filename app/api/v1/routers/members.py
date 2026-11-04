"""Member endpoints."""

from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import CurrentMember, PageDep, SessionDep, StaffMember, is_staff
from app.core.exceptions import ForbiddenError
from app.core.pagination import Page
from app.schemas.common import Message
from app.schemas.member import MemberCreate, MemberRead, MemberUpdate
from app.services.member_service import MemberService

router = APIRouter(prefix="/members", tags=["members"])


@router.get("", response_model=Page[MemberRead], summary="List members")
async def list_members(
    session: SessionDep,
    params: PageDep,
    _: StaffMember,
    q: Annotated[str | None, Query(max_length=150)] = None,
    is_active: bool | None = None,
) -> Page[MemberRead]:
    members, total = await MemberService(session).list_members(
        offset=params.offset, limit=params.limit, q=q, is_active=is_active
    )
    return Page.from_orm_items(members, total, params, MemberRead)


@router.post(
    "",
    response_model=MemberRead,
    status_code=201,
    summary="Create a member or staff account",
)
async def create_member(data: MemberCreate, session: SessionDep, _: StaffMember) -> MemberRead:
    member = await MemberService(session).create_member(data)
    return MemberRead.model_validate(member)


@router.get("/{member_id}", response_model=MemberRead, summary="Get a member profile")
async def get_member(member_id: int, session: SessionDep, current: CurrentMember) -> MemberRead:
    if not is_staff(current) and current.id != member_id:
        raise ForbiddenError("You can only read your own profile.")
    member = await MemberService(session).get_member(member_id)
    return MemberRead.model_validate(member)


@router.patch("/{member_id}", response_model=MemberRead, summary="Update a member")
async def update_member(
    member_id: int, data: MemberUpdate, session: SessionDep, _: StaffMember
) -> MemberRead:
    member = await MemberService(session).update_member(member_id, data)
    return MemberRead.model_validate(member)


@router.delete("/{member_id}", response_model=Message, summary="Deactivate a member")
async def deactivate_member(member_id: int, session: SessionDep, _: StaffMember) -> Message:
    await MemberService(session).deactivate_member(member_id)
    return Message(message="Member deactivated.")
