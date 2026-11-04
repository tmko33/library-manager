"""Member entity (library user and staff)."""

from datetime import date
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Date, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.loan import Loan
    from app.models.reservation import Reservation


class MemberRole(StrEnum):
    """Roles used for authorization."""

    ADMIN = "admin"
    LIBRARIAN = "librarian"
    MEMBER = "member"


member_role_enum = SAEnum(
    MemberRole,
    name="member_role",
    native_enum=False,
    length=20,
    values_callable=lambda enum: [member.value for member in enum],
)


class Member(Base, TimestampMixin):
    """A registered library user.

    Members with the ``librarian`` or ``admin`` role can manage the catalogue
    and other members. Plain ``member`` users can only borrow books.
    """

    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(150), index=True)
    phone: Mapped[str | None] = mapped_column(String(30))
    address: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[MemberRole] = mapped_column(member_role_enum, default=MemberRole.MEMBER)
    is_active: Mapped[bool] = mapped_column(default=True)
    membership_expires_at: Mapped[date | None] = mapped_column(Date)

    loans: Mapped[list["Loan"]] = relationship(
        back_populates="member",
        foreign_keys="Loan.member_id",
    )
    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="member",
        cascade="all, delete-orphan",
    )
