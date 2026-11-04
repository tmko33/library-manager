"""Integration tests for reservations, fines and staff operations."""

from collections.abc import Callable
from datetime import date, timedelta

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models import (
    Book,
    BookCopy,
    Branch,
    Loan,
    Member,
    Reservation,
    ReservationStatus,
)


@pytest_asyncio.fixture
async def empty_book(
    session_factory: async_sessionmaker[AsyncSession],
) -> tuple[Book, Branch]:
    async with session_factory() as session:
        branch = Branch(name="Empty Branch", address="2 Main St", city="Testville")
        book = Book(isbn="9782222222222", title="Reserved Title")
        session.add_all([branch, book])
        await session.commit()
        return book, branch


@pytest_asyncio.fixture
async def stocked_book(
    session_factory: async_sessionmaker[AsyncSession],
) -> tuple[Book, Branch]:
    async with session_factory() as session:
        branch = Branch(name="Stocked Branch", address="3 Main St", city="Testville")
        book = Book(isbn="9783333333333", title="Stocked Title")
        session.add_all([branch, book])
        await session.flush()
        session.add(BookCopy(inventory_code="S-001", book_id=book.id, branch_id=branch.id))
        await session.commit()
        return book, branch


async def test_reservation_queue_respects_priority(
    client: AsyncClient,
    member: Member,
    other_member: Member,
    librarian: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    session_factory: async_sessionmaker[AsyncSession],
    empty_book: tuple[Book, Branch],
) -> None:
    book, branch = empty_book
    headers = auth_headers(member)

    created = await client.post("/api/v1/reservations", json={"book_id": book.id}, headers=headers)
    assert created.status_code == 201, created.text
    reservation_id = created.json()["id"]

    duplicate = await client.post(
        "/api/v1/reservations", json={"book_id": book.id}, headers=headers
    )
    assert duplicate.status_code == 409

    added = await client.post(
        f"/api/v1/books/{book.id}/copies",
        json={"book_id": book.id, "branch_id": branch.id, "inventory_code": "R-001"},
        headers=auth_headers(librarian),
    )
    assert added.status_code == 201, added.text

    blocked = await client.post(
        "/api/v1/loans", json={"book_id": book.id}, headers=auth_headers(other_member)
    )
    assert blocked.status_code == 409
    assert blocked.json()["code"] == "book_reserved"

    loan = await client.post("/api/v1/loans", json={"book_id": book.id}, headers=headers)
    assert loan.status_code == 201, loan.text

    async with session_factory() as session:
        stored = await session.get(Reservation, reservation_id)
        assert stored is not None
        assert stored.status == ReservationStatus.FULFILLED


async def test_reservation_requires_no_available_copies(
    client: AsyncClient,
    member: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    stocked_book: tuple[Book, Branch],
) -> None:
    book, _ = stocked_book
    response = await client.post(
        "/api/v1/reservations",
        json={"book_id": book.id},
        headers=auth_headers(member),
    )
    assert response.status_code == 409
    assert response.json()["code"] == "book_available"


async def test_cancelling_a_reservation(
    client: AsyncClient,
    member: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    empty_book: tuple[Book, Branch],
) -> None:
    book, _ = empty_book
    headers = auth_headers(member)
    created = await client.post("/api/v1/reservations", json={"book_id": book.id}, headers=headers)
    reservation_id = created.json()["id"]

    cancelled = await client.delete(f"/api/v1/reservations/{reservation_id}", headers=headers)
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"

    again = await client.delete(f"/api/v1/reservations/{reservation_id}", headers=headers)
    assert again.status_code == 409


async def test_staff_can_expire_stale_holds(
    client: AsyncClient,
    member: Member,
    librarian: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    session_factory: async_sessionmaker[AsyncSession],
    empty_book: tuple[Book, Branch],
) -> None:
    book, _ = empty_book
    created = await client.post(
        "/api/v1/reservations",
        json={"book_id": book.id},
        headers=auth_headers(member),
    )
    reservation_id = created.json()["id"]

    async with session_factory() as session:
        stored = await session.get(Reservation, reservation_id)
        assert stored is not None
        stored.expires_at = date.today() - timedelta(days=1)
        await session.commit()

    response = await client.post("/api/v1/reservations/expire", headers=auth_headers(librarian))
    assert response.status_code == 200
    assert response.json()["expired"] == 1

    async with session_factory() as session:
        stored = await session.get(Reservation, reservation_id)
        assert stored is not None
        assert stored.status == ReservationStatus.EXPIRED


async def test_fine_can_be_paid_once(
    client: AsyncClient,
    member: Member,
    librarian: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    session_factory: async_sessionmaker[AsyncSession],
    stocked_book: tuple[Book, Branch],
) -> None:
    book, _ = stocked_book
    headers = auth_headers(member)
    loan = await client.post("/api/v1/loans", json={"book_id": book.id}, headers=headers)
    loan_id = loan.json()["id"]

    async with session_factory() as session:
        stored = await session.scalar(select(Loan).where(Loan.id == loan_id))
        assert stored is not None
        stored.due_date = date.today() - timedelta(days=2)
        await session.commit()

    assert (
        await client.post(f"/api/v1/loans/{loan_id}/return", headers=headers)
    ).status_code == 200

    fines = await client.get("/api/v1/fines", headers=headers)
    fine = fines.json()["items"][0]
    assert fine["amount"] == "1.00"

    paid = await client.post(f"/api/v1/fines/{fine['id']}/pay", headers=auth_headers(librarian))
    assert paid.status_code == 200
    assert paid.json()["status"] == "paid"

    again = await client.post(f"/api/v1/fines/{fine['id']}/pay", headers=auth_headers(librarian))
    assert again.status_code == 409


