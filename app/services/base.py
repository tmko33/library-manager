"""Shared service behaviour."""

from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    """Base class holding the request-scoped session."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def commit(self) -> None:
        await self.session.commit()
