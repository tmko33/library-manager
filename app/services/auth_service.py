"""Authentication service."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import InactiveMemberError, InvalidCredentialsError
from app.core.security import create_access_token, verify_password
from app.models.member import Member, MemberRole
from app.repositories.member_repository import MemberRepository
from app.schemas.auth import Token
from app.schemas.member import MemberCreate
from app.services.base import BaseService
from app.services.member_service import MemberService


class AuthService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.members = MemberRepository(session)
        self.member_service = MemberService(session)

    async def register(self, data: MemberCreate) -> Member:
        """Public self-registration always creates a plain member account."""
        return await self.member_service.create_member(data, forced_role=MemberRole.MEMBER)

    async def authenticate(self, email: str, password: str) -> Member:
        member = await self.members.get_by_email(email)
        if member is None or not verify_password(password, member.hashed_password):
            raise InvalidCredentialsError("Incorrect email or password.")
        if not member.is_active:
            raise InactiveMemberError("This account has been deactivated.")
        return member

    def issue_token(self, member: Member) -> Token:
        token = create_access_token(
            member.id,
            extra_claims={"role": member.role.value, "email": member.email},
        )
        return Token(
            access_token=token,
            expires_in=settings.access_token_expire_minutes * 60,
        )
