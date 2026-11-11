# Files

- [HTTP API Surface and Idempotency](api-surface.md) - Endpoint-by-endpoint reference for the REST API exposed by OrderController, including request and response schemas, status codes, exception handling, and the idempotency mechanism with request hashing.
- [Checkout Saga](checkout-saga.md) - Deep documentation of the Checkout saga state machine, Ports interface, intermediate-state checkpointing, and cross-community HTTP bridge. Explains why uncertain payment outcomes stay in payment_unknown and how crash safety is achieved.
- [Data Model and Persistence](data-model.md) - Database schema, entity design, JSONB storage strategy, and the outbox table for the orders service. Explains how OrderStore maps the Checkout.Order object to PostgreSQL JSONB and maintains idempotency and state durability.
- [Outbox Publishing and Messaging](outbox-publishing.md) - RabbitMQ outbox pattern implementation using an OutboxPublisher component with queue declarations, publisher confirms, dead-letter exchange, scheduled polling, and at-least-once delivery semantics for confirmed order events.
