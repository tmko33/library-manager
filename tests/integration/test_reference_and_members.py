"""Reference data, member administration and validation tests."""

from collections.abc import Callable

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models import Book, BookCopy, Branch, Member


async def test_author_and_publisher_lifecycle(
    client: AsyncClient,
    librarian: Member,
    auth_headers: Callable[[Member], dict[str, str]],
) -> None:
    headers = auth_headers(librarian)

    country = await client.post(
        "/api/v1/countries", json={"name": "Uruguay", "iso_code": "UY"}, headers=headers
    )
    country_id = country.json()["id"]

    author = await client.post(
        "/api/v1/authors",
        json={"name": "Mario Benedetti", "birth_year": 1920, "country_id": country_id},
        headers=headers,
    )
    assert author.status_code == 201, author.text
    author_id = author.json()["id"]

    detail = await client.get(f"/api/v1/authors/{author_id}")
    assert detail.status_code == 200
    assert detail.json()["country"]["name"] == "Uruguay"

    updated = await client.patch(
        f"/api/v1/authors/{author_id}", json={"bio": "Uruguayan writer."}, headers=headers
    )
    assert updated.status_code == 200
    assert updated.json()["bio"] == "Uruguayan writer."

    publisher = await client.post("/api/v1/publishers", json={"name": "Alfaguara"}, headers=headers)
    assert publisher.status_code == 201
    publisher_id = publisher.json()["id"]

    updated_publisher = await client.patch(
        f"/api/v1/publishers/{publisher_id}",
        json={"website": "https://example.com"},
        headers=headers,
    )
    assert updated_publisher.status_code == 200

    assert (
        await client.delete(f"/api/v1/publishers/{publisher_id}", headers=headers)
    ).status_code == 200
    assert (await client.delete(f"/api/v1/authors/{author_id}", headers=headers)).status_code == 200


