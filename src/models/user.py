from dataclasses import dataclass
from models.book_copy import BookCopy 


@dataclass
class User:

    id: int
    name : str
    address : str
    email : str
    phone : str

    def get_id(self) -> int:
        return self.id

    def get_name(self) -> str:
        return self.name

    def get_address(self) -> str:
        return self.address

    def get_email(self) -> str:
        return self.email

    def get_phone(self) -> str:
        return self.phone
