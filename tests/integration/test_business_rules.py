"""Business-rule tests for lending, reservations and fines."""

from collections.abc import Callable
from datetime import date, timedelta
from typing import Any

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models import Author, Book, BookCopy, Branch, Loan, Member, Publisher


async def make_book(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    isbn: str,
    title: str,
    copies: int = 1,
    author_id: int | None = None,
    publisher_id: int | None = None,
    publication_year: int | None = None,
    branch_id: int | None = None,
) -> tuple[Book, Branch]:
    async with session_factory() as session:
        if branch_id is None:
            branch = Branch(name=f"Branch {isbn}", address="1 Main St", city="Testville")
            session.add(branch)
            await session.flush()
            branch_id = branch.id

        book = Book(
            isbn=isbn,
            title=title,
            publication_year=publication_year,
            publisher_id=publisher_id,
        )
        if author_id is not None:
            author = await session.get(Author, author_id)
            assert author is not None
            book.authors = [author]
        session.add(book)
        await session.flush()
        for index in range(copies):
            session.add(
                BookCopy(
                    inventory_code=f"{isbn}-{index}",
                    book_id=book.id,
                    branch_id=branch_id,
                )
            )
        await session.commit()
        branch = await session.get(Branch, branch_id)
        assert branch is not None
        return book, branch


