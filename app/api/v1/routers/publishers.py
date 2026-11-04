"""Publisher endpoints."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import PageDep, SessionDep, StaffMember
from app.core.pagination import Page
from app.schemas.common import Message
from app.schemas.publisher import PublisherCreate, PublisherRead, PublisherUpdate
from app.services.reference_service import PublisherService

router = APIRouter(prefix="/publishers", tags=["publishers"])


@router.get("", response_model=Page[PublisherRead], summary="List publishers")
async def list_publishers(
    session: SessionDep,
    params: PageDep,
    q: Annotated[str | None, Query(max_length=150)] = None,
) -> Page[PublisherRead]:
    publishers, total = await PublisherService(session).list_publishers(
        offset=params.offset, limit=params.limit, q=q
    )
    return Page.from_orm_items(publishers, total, params, PublisherRead)


@router.post(
    "",
    response_model=PublisherRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a publisher",
)
async def create_publisher(
    data: PublisherCreate, session: SessionDep, _: StaffMember
) -> PublisherRead:
    publisher = await PublisherService(session).create_publisher(data)
    return PublisherRead.model_validate(publisher)


@router.get("/{publisher_id}", response_model=PublisherRead, summary="Get a publisher")
async def get_publisher(publisher_id: int, session: SessionDep) -> PublisherRead:
    publisher = await PublisherService(session).get_publisher(publisher_id)
    return PublisherRead.model_validate(publisher)


@router.patch("/{publisher_id}", response_model=PublisherRead, summary="Update a publisher")
async def update_publisher(
    publisher_id: int, data: PublisherUpdate, session: SessionDep, _: StaffMember
) -> PublisherRead:
    publisher = await PublisherService(session).update_publisher(publisher_id, data)
    return PublisherRead.model_validate(publisher)


@router.delete("/{publisher_id}", response_model=Message, summary="Delete a publisher")
async def delete_publisher(publisher_id: int, session: SessionDep, _: StaffMember) -> Message:
    await PublisherService(session).delete_publisher(publisher_id)
    return Message(message="Publisher deleted.")
