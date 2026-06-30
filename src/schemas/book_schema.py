from pydantic import BaseModel


class BookCreate(BaseModel):

    isbn: str
    title: str
    author: str
    year: int
    summary: str
    publisher: str