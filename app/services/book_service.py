"""Book service."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AuthorNotFoundError,
    BookNotFoundError,
    BusinessRuleError,
    DuplicateISBNError,
    PublisherNotFoundError,
)
from app.models.author import Author
from app.models.book import Book
from app.repositories.author_repository import AuthorRepository
from app.repositories.book_repository import BookRepository, SortField
from app.repositories.copy_repository import CopyRepository
from app.repositories.publisher_repository import PublisherRepository
from app.schemas.book import BookCreate, BookUpdate
from app.services.base import BaseService


class BookService(BaseService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.books = BookRepository(session)
        self.authors = AuthorRepository(session)
        self.publishers = PublisherRepository(session)
        self.copies = CopyRepository(session)

    async def list_books(
        self,
        *,
        offset: int,
        limit: int,
        q: str | None = None,
        author_id: int | None = None,
        publisher_id: int | None = None,
        year: int | None = None,
        available: bool | None = None,
        sort: SortField = "title",
        order: str = "asc",
    ) -> tuple[list[Book], int]:
        ordering = "desc" if order == "desc" else "asc"
        return await self.books.list_paginated(
            offset=offset,
            limit=limit,
            q=q,
            author_id=author_id,
            publisher_id=publisher_id,
            year=year,
            available=available,
            sort=sort,
            order=ordering,  # type: ignore[arg-type]
        )

    async def get_book(self, book_id: int) -> Book:
        book = await self.books.get_detailed(book_id)
        if book is None:
            raise BookNotFoundError(f"Book {book_id} does not exist.")
        return book

    async def create_book(self, data: BookCreate) -> Book:
        if await self.books.get_by_isbn(data.isbn):
            raise DuplicateISBNError(f"A book with ISBN {data.isbn} already exists.")
        if data.publisher_id is not None and await self.publishers.get(data.publisher_id) is None:
            raise PublisherNotFoundError(f"Publisher {data.publisher_id} does not exist.")

        authors = await self._load_authors(data.author_ids)
        book = Book(**data.model_dump(exclude={"author_ids"}))
        book.authors = authors

        await self.books.add(book)
        await self.commit()
        return await self.get_book(book.id)

    async def update_book(self, book_id: int, data: BookUpdate) -> Book:
        book = await self.get_book(book_id)
        changes = data.model_dump(exclude_unset=True)
        author_ids = changes.pop("author_ids", None)

        new_isbn = changes.get("isbn")
        if new_isbn is not None and new_isbn != book.isbn:
            existing = await self.books.get_by_isbn(new_isbn)
            if existing is not None and existing.id != book.id:
                raise DuplicateISBNError(f"A book with ISBN {new_isbn} already exists.")

        new_publisher_id = changes.get("publisher_id")
        if new_publisher_id is not None and await self.publishers.get(new_publisher_id) is None:
            raise PublisherNotFoundError(f"Publisher {new_publisher_id} does not exist.")

        for field, value in changes.items():
            setattr(book, field, value)

        if author_ids is not None:
            book.authors = await self._load_authors(author_ids)

        await self.commit()
        return await self.get_book(book_id)

    async def delete_book(self, book_id: int) -> None:
        book = await self.get_book(book_id)
        for copy in book.copies:
            if await self.copies.has_active_loan(copy.id):
                raise BusinessRuleError(
                    "Cannot delete a book that has active loans.",
                    code="book_has_active_loans",
                    status_code=409,
                )
        await self.books.delete(book)
        await self.commit()

    async def _load_authors(self, author_ids: list[int]) -> list[Author]:
        unique_ids = list(dict.fromkeys(author_ids))
        authors = await self.authors.get_many(unique_ids)
        found = {author.id for author in authors}
        missing = [author_id for author_id in unique_ids if author_id not in found]
        if missing:
            raise AuthorNotFoundError(f"Authors not found: {missing}")
        return list(authors)
