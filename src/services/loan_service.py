from datetime import date, timedelta
from models.loan import Loan
from exceptions.no_copies import NoBookCopiesAvailable


class LoanService:
    def __init__(self, book_service, user_service):
        self.book_service = book_service
        self.user_service = user_service
        self.loans: list[Loan] = []
        self._counter = 0


    def borrow_book(self, user_id: int, isbn: str) -> Loan:
        # 1. Obtener entidades validadas
        user = self.user_service.find_by_id(user_id)
        book = self.book_service.find_by_isbn(isbn)
        
        # 2. Buscar una copia que NO esté en la lista de préstamos activos
        target_copy = None
        for copy in book.copies:
            if(self._is_copy_available(copy)):
                target_copy = copy
                break
        
        if(not target_copy):
            raise NoBookCopiesAvailable(f"No hay copias disponibles del libro {isbn}")

        # 3. Crear el préstamo
        self._counter += 1
        loan_date = date.today()
        due_date = loan_date + timedelta(days=7)
        
        loan = Loan(self._counter, loan_date, due_date, user, target_copy)
        
        # 4. Persistir
        self.loans.append(loan)
        return loan


    def _is_copy_available(self, copy) -> bool:
        """ Método privado de ayuda para verificar disponibilidad """
        for loan in self.loans:
            # Si el préstamo está activo (returned es False) y la copia es la misma
            if((loan.copy.id == copy.id) and (not loan.returned)):
                return False
        return True


    def return_book(self, loan_id: int) -> None:
        """ Lógica para devolver un libro y marcarlo como disponible """
        for loan in self.loans:
            if(loan.id == loan_id):
                loan.returned = True
                return
        raise Exception("Préstamo no encontrado")