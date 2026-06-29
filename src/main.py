from models import Book, Library, Author, Country

def main():
    country1 = Country("Colombia")
    author1 = Author(1, 1999, "Robert", [country1])
    book1 = Book(1, "1984", [author1], 3333, 1, "hi", "LOL")
    book2 = Book(1, "guasaa", [author1], 1111, 2, "hello", "zamn")
    library = Library()
    library.add_book(book1)
    library.add_book(book2)
    print(library.list_books())


main()
    