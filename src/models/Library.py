from models.book import Book

@dataclass
class Library:
    def __init__(self):
        self.books: list[Book] = []

    def add_book(self, book: Book) -> None:
        self.books.append(book)

    def list_books(self) -> list[Book]:
        return self.books