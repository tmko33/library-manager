from models import Book, Library, Author, Country

def main():
    country1 = Country("Colombia")
    author1 = Author(1, 1999, "Robert", [country1])
    book1 = Book("0", "1984", [author1], 3333, 1, "hi", "LOL")
    book2 = Book("1", "guasaa", [author1], 1111, 2, "hello", "zamn")
    library = Library()
    library.add_book(book1)
    library.add_book(book2)
    print(library.list_books())

    print(library.find_book_by_isbn("0"))
    print(library.remove_book("0"))
    print(library.add_user("phanor", "nolose", "albertguasa", "315655154"))
    print(library.list_users())
    print(library.borrow_book(0, "1"))
    print(library.list_loans())

main()
    