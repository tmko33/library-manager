from dataclasses import dataclass
from models.user import User
from models.book_copy import BookCopy 

@dataclass
class Loan:

    id: int
    loan_date: date
    due_date : date
    user: User
    copy: BookCopy
    returned : bool = False

    def get_book_copy(self) -> BookCopy:
        return self.copy