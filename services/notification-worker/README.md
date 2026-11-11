# commercelens-notification-worker
Node.js/TypeScript worker consumes durable RabbitMQ queue order.confirmed, calls an HTTP email provider, and stores delivery state in PostgreSQL. Default provider is an explicit local mock.

## Contract and guarantees

Event JSON: `{eventId,orderId,customerEmail,totalCents,trackingNumber}`. POST to provider /email with Idempotency-Key equal to eventId. Provider must return `{status:"sent"}` and durably deduplicate the key. Delivery is at-least-once; external delivery and message acknowledgments cannot be one atomic transaction.

Queue order.confirmed is durable with x-dead-letter-exchange empty and x-dead-letter-routing-key order.confirmed.dead. Producers must declare matching arguments and publish persistent messages. Dead queue is durable.

At most three persisted attempts, including interrupted attempts; 250ms/500ms backoff and 3-second HTTP deadline. Status sent is persisted before acknowledgment. Exhaustion persists status dead before rejecting to the dead-letter queue. Malformed/conflicting events are dead-lettered. PostgreSQL advisory locks serialize concurrent duplicate events. Sent redeliveries skip the provider. A crash between provider success and persistence relies on provider idempotency.

Email failure never rolls back confirmed orders. Manual replay of dead messages is not implemented.

## Operations

GET /health reports ready after DB initialization and RabbitMQ connection. GET /api/notifications returns latest 100 `{eventId,orderId,status,attempts,lastError}` rows.

Required DATABASE_URL; optional RABBITMQ_URL (amqp://guest:guest@rabbitmq:5672), EMAIL_PROVIDER_URL (http://mock-provider:8080), PROVIDER_TIMEOUT_MS (3000), PORT (8080).

`npm ci && npm test && npm run build`; Docker build also runs tests and compilation. Central CommerceLens Compose provides dependencies. Recipient fail-email@example.com triggers the mock failure path. Status API is unauthenticated and intended only for local/private demonstration.
