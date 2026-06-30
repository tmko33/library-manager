# models/book.py
from dataclasses import dataclass, field
from models.author import Author
from models.book_copy import BookCopy


@dataclass
class Book:
    id: int
    isbn: str
    title: str
    author: list[Author]
    year: str
    summary: str
    publisher: str
    copies: list[BookCopy] = field(init=False) 

    # def __post_init__(self):
    #     # Generamos 5 copias: el ID será 1-5, y el ISBN el del libro
    #     self.bookCopies = [BookCopy(i, self.isbn) for i in range(1, 6)]
