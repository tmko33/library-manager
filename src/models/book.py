# models/book.py
from dataclasses import dataclass
from models.author import Author

@dataclass
class Book:
    isbn: str
    title: str
    author: list[Author]
    year: int
    code: int
    summary: str
    publisher: str