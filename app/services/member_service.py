"""Member service."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    DuplicateEmailError,
    MemberNotFoundError,
)
from app.core.security import hash_password
from app.models.member import Member, MemberRole
from app.repositories.member_repository import MemberRepository
from app.schemas.member import MemberCreate, MemberUpdate
from app.services.base import BaseService


class MemberService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.members = MemberRepository(session)

    async def list_members(
        self,
        *,
        offset: int,
        limit: int,
        q: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[Member], int]:
        return await self.members.list_paginated(
            offset=offset, limit=limit, q=q, is_active=is_active
        )

    async def get_member(self, member_id: int) -> Member:
        member = await self.members.get(member_id)
        if member is None:
            raise MemberNotFoundError(f"Member {member_id} does not exist.")
        return member

    async def create_member(
        self,
        data: MemberCreate,
        *,
        forced_role: MemberRole | None = None,
    ) -> Member:
        if await self.members.get_by_email(data.email):
            raise DuplicateEmailError(f"Email {data.email} is already registered.")

        payload = data.model_dump(exclude={"password"})
        payload["role"] = forced_role or data.role
        member = Member(**payload, hashed_password=hash_password(data.password))

        await self.members.add(member)
        await self.commit()
        return member

    async def update_member(self, member_id: int, data: MemberUpdate) -> Member:
        member = await self.get_member(member_id)
        changes = data.model_dump(exclude_unset=True)

        new_email = changes.get("email")
        if (
            new_email is not None
            and new_email.lower() != member.email.lower()
            and await self.members.get_by_email(new_email)
        ):
            raise DuplicateEmailError(f"Email {new_email} is already registered.")

        for field, value in changes.items():
            setattr(member, field, value)
        await self.commit()
        return member

    async def deactivate_member(self, member_id: int) -> Member:
        member = await self.get_member(member_id)
        member.is_active = False
        await self.commit()
        return member