async def test_book_relations_and_validation(
    client: AsyncClient,
    librarian: Member,
    auth_headers: Callable[[Member], dict[str, str]],
) -> None:
    headers = auth_headers(librarian)

    invalid_author = await client.post(
        "/api/v1/books",
        json={"isbn": "9784444444444", "title": "Orphan", "author_ids": [999]},
        headers=headers,
    )
    assert invalid_author.status_code == 404
    assert invalid_author.json()["code"] == "author_not_found"

    invalid_publisher = await client.post(
        "/api/v1/books",
        json={"isbn": "9784444444445", "title": "Orphan 2", "publisher_id": 999},
        headers=headers,
    )
    assert invalid_publisher.status_code == 404
    assert invalid_publisher.json()["code"] == "publisher_not_found"

    author = await client.post("/api/v1/authors", json={"name": "Primary Author"}, headers=headers)
    other_author = await client.post(
        "/api/v1/authors", json={"name": "Secondary Author"}, headers=headers
    )
    created = await client.post(
        "/api/v1/books",
        json={
            "isbn": "9784444444446",
            "title": "Relations",
            "author_ids": [author.json()["id"]],
        },
        headers=headers,
    )
    assert created.status_code == 201, created.text
    book_id = created.json()["id"]

    updated = await client.patch(
        f"/api/v1/books/{book_id}",
        json={"author_ids": [other_author.json()["id"]]},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["authors"][0]["name"] == "Secondary Author"

    duplicate = await client.post(
        "/api/v1/books",
        json={"isbn": "9784444444446", "title": "Copycat"},
        headers=headers,
    )
    assert duplicate.status_code == 409


async def test_branch_with_copies_cannot_be_deleted(
    client: AsyncClient,
    librarian: Member,
    auth_headers: Callable[[Member], dict[str, str]],
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    headers = auth_headers(librarian)
    async with session_factory() as session:
        branch = Branch(name="Busy Branch", address="5 Main St", city="Testville")
        book = Book(isbn="9785555555555", title="Branch Book")
        session.add_all([branch, book])
        await session.flush()
        session.add(BookCopy(inventory_code="B-001", book_id=book.id, branch_id=branch.id))
        await session.commit()
        branch_id = branch.id
        book_id = book.id

    response = await client.delete(f"/api/v1/branches/{branch_id}", headers=headers)
    assert response.status_code == 409
    assert response.json()["code"] == "branch_has_copies"

    copies = await client.get("/api/v1/copies", params={"book_id": book_id}, headers=headers)
    copy_id = copies.json()["items"][0]["id"]
    assert (await client.delete(f"/api/v1/copies/{copy_id}", headers=headers)).status_code == 200
    assert (
        await client.delete(f"/api/v1/branches/{branch_id}", headers=headers)
    ).status_code == 200


async def test_copy_validation_errors(
    client: AsyncClient,
    librarian: Member,
    auth_headers: Callable[[Member], dict[str, str]],
) -> None:
    headers = auth_headers(librarian)

    missing_book = await client.post(
        "/api/v1/copies",
        json={"book_id": 999, "branch_id": 999, "inventory_code": "X-001"},
        headers=headers,
    )
    assert missing_book.status_code == 404
    assert missing_book.json()["code"] == "book_not_found"

    book = await client.post(
        "/api/v1/books", json={"isbn": "9786666666666", "title": "Copy Target"}, headers=headers
    )
    missing_branch = await client.post(
        "/api/v1/copies",
        json={
            "book_id": book.json()["id"],
            "branch_id": 999,
            "inventory_code": "X-002",
        },
        headers=headers,
    )
    assert missing_branch.status_code == 404
    assert missing_branch.json()["code"] == "branch_not_found"


async def test_member_administration_rules(
    client: AsyncClient,
    librarian: Member,
    admin: Member,
    auth_headers: Callable[[Member], dict[str, str]],
) -> None:
    librarian_headers = auth_headers(librarian)
    admin_headers = auth_headers(admin)

    created = await client.post(
        "/api/v1/members",
        json={
            "email": "staff-created@test.dev",
            "password": "password123",
            "full_name": "Staff Created",
        },
        headers=librarian_headers,
    )
    assert created.status_code == 201, created.text
    member_id = created.json()["id"]

    duplicate = await client.post(
        "/api/v1/members",
        json={
            "email": "staff-created@test.dev",
            "password": "password123",
            "full_name": "Duplicate",
        },
        headers=librarian_headers,
    )
    assert duplicate.status_code == 409

    escalation = await client.post(
        "/api/v1/members",
        json={
            "email": "sneaky-admin@test.dev",
            "password": "password123",
            "full_name": "Sneaky",
            "role": "admin",
        },
        headers=librarian_headers,
    )
    assert escalation.status_code == 403

    allowed = await client.post(
        "/api/v1/members",
        json={
            "email": "real-admin@test.dev",
            "password": "password123",
            "full_name": "Real Admin",
            "role": "admin",
        },
        headers=admin_headers,
    )
    assert allowed.status_code == 201

    promote = await client.patch(
        f"/api/v1/members/{member_id}", json={"role": "admin"}, headers=librarian_headers
    )
    assert promote.status_code == 403

    renamed = await client.patch(
        f"/api/v1/members/{member_id}",
        json={"full_name": "Renamed Again"},
        headers=librarian_headers,
    )
    assert renamed.status_code == 200


async def test_public_registration_cannot_choose_a_role(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wannabe-admin@test.dev",
            "password": "password123",
            "full_name": "Wannabe",
            "role": "admin",
        },
    )
    assert response.status_code == 201
    assert response.json()["role"] == "member"


async def test_deactivated_member_cannot_authenticate(
    client: AsyncClient,
    librarian: Member,
    member: Member,
    auth_headers: Callable[[Member], dict[str, str]],
) -> None:
    assert (
        await client.delete(f"/api/v1/members/{member.id}", headers=auth_headers(librarian))
    ).status_code == 200

    login = await client.post(
        "/api/v1/auth/login",
        data={"username": member.email, "password": "password123"},
    )
    assert login.status_code == 403
    assert login.json()["code"] == "inactive_member"

    me = await client.get("/api/v1/auth/me", headers=auth_headers(member))
    assert me.status_code == 401


async def test_validation_errors_use_problem_json(
    client: AsyncClient,
    librarian: Member,
    auth_headers: Callable[[Member], dict[str, str]],
) -> None:
    response = await client.post(
        "/api/v1/books", json={"isbn": "123"}, headers=auth_headers(librarian)
    )
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")
    body = response.json()
    assert body["code"] == "validation_error"
    assert any(error["field"] == "title" for error in body["errors"])
