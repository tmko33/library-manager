"""Branch service."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BranchNotFoundError, ConflictError, CountryNotFoundError
from app.models.branch import Branch
from app.repositories.branch_repository import BranchRepository
from app.repositories.country_repository import CountryRepository
from app.schemas.branch import BranchCreate, BranchUpdate
from app.services.base import BaseService


class BranchService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.branches = BranchRepository(session)
        self.countries = CountryRepository(session)

    async def list_branches(
        self,
        *,
        offset: int,
        limit: int,
        q: str | None = None,
        city: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[Branch], int]:
        return await self.branches.list_paginated(
            offset=offset, limit=limit, q=q, city=city, is_active=is_active
        )

    async def get_branch(self, branch_id: int) -> Branch:
        branch = await self.branches.get_detailed(branch_id)
        if branch is None:
            raise BranchNotFoundError(f"Branch {branch_id} does not exist.")
        return branch

    async def create_branch(self, data: BranchCreate) -> Branch:
        if await self.branches.get_by_name(data.name):
            raise ConflictError(f"A branch named '{data.name}' already exists.")
        if data.country_id is not None and await self.countries.get(data.country_id) is None:
            raise CountryNotFoundError(f"Country {data.country_id} does not exist.")
        branch = Branch(**data.model_dump())
        await self.branches.add(branch)
        await self.commit()
        return await self.get_branch(branch.id)

    async def update_branch(self, branch_id: int, data: BranchUpdate) -> Branch:
        branch = await self.get_branch(branch_id)
        changes = data.model_dump(exclude_unset=True)
        if (
            "name" in changes
            and changes["name"] != branch.name
            and await self.branches.get_by_name(changes["name"])
        ):
            raise ConflictError(f"A branch named '{changes['name']}' already exists.")
        if (
            changes.get("country_id") is not None
            and await self.countries.get(changes["country_id"]) is None
        ):
            raise CountryNotFoundError(f"Country {changes['country_id']} does not exist.")
        for field, value in changes.items():
            setattr(branch, field, value)
        await self.commit()
        return await self.get_branch(branch_id)

    async def delete_branch(self, branch_id: int) -> None:
        branch = await self.get_branch(branch_id)
        await self.branches.delete(branch)
        await self.commit()
