# Files

- [Delivery and Retry Logic](delivery-retry.md) - Deep dive into the deliver() function in src/delivery.ts, covering attempt budgeting, backoff timing, idempotency via eventId, prior-attempt preservation, and terminal dead status.
- [Connection and Session Lifecycle](lifecycle.md) - Reconnect loop, session watcher, channel and connection event handling, ready-state management, and graceful shutdown semantics that keep the notification worker resilient to broker and database failures.
