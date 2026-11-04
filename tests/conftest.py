"""Shared pytest fixtures."""

from collections.abc import AsyncIterator, Callable

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

import app.models
from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Member, MemberRole

TEST_PASSWORD = "password123"


@pytest_asyncio.fixture
async def engine() -> AsyncIterator[AsyncEngine]:
    test_engine = create_async_engine(settings.test_database_url, poolclass=NullPool)
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture
async def session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncClient]:
    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
        yield http_client
    app.dependency_overrides.clear()


async def _create_member(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    email: str,
    role: MemberRole,
    full_name: str,
) -> Member:
    async with session_factory() as session:
        member = Member(
            email=email,
            hashed_password=hash_password(TEST_PASSWORD),
            full_name=full_name,
            role=role,
        )
        session.add(member)
        await session.commit()
        return member


@pytest_asyncio.fixture
async def admin(
    session_factory: async_sessionmaker[AsyncSession],
) -> Member:
    return await _create_member(
        session_factory, email="admin@test.dev", role=MemberRole.ADMIN, full_name="Admin"
    )


@pytest_asyncio.fixture
async def librarian(
    session_factory: async_sessionmaker[AsyncSession],
) -> Member:
    return await _create_member(
        session_factory,
        email="librarian@test.dev",
        role=MemberRole.LIBRARIAN,
        full_name="Librarian",
    )


@pytest_asyncio.fixture
async def member(
    session_factory: async_sessionmaker[AsyncSession],
) -> Member:
    return await _create_member(
        session_factory,
        email="member@test.dev",
        role=MemberRole.MEMBER,
        full_name="Member",
    )


@pytest_asyncio.fixture
async def other_member(
    session_factory: async_sessionmaker[AsyncSession],
) -> Member:
    return await _create_member(
        session_factory,
        email="other@test.dev",
        role=MemberRole.MEMBER,
        full_name="Other Member",
    )


@pytest_asyncio.fixture
def auth_headers() -> Callable[[Member], dict[str, str]]:
    def _headers(member: Member) -> dict[str, str]:
        return {"Authorization": f"Bearer {create_access_token(member.id)}"}

    return _headers
