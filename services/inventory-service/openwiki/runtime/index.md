# Files

- [Release Flow — End-to-End](release-flow.md) - Complete release workflow and idempotency guarantees. Covers the POST /api/reservations/{id}/release handler, transactional stock restoration, and the no-compensation design.
- [Reservation Flow — End-to-End](reservation-flow.md) - Complete reserve workflow from HTTP handler to committed transaction, including validation, locking, stock decrement, and failure behavior.
