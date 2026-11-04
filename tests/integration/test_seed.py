"""Demo seeding tests."""

from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.demo_data import DEMO_PASSWORD, seed_demo_data
from app.models import Book, BookCopy, Member


async def test_seed_is_idempotent(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        assert await seed_demo_data(session) is True

    async with session_factory() as session:
        assert await seed_demo_data(session) is False
        assert await session.scalar(select(func.count()).select_from(Book)) == 4
        assert await session.scalar(select(func.count()).select_from(BookCopy)) == 12
        assert await session.scalar(select(func.count()).select_from(Member)) == 3


async def test_seeded_admin_can_log_in(
    client: AsyncClient,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        await seed_demo_data(session)

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin@library.dev", "password": DEMO_PASSWORD},
    )
    assert response.status_code == 200, response.text
    assert response.json()["access_token"]
