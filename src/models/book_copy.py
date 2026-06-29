@dataclass
class BookCopy:
    """
    Represents a copy of the book from the library.
    """
    id: int
    code: str
    available: bool

    def borrow_book(self):
        if(not self.available):
            raise Exception(
                "Error, Not Available"
            )
        self.available = False
    
    def return_book(self):
        if(not self.available):
            raise Exception(
                "Error, The Book its Already Available"
            )

        self.available = True
    
