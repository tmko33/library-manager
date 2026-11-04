"""Book endpoints."""

from typing import Annotated, Literal

from fastapi import APIRouter, Query, status

from app.api.deps import PageDep, SessionDep, StaffMember
from app.core.pagination import Page
from app.schemas.book import BookCreate, BookRead, BookUpdate
from app.schemas.common import Message
from app.schemas.copy import CopyCreate, CopyRead
from app.services.book_service import BookService
from app.services.copy_service import CopyService

router = APIRouter(prefix="/books", tags=["books"])

SortField = Literal["title", "publication_year", "created_at"]


@router.get("", response_model=Page[BookRead], summary="Search the catalogue")
async def list_books(
    session: SessionDep,
    params: PageDep,
    q: Annotated[str | None, Query(max_length=150)] = None,
    author_id: int | None = None,
    publisher_id: int | None = None,
    year: int | None = None,
    available: bool | None = None,
    sort: SortField = "title",
    order: Literal["asc", "desc"] = "asc",
) -> Page[BookRead]:
    books, total = await BookService(session).list_books(
        offset=params.offset,
        limit=params.limit,
        q=q,
        author_id=author_id,
        publisher_id=publisher_id,
        year=year,
        available=available,
        sort=sort,
        order=order,
    )
    return Page.from_orm_items(books, total, params, BookRead)


@router.post(
    "",
    response_model=BookRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a book",
)
async def create_book(data: BookCreate, session: SessionDep, _: StaffMember) -> BookRead:
    book = await BookService(session).create_book(data)
    return BookRead.model_validate(book)


@router.get("/{book_id}", response_model=BookRead, summary="Get a book")
async def get_book(book_id: int, session: SessionDep) -> BookRead:
    book = await BookService(session).get_book(book_id)
    return BookRead.model_validate(book)


@router.patch("/{book_id}", response_model=BookRead, summary="Update a book")
async def update_book(
    book_id: int, data: BookUpdate, session: SessionDep, _: StaffMember
) -> BookRead:
    book = await BookService(session).update_book(book_id, data)
    return BookRead.model_validate(book)


@router.delete("/{book_id}", response_model=Message, summary="Delete a book")
async def delete_book(book_id: int, session: SessionDep, _: StaffMember) -> Message:
    await BookService(session).delete_book(book_id)
    return Message(message="Book deleted.")


@router.get(
    "/{book_id}/copies",
    response_model=Page[CopyRead],
    summary="List the copies of a book",
)
async def list_book_copies(
    book_id: int,
    session: SessionDep,
    params: PageDep,
) -> Page[CopyRead]:
    await BookService(session).get_book(book_id)
    copies, total = await CopyService(session).list_copies(
        offset=params.offset, limit=params.limit, book_id=book_id
    )
    return Page.from_orm_items(copies, total, params, CopyRead)


@router.post(
    "/{book_id}/copies",
    response_model=CopyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new copy of a book",
)
async def create_book_copy(
    book_id: int,
    data: CopyCreate,
    session: SessionDep,
    _: StaffMember,
) -> CopyRead:
    payload = data.model_copy(update={"book_id": book_id})
    copy = await CopyService(session).create_copy(payload)
    return CopyRead.model_validate(copy)
