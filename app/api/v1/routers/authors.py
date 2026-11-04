"""Author endpoints."""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import PageDep, SessionDep, StaffMember
from app.core.pagination import Page
from app.schemas.author import AuthorCreate, AuthorRead, AuthorUpdate
from app.schemas.common import Message
from app.services.reference_service import AuthorService

router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("", response_model=Page[AuthorRead], summary="List authors")
async def list_authors(
    session: SessionDep,
    params: PageDep,
    q: Annotated[str | None, Query(max_length=150)] = None,
) -> Page[AuthorRead]:
    authors, total = await AuthorService(session).list_authors(
        offset=params.offset, limit=params.limit, q=q
    )
    return Page.from_orm_items(authors, total, params, AuthorRead)


@router.post(
    "",
    response_model=AuthorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create an author",
)
async def create_author(data: AuthorCreate, session: SessionDep, _: StaffMember) -> AuthorRead:
    author = await AuthorService(session).create_author(data)
    return AuthorRead.model_validate(author)


@router.get("/{author_id}", response_model=AuthorRead, summary="Get an author")
async def get_author(author_id: int, session: SessionDep) -> AuthorRead:
    author = await AuthorService(session).get_author(author_id)
    return AuthorRead.model_validate(author)


@router.patch("/{author_id}", response_model=AuthorRead, summary="Update an author")
async def update_author(
    author_id: int, data: AuthorUpdate, session: SessionDep, _: StaffMember
) -> AuthorRead:
    author = await AuthorService(session).update_author(author_id, data)
    return AuthorRead.model_validate(author)


@router.delete("/{author_id}", response_model=Message, summary="Delete an author")
async def delete_author(author_id: int, session: SessionDep, _: StaffMember) -> Message:
    await AuthorService(session).delete_author(author_id)
    return Message(message="Author deleted.")
