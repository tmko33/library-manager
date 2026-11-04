# ADR 0004 — JWT authentication with role-based authorization

## Status

Accepted.

## Context

The library has three kinds of users with different permissions:

- **Members** borrow books and manage their own loans, reservations and fines.
- **Librarians** manage the catalogue, copies and members.
- **Admins** additionally manage staff accounts and waive fines.

The API is consumed by a future SPA and by operators, so it must be stateless
and easy to consume from JavaScript.

## Decision

- Authenticate with **OAuth2 password flow** and issue signed **JWTs** (`HS256`).
- Store only argon2 password hashes; never store or log plaintext passwords.
- Encode `sub`, `role` and `email` in the token; validate the member on every
  request so deactivation takes effect immediately.
- Enforce authorization with FastAPI dependencies: `CurrentMember`,
  `StaffMember` and `AdminMember`.
- Scope collection endpoints for plain members (`member_id` is forced to the
  authenticated member), so a member cannot read another member's data.

## Consequences

- Horizontal scaling works without server-side sessions.
- Tokens cannot be revoked individually before expiry; deactivation is enforced
  by the per-request database lookup, which mitigates the most important case.
- Role checks live in one place (`app/api/deps.py`) and are easy to audit.
