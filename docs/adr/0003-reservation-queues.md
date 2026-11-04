# ADR 0003 — FIFO reservation queues with expiring holds

## Status

Accepted.

## Context

Multiple members may want the same title while every copy is on loan. A first
come, first served policy is expected by users and is easy to reason about, but
an unattended hold can block a copy forever.

## Decision

- Reservations are stored per `(member, book)` with status `pending`.
- The queue is ordered by `created_at, id`.
- While a pending reservation exists, only the first member in the queue may
  borrow the title.
- When a copy is returned, the first pending reservation receives an
  `expires_at` of `today + RESERVATION_HOLD_DAYS`.
- Expired holds move to `expired`, releasing the priority.

## Consequences

- Fair allocation without a background scheduler.
- Stale holds cannot block the catalogue indefinitely.
- A periodic job can still call the maintenance endpoints to expire holds
  proactively.
