"""Reusable FastAPI dependencies."""

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.pagination import PageParams, pagination_params
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.member import Member, MemberRole
from app.repositories.member_repository import MemberRepository

SessionDep = Annotated[AsyncSession, Depends(get_db)]
PageDep = Annotated[PageParams, Depends(pagination_params)]

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_v1_prefix}/auth/login",
    auto_error=True,
)


async def get_current_member(
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> Member:
    """Resolve the authenticated member from the bearer token."""
    payload = decode_access_token(token)
    subject = payload.get("sub")
    if subject is None:
        raise UnauthorizedError("The access token is missing the subject claim.")
    try:
        member_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise UnauthorizedError("The access token subject is invalid.") from exc

    member = await MemberRepository(session).get(member_id)
    if member is None or not member.is_active:
        raise UnauthorizedError("The member no longer exists or was deactivated.")
    return member


CurrentMember = Annotated[Member, Depends(get_current_member)]


def require_roles(*roles: MemberRole) -> Callable[..., Awaitable[Member]]:
    """Build a dependency that allows only the given roles."""

    async def checker(current: CurrentMember) -> Member:
        if current.role not in roles:
            allowed = ", ".join(role.value for role in roles)
            raise ForbiddenError(f"This action requires one of these roles: {allowed}.")
        return current

    return checker


StaffMember = Annotated[Member, Depends(require_roles(MemberRole.ADMIN, MemberRole.LIBRARIAN))]
AdminMember = Annotated[Member, Depends(require_roles(MemberRole.ADMIN))]


def is_staff(member: Member) -> bool:
    return member.role in (MemberRole.ADMIN, MemberRole.LIBRARIAN)