async def test_admin_can_waive_a_fine(
    client: AsyncClient,
    member: Member,
    admin: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    session_factory: async_sessionmaker[AsyncSession],
    stocked_book: tuple[Book, Branch],
) -> None:
    book, _ = stocked_book
    headers = auth_headers(member)
    loan = await client.post("/api/v1/loans", json={"book_id": book.id}, headers=headers)
    loan_id = loan.json()["id"]

    async with session_factory() as session:
        stored = await session.scalar(select(Loan).where(Loan.id == loan_id))
        assert stored is not None
        stored.due_date = date.today() - timedelta(days=1)
        await session.commit()

    await client.post(f"/api/v1/loans/{loan_id}/return", headers=headers)
    fines = await client.get("/api/v1/fines", headers=headers)
    fine_id = fines.json()["items"][0]["id"]

    waived = await client.post(f"/api/v1/fines/{fine_id}/waive", headers=auth_headers(admin))
    assert waived.status_code == 200
    assert waived.json()["status"] == "waived"


async def test_member_profile_visibility(
    client: AsyncClient,
    member: Member,
    other_member: Member,
    librarian: Member,
    auth_headers: Callable[[Member], dict[str, str]],
) -> None:
    own = await client.get(f"/api/v1/members/{member.id}", headers=auth_headers(member))
    assert own.status_code == 200

    foreign = await client.get(f"/api/v1/members/{other_member.id}", headers=auth_headers(member))
    assert foreign.status_code == 403

    listing = await client.get("/api/v1/members", headers=auth_headers(librarian))
    assert listing.status_code == 200
    assert listing.json()["total"] >= 2


async def test_staff_can_update_and_deactivate_a_member(
    client: AsyncClient,
    member: Member,
    librarian: Member,
    auth_headers: Callable[[Member], dict[str, str]],
) -> None:
    headers = auth_headers(librarian)
    updated = await client.patch(
        f"/api/v1/members/{member.id}",
        json={"full_name": "Renamed Member"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Renamed Member"

    deleted = await client.delete(f"/api/v1/members/{member.id}", headers=headers)
    assert deleted.status_code == 200

    deactivated = await client.get(f"/api/v1/members/{member.id}", headers=headers)
    assert deactivated.json()["is_active"] is False


async def test_book_with_active_loan_cannot_be_deleted(
    client: AsyncClient,
    member: Member,
    librarian: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    stocked_book: tuple[Book, Branch],
) -> None:
    book, _ = stocked_book
    loan = await client.post(
        "/api/v1/loans", json={"book_id": book.id}, headers=auth_headers(member)
    )
    assert loan.status_code == 201

    response = await client.delete(f"/api/v1/books/{book.id}", headers=auth_headers(librarian))
    assert response.status_code == 409
    assert response.json()["code"] == "book_has_active_loans"


async def test_copy_lifecycle(
    client: AsyncClient,
    librarian: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    stocked_book: tuple[Book, Branch],
) -> None:
    book, branch = stocked_book
    headers = auth_headers(librarian)

    created = await client.post(
        f"/api/v1/books/{book.id}/copies",
        json={"book_id": book.id, "branch_id": branch.id, "inventory_code": "S-002"},
        headers=headers,
    )
    assert created.status_code == 201, created.text
    copy_id = created.json()["id"]

    duplicate = await client.post(
        f"/api/v1/books/{book.id}/copies",
        json={"book_id": book.id, "branch_id": branch.id, "inventory_code": "S-002"},
        headers=headers,
    )
    assert duplicate.status_code == 409

    updated = await client.patch(
        f"/api/v1/copies/{copy_id}", json={"status": "maintenance"}, headers=headers
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "maintenance"

    listing = await client.get("/api/v1/copies", params={"book_id": book.id}, headers=headers)
    assert listing.status_code == 200

    deleted = await client.delete(f"/api/v1/copies/{copy_id}", headers=headers)
    assert deleted.status_code == 200


async def test_reference_crud(
    client: AsyncClient,
    librarian: Member,
    auth_headers: Callable[[Member], dict[str, str]],
) -> None:
    headers = auth_headers(librarian)

    country = await client.post(
        "/api/v1/countries", json={"name": "Testland", "iso_code": "TL"}, headers=headers
    )
    assert country.status_code == 201, country.text
    country_id = country.json()["id"]

    duplicated = await client.post("/api/v1/countries", json={"name": "Testland"}, headers=headers)
    assert duplicated.status_code == 409

    branch = await client.post(
        "/api/v1/branches",
        json={
            "name": "Reference Branch",
            "address": "4 Main St",
            "city": "Testville",
            "country_id": country_id,
        },
        headers=headers,
    )
    assert branch.status_code == 201, branch.text

    publisher = await client.post(
        "/api/v1/publishers", json={"name": "Reference Press"}, headers=headers
    )
    assert publisher.status_code == 201

    listed = await client.get("/api/v1/countries", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["total"] >= 1

    removed = await client.delete(f"/api/v1/countries/{country_id}", headers=headers)
    assert removed.status_code == 200
