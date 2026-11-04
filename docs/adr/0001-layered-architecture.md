# ADR 0001 — Layered architecture

## Status

Accepted.

## Context

The project started as a single `Library` aggregate that owned every operation
(add books, register users, compute availability, create loans). This worked for
an in-memory prototype but mixed persistence concerns, business rules and
presentation in one class. It also duplicated logic once FastAPI services were
introduced.

## Decision

Adopt a four-layer architecture:

```text
router  →  service  →  repository  →  database
```

- **Routers** parse HTTP input, enforce authorization and shape responses.
- **Services** own transactions and business rules. They never know about HTTP.
- **Repositories** contain SQL queries and eager-loading strategies.
- **Models** describe persistence; **schemas** describe the API contract.

Dependencies point inwards only: a repository never imports a service, and a
service never imports FastAPI.

## Consequences

- Business rules are testable without spinning up the HTTP layer.
- Query performance is tuned in a single place per aggregate.
- More files per feature, but each with a single responsibility.
