"""Catalogue endpoint tests."""

from collections.abc import Callable

from httpx import AsyncClient

from app.models import Member


async def test_staff_can_manage_the_catalogue(
    client: AsyncClient,
    librarian: Member,
    auth_headers: Callable[[Member], dict[str, str]],
) -> None:
    headers = auth_headers(librarian)

    publisher = await client.post(
        "/api/v1/publishers", json={"name": "Test Press"}, headers=headers
    )
    assert publisher.status_code == 201, publisher.text
    publisher_id = publisher.json()["id"]

    author = await client.post(
        "/api/v1/authors",
        json={"name": "Test Author", "birth_year": 1970},
        headers=headers,
    )
    assert author.status_code == 201, author.text
    author_id = author.json()["id"]

    book = await client.post(
        "/api/v1/books",
        json={
            "isbn": "9780000000001",
            "title": "Testing FastAPI",
            "publication_year": 2024,
            "publisher_id": publisher_id,
            "author_ids": [author_id],
        },
        headers=headers,
    )
    assert book.status_code == 201, book.text
    book_body = book.json()
    assert book_body["authors"][0]["name"] == "Test Author"
    assert book_body["total_copies"] == 0
    book_id = book_body["id"]

    branch = await client.post(
        "/api/v1/branches",
        json={"name": "Test Branch", "address": "Evergreen 742", "city": "Springfield"},
        headers=headers,
    )
    assert branch.status_code == 201, branch.text
    branch_id = branch.json()["id"]

    copy = await client.post(
        f"/api/v1/books/{book_id}/copies",
        json={"book_id": book_id, "branch_id": branch_id, "inventory_code": "T-0001"},
        headers=headers,
    )
    assert copy.status_code == 201, copy.text

    detail = await client.get(f"/api/v1/books/{book_id}")
    assert detail.json()["total_copies"] == 1
    assert detail.json()["available_copies"] == 1

    updated = await client.patch(
        f"/api/v1/books/{book_id}", json={"title": "Testing FastAPI 2e"}, headers=headers
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Testing FastAPI 2e"


async def test_duplicate_isbn_is_rejected(
    client: AsyncClient,
    librarian: Member,
    auth_headers: Callable[[Member], dict[str, str]],
) -> None:
    headers = auth_headers(librarian)
    payload = {"isbn": "9780000000002", "title": "Duplicate"}

    assert (await client.post("/api/v1/books", json=payload, headers=headers)).status_code == 201
    response = await client.post("/api/v1/books", json=payload, headers=headers)

    assert response.status_code == 409
    assert response.json()["code"] == "duplicate_isbn"


async def test_members_cannot_create_books(
    client: AsyncClient,
    member: Member,
    auth_headers: Callable[[Member], dict[str, str]],
) -> None:
    response = await client.post(
        "/api/v1/books",
        json={"isbn": "9780000000003", "title": "Forbidden"},
        headers=auth_headers(member),
    )
    assert response.status_code == 403


async def test_book_search_filters(
    client: AsyncClient,
    librarian: Member,
    auth_headers: Callable[[Member], dict[str, str]],
) -> None:
    headers = auth_headers(librarian)
    for index, title in enumerate(["Alpha Book", "Beta Novel"], start=1):
        response = await client.post(
            "/api/v1/books",
            json={"isbn": f"97800000001{index:02d}", "title": title},
            headers=headers,
        )
        assert response.status_code == 201, response.text

    response = await client.get("/api/v1/books", params={"q": "alpha"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Alpha Book"


async def test_missing_book_returns_problem_json(client: AsyncClient) -> None:
    response = await client.get("/api/v1/books/9999")
    assert response.status_code == 404
    assert response.json()["code"] == "book_not_found"
