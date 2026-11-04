"""Book copy endpoints."""

from fastapi import APIRouter

from app.api.deps import PageDep, SessionDep, StaffMember
from app.core.pagination import Page
from app.models.book_copy import CopyStatus
from app.schemas.common import Message
from app.schemas.copy import CopyReadDetailed, CopyUpdate
from app.services.copy_service import CopyService

router = APIRouter(prefix="/copies", tags=["copies"])


@router.get("", response_model=Page[CopyReadDetailed], summary="List copies")
async def list_copies(
    session: SessionDep,
    params: PageDep,
    book_id: int | None = None,
    branch_id: int | None = None,
    status_filter: CopyStatus | None = None,
) -> Page[CopyReadDetailed]:
    copies, total = await CopyService(session).list_copies(
        offset=params.offset,
        limit=params.limit,
        book_id=book_id,
        branch_id=branch_id,
        status=status_filter,
    )
    return Page.from_orm_items(copies, total, params, CopyReadDetailed)


@router.get("/{copy_id}", response_model=CopyReadDetailed, summary="Get a copy")
async def get_copy(copy_id: int, session: SessionDep) -> CopyReadDetailed:
    copy = await CopyService(session).get_copy(copy_id)
    return CopyReadDetailed.model_validate(copy)


@router.patch("/{copy_id}", response_model=CopyReadDetailed, summary="Update a copy")
async def update_copy(
    copy_id: int, data: CopyUpdate, session: SessionDep, _: StaffMember
) -> CopyReadDetailed:
    copy = await CopyService(session).update_copy(copy_id, data)
    return CopyReadDetailed.model_validate(copy)


@router.delete("/{copy_id}", response_model=Message, summary="Delete a copy")
async def delete_copy(copy_id: int, session: SessionDep, _: StaffMember) -> Message:
    await CopyService(session).delete_copy(copy_id)
    return Message(message="Copy deleted.")
