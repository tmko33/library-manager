from dataclasses import dataclass, field


@dataclass
class BookCopy:
    """
    Represents a copy of the book from the library.
    """
    id: int
    isbn: str
    
    def get_isbn(self) -> str:
        return self.isbn