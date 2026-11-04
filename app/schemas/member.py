"""Member schemas."""

from datetime import date, datetime

from pydantic import EmailStr, Field

from app.models.member import MemberRole
from app.schemas.common import ORMBase


class MemberBase(ORMBase):
    email: EmailStr = Field(examples=["ana@example.com"])
    full_name: str = Field(min_length=2, max_length=150, examples=["Ana Torres"])
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=255)


class MemberCreate(MemberBase):
    password: str = Field(min_length=8, max_length=128)
    role: MemberRole = MemberRole.MEMBER
    membership_expires_at: date | None = None


class MemberUpdate(ORMBase):
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=255)
    role: MemberRole | None = None
    is_active: bool | None = None
    membership_expires_at: date | None = None


class MemberBrief(ORMBase):
    id: int
    full_name: str
    email: EmailStr


class MemberRead(MemberBase):
    id: int
    role: MemberRole
    is_active: bool
    membership_expires_at: date | None = None
    created_at: datetime
