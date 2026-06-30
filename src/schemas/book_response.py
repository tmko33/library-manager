# schemas/book_schema.py
from pydantic import BaseModel

class BookResponse(BaseModel):
    isbn: str
    title: str
    # No incluyes id ni copias aquí si no quieres que se vean