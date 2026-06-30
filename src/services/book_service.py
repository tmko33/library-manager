from models.book import Book
from models.book_copy import BookCopy
from exceptions.book_not_found import BookNotFoundError

class BookService:
    def __init__(self):
        self.books: list[Book] = []
        self._counter = 0


    def create_book(self, isbn, title, author, year, summary, publisher) -> Book:
        self._counter += 1
        new_book = Book(self._counter, isbn, title, author, [author], [], year, summary, publisher)
        self.books.append(new_book)
        
        return new_book


    def find_by_isbn(self, isbn: str) -> Book:
        for book in self.books:
            if(book.isbn == isbn):
                return book
        
        raise BookNotFoundError(f"The book {isbn} is not found.")

    def get_all_books(self):
        return self.books