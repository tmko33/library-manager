"""Branch endpoints."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import PageDep, SessionDep, StaffMember
from app.core.pagination import Page
from app.schemas.branch import BranchCreate, BranchRead, BranchUpdate
from app.schemas.common import Message
from app.services.branch_service import BranchService

router = APIRouter(prefix="/branches", tags=["branches"])


@router.get("", response_model=Page[BranchRead], summary="List branches")
async def list_branches(
    session: SessionDep,
    params: PageDep,
    q: Annotated[str | None, Query(max_length=150)] = None,
    city: Annotated[str | None, Query(max_length=100)] = None,
    is_active: bool | None = None,
) -> Page[BranchRead]:
    branches, total = await BranchService(session).list_branches(
        offset=params.offset,
        limit=params.limit,
        q=q,
        city=city,
        is_active=is_active,
    )
    return Page.from_orm_items(branches, total, params, BranchRead)


@router.post(
    "",
    response_model=BranchRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a branch",
)
async def create_branch(data: BranchCreate, session: SessionDep, _: StaffMember) -> BranchRead:
    branch = await BranchService(session).create_branch(data)
    return BranchRead.model_validate(branch)


@router.get("/{branch_id}", response_model=BranchRead, summary="Get a branch")
async def get_branch(branch_id: int, session: SessionDep) -> BranchRead:
    branch = await BranchService(session).get_branch(branch_id)
    return BranchRead.model_validate(branch)


@router.patch("/{branch_id}", response_model=BranchRead, summary="Update a branch")
async def update_branch(
    branch_id: int, data: BranchUpdate, session: SessionDep, _: StaffMember
) -> BranchRead:
    branch = await BranchService(session).update_branch(branch_id, data)
    return BranchRead.model_validate(branch)


@router.delete("/{branch_id}", response_model=Message, summary="Delete a branch")
async def delete_branch(branch_id: int, session: SessionDep, _: StaffMember) -> Message:
    await BranchService(session).delete_branch(branch_id)
    return Message(message="Branch deleted.")
