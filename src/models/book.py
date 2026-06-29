# models/book.py
from dataclasses import dataclass, field
from models.author import Author
from models.book_copy import BookCopy


@dataclass
class Book:
    isbn: str
    title: str
    author: list[Author]
    year: int
    code: int
    summary: str
    publisher: str
    bookCopies: list[BookCopy] = field(init=False) 

    def __post_init__(self):
        # Generamos 5 copias: el ID será 1-5, y el ISBN el del libro
        self.bookCopies = [BookCopy(i, self.isbn) for i in range(1, 6)]

    def get_isbn(self) -> str:
        return self.isbn

    def get_copies(self) -> list[BookCopy]:
        return self.bookCopies