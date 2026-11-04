"""Loan workflow tests."""

from collections.abc import Callable
from datetime import date, timedelta

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models import Book, BookCopy, Branch, Loan, Member
from app.models.book_copy import CopyStatus


@pytest_asyncio.fixture
async def book_with_copies(
    session_factory: async_sessionmaker[AsyncSession],
) -> tuple[Book, Branch]:
    async with session_factory() as session:
        branch = Branch(name="Main", address="1 Main St", city="Testville")
        book = Book(isbn="9781111111111", title="Loanable Book")
        session.add_all([branch, book])
        await session.flush()
        for index in range(2):
            session.add(
                BookCopy(
                    inventory_code=f"L-{index:03d}",
                    book_id=book.id,
                    branch_id=branch.id,
                )
            )
        await session.commit()
        return book, branch


async def _borrow(client: AsyncClient, headers: dict[str, str], book_id: int) -> dict:
    response = await client.post("/api/v1/loans", json={"book_id": book_id}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


async def test_borrow_and_return(
    client: AsyncClient,
    member: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    session_factory: async_sessionmaker[AsyncSession],
    book_with_copies: tuple[Book, Branch],
) -> None:
    book, _ = book_with_copies
    headers = auth_headers(member)

    loan = await _borrow(client, headers, book.id)
    assert loan["status"] == "active"
    assert loan["book"]["title"] == "Loanable Book"
    assert loan["due_date"] > loan["loan_date"]

    async with session_factory() as session:
        copy = await session.get(BookCopy, loan["copy_id"])
        assert copy is not None
        assert copy.status == CopyStatus.ON_LOAN

    returned = await client.post(f"/api/v1/loans/{loan['id']}/return", headers=headers)
    assert returned.status_code == 200, returned.text
    assert returned.json()["status"] == "returned"

    async with session_factory() as session:
        copy = await session.get(BookCopy, loan["copy_id"])
        assert copy is not None
        assert copy.status == CopyStatus.AVAILABLE


async def test_borrowing_without_copies_fails(
    client: AsyncClient,
    member: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    book_with_copies: tuple[Book, Branch],
) -> None:
    book, _ = book_with_copies
    headers = auth_headers(member)

    await _borrow(client, headers, book.id)
    await _borrow(client, headers, book.id)

    response = await client.post("/api/v1/loans", json={"book_id": book.id}, headers=headers)
    assert response.status_code == 409
    assert response.json()["code"] == "no_copies_available"


async def test_late_return_creates_a_fine(
    client: AsyncClient,
    member: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    session_factory: async_sessionmaker[AsyncSession],
    book_with_copies: tuple[Book, Branch],
) -> None:
    book, _ = book_with_copies
    headers = auth_headers(member)
    loan = await _borrow(client, headers, book.id)

    async with session_factory() as session:
        stored = await session.scalar(select(Loan).where(Loan.id == loan["id"]))
        assert stored is not None
        stored.due_date = date.today() - timedelta(days=3)
        await session.commit()

    returned = await client.post(f"/api/v1/loans/{loan['id']}/return", headers=headers)
    assert returned.status_code == 200, returned.text

    fines = await client.get("/api/v1/fines", headers=headers)
    assert fines.status_code == 200
    body = fines.json()
    assert body["total"] == 1
    assert body["items"][0]["amount"] == "1.50"
    assert body["items"][0]["status"] == "pending"


async def test_renewal_limit_is_enforced(
    client: AsyncClient,
    member: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    book_with_copies: tuple[Book, Branch],
) -> None:
    book, _ = book_with_copies
    headers = auth_headers(member)
    loan = await _borrow(client, headers, book.id)

    for _ in range(2):
        response = await client.post(f"/api/v1/loans/{loan['id']}/renew", headers=headers)
        assert response.status_code == 200, response.text

    response = await client.post(f"/api/v1/loans/{loan['id']}/renew", headers=headers)
    assert response.status_code == 422
    assert response.json()["code"] == "renewal_limit_reached"


async def test_member_cannot_read_another_members_loan(
    client: AsyncClient,
    member: Member,
    librarian: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    book_with_copies: tuple[Book, Branch],
) -> None:
    book, _ = book_with_copies
    loan = await _borrow(client, auth_headers(librarian), book.id)

    response = await client.get(f"/api/v1/loans/{loan['id']}", headers=auth_headers(member))
    assert response.status_code == 403
