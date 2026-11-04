# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project adheres to [Semantic Versioning](https://semver.org/).

### Fixed

- Container entrypoint now applies migrations and honours the platform `$PORT`
  (fixes Render deployments with a custom `dockerCommand`).
- Mermaid architecture diagram renders correctly on GitHub.

## [0.1.0] - 2026-11-04

### Added

- Layered FastAPI application (routers → services → repositories).
- SQLAlchemy 2.0 async models for countries, authors, publishers, books,
  copies, branches, members, loans, reservations and fines.
- Alembic migrations and a demo seed script.
- JWT authentication with `admin`, `librarian` and `member` roles.
- Lending workflow with transactional copy assignment, renewals, overdue
  detection and automatic fines.
- FIFO reservation queue with expiring holds.
- Pagination, filtering and sorting on every collection.
- RFC 7807 error responses with stable error codes.
- Request correlation (`X-Request-ID`), access logs, Prometheus metrics and
  readiness probes.
- Maintenance job for overdue loans and expired holds.
- Integration test suite (57 tests, 90% coverage), ruff, mypy and GitHub Actions.
- Docker multi-stage image, Docker Compose stack and a Render blueprint.
