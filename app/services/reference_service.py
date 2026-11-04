"""Author and publisher services."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AuthorNotFoundError,
    ConflictError,
    CountryNotFoundError,
    PublisherNotFoundError,
)
from app.models.author import Author
from app.models.publisher import Publisher
from app.repositories.author_repository import AuthorRepository
from app.repositories.country_repository import CountryRepository
from app.repositories.publisher_repository import PublisherRepository
from app.schemas.author import AuthorCreate, AuthorUpdate
from app.schemas.publisher import PublisherCreate, PublisherUpdate
from app.services.base import BaseService


class AuthorService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.authors = AuthorRepository(session)
        self.countries = CountryRepository(session)

    async def list_authors(
        self, *, offset: int, limit: int, q: str | None = None
    ) -> tuple[list[Author], int]:
        return await self.authors.list_paginated(offset=offset, limit=limit, q=q)

    async def get_author(self, author_id: int) -> Author:
        author = await self.authors.get_detailed(author_id)
        if author is None:
            raise AuthorNotFoundError(f"Author {author_id} does not exist.")
        return author

    async def create_author(self, data: AuthorCreate) -> Author:
        if data.country_id is not None and await self.countries.get(data.country_id) is None:
            raise CountryNotFoundError(f"Country {data.country_id} does not exist.")
        author = Author(**data.model_dump())
        await self.authors.add(author)
        await self.commit()
        return await self.get_author(author.id)

    async def update_author(self, author_id: int, data: AuthorUpdate) -> Author:
        author = await self.get_author(author_id)
        changes = data.model_dump(exclude_unset=True)
        if (
            "country_id" in changes
            and changes["country_id"] is not None
            and await self.countries.get(changes["country_id"]) is None
        ):
            raise CountryNotFoundError(f"Country {changes['country_id']} does not exist.")
        for field, value in changes.items():
            setattr(author, field, value)
        await self.commit()
        return await self.get_author(author_id)

    async def delete_author(self, author_id: int) -> None:
        author = await self.get_author(author_id)
        await self.authors.delete(author)
        await self.commit()


class PublisherService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.publishers = PublisherRepository(session)

    async def list_publishers(
        self, *, offset: int, limit: int, q: str | None = None
    ) -> tuple[list[Publisher], int]:
        return await self.publishers.list_paginated(offset=offset, limit=limit, q=q)

    async def get_publisher(self, publisher_id: int) -> Publisher:
        publisher = await self.publishers.get(publisher_id)
        if publisher is None:
            raise PublisherNotFoundError(f"Publisher {publisher_id} does not exist.")
        return publisher

    async def create_publisher(self, data: PublisherCreate) -> Publisher:
        if await self.publishers.get_by_name(data.name):
            raise ConflictError(f"A publisher named '{data.name}' already exists.")
        publisher = Publisher(**data.model_dump())
        await self.publishers.add(publisher)
        await self.commit()
        return publisher

    async def update_publisher(self, publisher_id: int, data: PublisherUpdate) -> Publisher:
        publisher = await self.get_publisher(publisher_id)
        changes = data.model_dump(exclude_unset=True)
        if (
            "name" in changes
            and changes["name"] != publisher.name
            and await self.publishers.get_by_name(changes["name"])
        ):
            raise ConflictError(f"A publisher named '{changes['name']}' already exists.")
        for field, value in changes.items():
            setattr(publisher, field, value)
        await self.commit()
        return publisher

    async def delete_publisher(self, publisher_id: int) -> None:
        publisher = await self.get_publisher(publisher_id)
        await self.publishers.delete(publisher)
        await self.commit()