async def borrow(client: AsyncClient, headers: dict[str, str], book_id: int) -> dict[str, Any]:
    response = await client.post("/api/v1/loans", json={"book_id": book_id}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


async def set_due_date(
    session_factory: async_sessionmaker[AsyncSession],
    loan_id: int,
    due_date: date,
) -> None:
    async with session_factory() as session:
        loan = await session.scalar(select(Loan).where(Loan.id == loan_id))
        assert loan is not None
        loan.due_date = due_date
        await session.commit()


@pytest_asyncio.fixture
async def library_book(
    session_factory: async_sessionmaker[AsyncSession],
) -> Book:
    book, _ = await make_book(
        session_factory, isbn="9787777777777", title="Business Book", copies=6
    )
    return book


async def test_loan_limit_is_enforced(
    client: AsyncClient,
    member: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    library_book: Book,
) -> None:
    headers = auth_headers(member)
    for _ in range(5):
        await borrow(client, headers, library_book.id)

    response = await client.post(
        "/api/v1/loans", json={"book_id": library_book.id}, headers=headers
    )
    assert response.status_code == 422
    assert response.json()["code"] == "loan_limit_reached"


async def test_overdue_loans_block_new_borrows(
    client: AsyncClient,
    member: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    session_factory: async_sessionmaker[AsyncSession],
    library_book: Book,
) -> None:
    headers = auth_headers(member)
    first = await borrow(client, headers, library_book.id)
    await set_due_date(session_factory, first["id"], date.today() - timedelta(days=1))

    second_book, _ = await make_book(session_factory, isbn="9787777777778", title="Second Book")

    response = await client.post("/api/v1/loans", json={"book_id": second_book.id}, headers=headers)
    assert response.status_code == 422
    assert response.json()["code"] == "has_overdue_loans"


async def test_unpaid_fines_block_new_borrows(
    client: AsyncClient,
    member: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    session_factory: async_sessionmaker[AsyncSession],
    library_book: Book,
) -> None:
    headers = auth_headers(member)
    loan = await borrow(client, headers, library_book.id)
    await set_due_date(session_factory, loan["id"], date.today() - timedelta(days=2))
    assert (
        await client.post(f"/api/v1/loans/{loan['id']}/return", headers=headers)
    ).status_code == 200

    other_book, _ = await make_book(session_factory, isbn="9787777777779", title="Blocked Book")
    response = await client.post("/api/v1/loans", json={"book_id": other_book.id}, headers=headers)
    assert response.status_code == 422
    assert response.json()["code"] == "has_unpaid_fines"


async def test_overdue_and_returned_loans_cannot_be_renewed(
    client: AsyncClient,
    member: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    session_factory: async_sessionmaker[AsyncSession],
    library_book: Book,
) -> None:
    headers = auth_headers(member)
    loan = await borrow(client, headers, library_book.id)
    await set_due_date(session_factory, loan["id"], date.today() - timedelta(days=1))

    overdue = await client.post(f"/api/v1/loans/{loan['id']}/renew", headers=headers)
    assert overdue.status_code == 422
    assert overdue.json()["code"] == "has_overdue_loans"

    await client.post(f"/api/v1/loans/{loan['id']}/return", headers=headers)
    returned = await client.post(f"/api/v1/loans/{loan['id']}/renew", headers=headers)
    assert returned.status_code == 422
    assert returned.json()["code"] == "loan_already_returned"


async def test_returning_twice_is_rejected(
    client: AsyncClient,
    member: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    library_book: Book,
) -> None:
    headers = auth_headers(member)
    loan = await borrow(client, headers, library_book.id)
    assert (
        await client.post(f"/api/v1/loans/{loan['id']}/return", headers=headers)
    ).status_code == 200

    again = await client.post(f"/api/v1/loans/{loan['id']}/return", headers=headers)
    assert again.status_code == 422
    assert again.json()["code"] == "loan_already_returned"


async def test_a_reservation_blocks_renewal(
    client: AsyncClient,
    member: Member,
    other_member: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    book, _ = await make_book(
        session_factory, isbn="9788888888888", title="Contended Book", copies=1
    )
    headers = auth_headers(member)
    loan = await borrow(client, headers, book.id)

    reserved = await client.post(
        "/api/v1/reservations",
        json={"book_id": book.id},
        headers=auth_headers(other_member),
    )
    assert reserved.status_code == 201, reserved.text

    response = await client.post(f"/api/v1/loans/{loan['id']}/renew", headers=headers)
    assert response.status_code == 409
    assert response.json()["code"] == "book_reserved"


async def test_reservation_limit(
    client: AsyncClient,
    member: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    headers = auth_headers(member)
    for index in range(4):
        book, _ = await make_book(
            session_factory,
            isbn=f"978999999900{index}",
            title=f"Limit Book {index}",
            copies=0,
        )
        response = await client.post(
            "/api/v1/reservations", json={"book_id": book.id}, headers=headers
        )
        if index < 3:
            assert response.status_code == 201, response.text
        else:
            assert response.status_code == 422
            assert response.json()["code"] == "reservation_limit_reached"


async def test_overdue_refresh_endpoint(
    client: AsyncClient,
    member: Member,
    librarian: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    session_factory: async_sessionmaker[AsyncSession],
    library_book: Book,
) -> None:
    headers = auth_headers(member)
    loan = await borrow(client, headers, library_book.id)
    await set_due_date(session_factory, loan["id"], date.today() - timedelta(days=1))

    refreshed = await client.post("/api/v1/loans/overdue/refresh", headers=auth_headers(librarian))
    assert refreshed.status_code == 200
    assert refreshed.json()["updated"] == 1

    detail = await client.get(f"/api/v1/loans/{loan['id']}", headers=headers)
    assert detail.json()["status"] == "overdue"


async def test_catalogue_filters(
    client: AsyncClient,
    librarian: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        author = Author(name="Filter Author")
        publisher = Publisher(name="Filter Press")
        session.add_all([author, publisher])
        await session.commit()
        author_id = author.id
        publisher_id = publisher.id

    available_book, _ = await make_book(
        session_factory,
        isbn="9781231231231",
        title="Available Filter Book",
        copies=1,
        author_id=author_id,
        publisher_id=publisher_id,
        publication_year=2001,
    )
    await make_book(
        session_factory,
        isbn="9781231231232",
        title="Empty Filter Book",
        copies=0,
        publication_year=1999,
    )

    by_author = await client.get("/api/v1/books", params={"author_id": author_id})
    assert by_author.json()["total"] == 1

    by_publisher = await client.get("/api/v1/books", params={"publisher_id": publisher_id})
    assert by_publisher.json()["total"] == 1

    by_year = await client.get("/api/v1/books", params={"year": 1999})
    assert by_year.json()["total"] == 1

    available = await client.get("/api/v1/books", params={"available": True})
    assert any(item["id"] == available_book.id for item in available.json()["items"])

    unavailable = await client.get("/api/v1/books", params={"available": False})
    assert all(item["available_copies"] == 0 for item in unavailable.json()["items"])

    sorted_books = await client.get(
        "/api/v1/books", params={"sort": "publication_year", "order": "desc"}
    )
    years = [
        item["publication_year"]
        for item in sorted_books.json()["items"]
        if item["publication_year"] is not None
    ]
    assert years == sorted(years, reverse=True)

    branches = await client.get("/api/v1/branches", params={"city": "Testville"})
    assert branches.status_code == 200


async def test_members_cannot_read_another_members_fine(
    client: AsyncClient,
    member: Member,
    other_member: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    session_factory: async_sessionmaker[AsyncSession],
    library_book: Book,
) -> None:
    headers = auth_headers(member)
    loan = await borrow(client, headers, library_book.id)
    await set_due_date(session_factory, loan["id"], date.today() - timedelta(days=1))
    await client.post(f"/api/v1/loans/{loan['id']}/return", headers=headers)

    fines = await client.get("/api/v1/fines", headers=headers)
    fine_id = fines.json()["items"][0]["id"]

    response = await client.get(f"/api/v1/fines/{fine_id}", headers=auth_headers(other_member))
    assert response.status_code == 403
