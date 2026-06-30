from fastapi import FastAPI

from services.book_service import BookService

from schemas.book_schema import BookCreate


app = FastAPI()

book_service = BookService()

@app.get("/books", response_model=list[BookResponse])
def get_books():
    return book_service.get_all_books()


@app.post("/books")
def create_book(book: BookCreate):
    # BookCreate solo tiene lo que el usuario envió (isbn, title, etc.)
    # El ID y la lista de copias se generan dentro del servicio
    new_book = book_service.create_book(
        isbn=book.isbn,
        title=book.title,
        author=book.author,
        year=book.year,
        summary=book.summary,
        publisher=book.publisher
    )
    return new_book