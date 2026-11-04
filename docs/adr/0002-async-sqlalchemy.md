# ADR 0002 — Async SQLAlchemy 2.0 and PostgreSQL

## Status

Accepted.

## Context

FastAPI is an ASGI framework; blocking database calls inside request handlers
would tie up the event loop and cap throughput. The library domain also needs
row-level guarantees to avoid lending the same physical copy twice.

## Decision

- Use **SQLAlchemy 2.0** with the asyncio extension and `asyncpg`.
- Use **PostgreSQL 16** in development, tests and production for parity.
- Manage schema changes with **Alembic**; never create tables at runtime.
- Acquire copies for lending with `SELECT … FOR UPDATE SKIP LOCKED`.

## Consequences

- Concurrency-safe lending without application-level locks.
- Tests run against the same engine as production, catching dialect issues early.
- The stack is harder to bootstrap than SQLite, so `docker compose` is the
  documented entry point.
