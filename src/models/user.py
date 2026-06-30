from dataclasses import dataclass
from models.book_copy import BookCopy 


@dataclass
class User:

    id: int
    name : str
    address : str
    email : str
    phone : str