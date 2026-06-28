@dataclass
class BookCopy:
    """
    Represents a copy of the book from the library.
    """

    def __init__(self, id, code, available=True):
        self.id = id
        self.code = code
        self.available = available

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
    
