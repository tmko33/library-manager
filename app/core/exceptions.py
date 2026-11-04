"""Domain and application exceptions.

Every exception raised by the application inherits from :class:`AppError` so
that a single handler can turn it into an RFC 7807 ``problem+json`` response.
"""

from typing import Any


class AppError(Exception):
    """Base class for all expected application errors."""

    status_code: int = 400
    code: str = "application_error"
    title: str = "Application error"

    def __init__(
        self,
        detail: str,
        *,
        code: str | None = None,
        status_code: int | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(detail)
        self.detail = detail
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code
        self.extra = extra or {}


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"
    title = "Resource not found"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"
    title = "Resource conflict"


class UnauthorizedError(AppError):
    status_code = 401
    code = "unauthorized"
    title = "Not authenticated"


class ForbiddenError(AppError):
    status_code = 403
    code = "forbidden"
    title = "Operation not allowed"


class BusinessRuleError(AppError):
    status_code = 422
    code = "business_rule_violated"
    title = "Business rule violated"


# --------------------------------------------------------------------------- #
# Domain-specific errors
# --------------------------------------------------------------------------- #
class BookNotFoundError(NotFoundError):
    code = "book_not_found"
    title = "Book not found"


class AuthorNotFoundError(NotFoundError):
    code = "author_not_found"
    title = "Author not found"


class PublisherNotFoundError(NotFoundError):
    code = "publisher_not_found"
    title = "Publisher not found"


class CountryNotFoundError(NotFoundError):
    code = "country_not_found"
    title = "Country not found"


class BranchNotFoundError(NotFoundError):
    code = "branch_not_found"
    title = "Branch not found"


class CopyNotFoundError(NotFoundError):
    code = "copy_not_found"
    title = "Book copy not found"


class MemberNotFoundError(NotFoundError):
    code = "member_not_found"
    title = "Member not found"


class LoanNotFoundError(NotFoundError):
    code = "loan_not_found"
    title = "Loan not found"


class ReservationNotFoundError(NotFoundError):
    code = "reservation_not_found"
    title = "Reservation not found"


class FineNotFoundError(NotFoundError):
    code = "fine_not_found"
    title = "Fine not found"


class DuplicateISBNError(ConflictError):
    code = "duplicate_isbn"
    title = "Duplicate ISBN"


class DuplicateEmailError(ConflictError):
    code = "duplicate_email"
    title = "Duplicate email"


class DuplicateInventoryCodeError(ConflictError):
    code = "duplicate_inventory_code"
    title = "Duplicate inventory code"


class NoCopiesAvailableError(ConflictError):
    code = "no_copies_available"
    title = "No copies available"


class InvalidCredentialsError(UnauthorizedError):
    code = "invalid_credentials"
    title = "Invalid credentials"


class InactiveMemberError(ForbiddenError):
    code = "inactive_member"
    title = "Inactive member"


class LoanLimitReachedError(BusinessRuleError):
    code = "loan_limit_reached"
    title = "Loan limit reached"


class HasOverdueLoansError(BusinessRuleError):
    code = "has_overdue_loans"
    title = "Member has overdue loans"


class HasUnpaidFinesError(BusinessRuleError):
    code = "has_unpaid_fines"
    title = "Member has unpaid fines"


class CopyNotAvailableError(BusinessRuleError):
    code = "copy_not_available"
    title = "Copy not available"


class LoanAlreadyReturnedError(BusinessRuleError):
    code = "loan_already_returned"
    title = "Loan already returned"


class RenewalLimitReachedError(BusinessRuleError):
    code = "renewal_limit_reached"
    title = "Renewal limit reached"


class ReservationLimitReachedError(BusinessRuleError):
    code = "reservation_limit_reached"
    title = "Reservation limit reached"
