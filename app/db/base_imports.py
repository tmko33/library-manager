"""Convenience imports for Alembic autogenerate and tests."""

from app.db.base import Base
from app.models.associations import book_authors
from app.models.author import Author
from app.models.book import Book
from app.models.book_copy import BookCopy
from app.models.branch import Branch
from app.models.country import Country
from app.models.fine import Fine
from app.models.loan import Loan
from app.models.member import Member
from app.models.publisher import Publisher
from app.models.reservation import Reservation

__all__ = [
    "Author",
    "Base",
    "Book",
    "BookCopy",
    "Branch",
    "Country",
    "Fine",
    "Loan",
    "Member",
    "Publisher",
    "Reservation",
    "book_authors",
]
