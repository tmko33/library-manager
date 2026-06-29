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


    def add_book(self, book: Book) -> None:
        try:
            # Si el libro ya existe, lanzará la excepción y entraremos al 'except'
            self.find_book_by_isbn(book.isbn)
            raise DuplicateBookError("Book already in the library")
        except BookNotFoundError:
            # Si no existe (da error), es justo lo que queremos para poder agregarlo
            self.books.append(book)


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
            if(book.get_isbn() == isbn):
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
        return "The Book has been removed"


    def search_user_id(self, user_id) -> User:

        for user in self.users:
            if(user.get_id() == user_id):
                return user
        
        raise UserNotFoundError(

        )


    def add_user(self, name: str, address: str, email: str, phone: str) -> str:
        n_user = User(self.users_id, name, address, email, phone)
        for user in self.users:
            if(user == n_user):
                raise UserAlreadyInSystem(

                )
        self.users.append(n_user)
        
        return "The user has been added"


    def check_availability(self, book_isbn: str) -> bool:
        available = True
        for loan in self.loans:
            if(loan.get_book_copy().get_isbn() == book_isbn):
                available = False
        return available

    def borrow_book(self, user_id: int, isbn: str) -> Loan:
            
        user = self.search_user_id(user_id)
        book = self.find_book_by_isbn(isbn)
        
        target_copy = None
        for copy in book.get_copies():
            if(self.check_availability(copy.get_isbn())):
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