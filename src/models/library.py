from dataclasses import dataclass, field
from datetime import date, timedelta
from models.book import Book
from models.user import User
from models.loan import Loan
from exceptions.book_not_found import BookNotFoundError
from exceptions.duplicate_book import duplicateBook


@dataclass
class Library:
    """
    Represents the system of the library.
    """

    books: list[Book] = field(default_factory=list)
    users : list[User] = field(default_factory=list)
    loans : list[Loans] = field(default_factory=list)
    loans_id : int = 0
    book_id : int = 0
    users_id : int = 0


    def create_book(self, isbn: str, title: str, author: Author, year: str, summary: str, publisher: str)  -> Book:
        n_book = Book(self.book_id, isbn, title, author, year, summary, publisher)
        self.book_id += 1

        return n_book

    
    def add_book(self, book: Book) -> None:
        if(self.exists_book(book.isbn)):
            raise DuplicateBookError(...)

        self.books.append(book)


    def add_copy(self, isbn: str, quantity: int) -> None:
        book = self.find_book_by_isbn(isbn)
        if(len(book.copies) > 0):
            copy_id = book.copies[-1].id + 1
        else:
            copy_id = len(book.copies)
        for i in range(quantity):
            n_copy = BookCopy(copy_id, isbn)
            book.copies.append(n_copy)
            copy_id += 1


    def exists_book(self, isbn: str) -> bool:
        return any(book.isbn == isbn for book in self.books)

    def list_books(self) -> list[Book]:
        return self.books
    

    def list_users(self) -> list[User]:
        return self.users


    def list_loans(self) -> list[Loan]:
        return self.loans


    def find_book_by_isbn(self, isbn: str) -> Book:
        if(isbn == ""):
            raise Exception(

            )

        for book in self.books:
            if(book.isbn == isbn):
                return book

        raise BookNotFoundError(
            f"Book with ISBN {isbn} not found."
        )


    def remove_book(self, isbn: str) -> str:
        if(isbn == ""):
            raise Exception(

            )
        book = self.find_book_by_isbn(isbn)
        self.books.remove(book)


    def search_user_id(self, user_id) -> User:
        for user in self.users:
            if(user.id == user_id):
                return user
        
        raise UserNotFoundError(

        )


    def add_user(self, name: str, address: str, email: str, phone: str) -> User:
        n_user = User(self.users_id, name, address, email, phone)
        for user in self.users:
            if(user == n_user):
                raise UserAlreadyInSystem(

                )
        self.users.append(n_user)
        
        self.users_id += 1
        return n_user


    def check_availability(self, copy: BookCopy) -> bool:
        available = True
        for loan in self.loans:
            if(loan.book_copy == copy):
                available = False
                break
        return available


    def borrow_book(self, user_id: int, isbn: str) -> Loan:            
        user = self.search_user_id(user_id)
        book = self.find_book_by_isbn(isbn)
        
        target_copy = None
        for copy in book.copies:
            if(self.check_availability(copy)):
                target_copy = copy
                break
        
        if(not target_copy):
            raise NoBookCopiesAvailable(
                "There are not available copies for this book."
                )

        self.loans_id += 1
        loan_date = date.today()
        due_date = loan_date + timedelta(days=7)
        
        loan = Loan(self.loans_id, loan_date, due_date, user, target_copy)
        
        self.loans.append(loan)
        return loan