"""Country service."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, CountryNotFoundError
from app.models.country import Country
from app.repositories.country_repository import CountryRepository
from app.schemas.country import CountryCreate, CountryUpdate
from app.services.base import BaseService


class CountryService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.countries = CountryRepository(session)

    async def list_countries(
        self, *, offset: int, limit: int, q: str | None = None
    ) -> tuple[list[Country], int]:
        return await self.countries.list_paginated(offset=offset, limit=limit, q=q)

    async def get_country(self, country_id: int) -> Country:
        country = await self.countries.get(country_id)
        if country is None:
            raise CountryNotFoundError(f"Country {country_id} does not exist.")
        return country

    async def create_country(self, data: CountryCreate) -> Country:
        if await self.countries.get_by_name(data.name):
            raise ConflictError(f"A country named '{data.name}' already exists.")
        country = Country(**data.model_dump())
        await self.countries.add(country)
        await self.commit()
        return country

    async def update_country(self, country_id: int, data: CountryUpdate) -> Country:
        country = await self.get_country(country_id)
        changes = data.model_dump(exclude_unset=True)
        if (
            "name" in changes
            and changes["name"] != country.name
            and await self.countries.get_by_name(changes["name"])
        ):
            raise ConflictError(f"A country named '{changes['name']}' already exists.")
        for field, value in changes.items():
            setattr(country, field, value)
        await self.commit()
        return country

    async def delete_country(self, country_id: int) -> None:
        country = await self.get_country(country_id)
        await self.countries.delete(country)
        await self.commit()
