from dataclasses import dataclass, field
from models.book import Book

@dataclass
class Library:
    """
    Represents the system of the library.
    """

    books: list[Book] = field(default_factory=list)

    def add_book(self, book: Book) -> None:
        self.books.append(book)

    def list_books(self) -> list[Book]:
        return self.books