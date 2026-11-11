# CommerceLens Order Service

Java 21 / Spring Boot checkout coordinator, PostgreSQL persistence and RabbitMQ durable outbox. Port 8080. This is a local demonstration service without authentication; expose through the loopback-bound central portal only.

## API

- `GET /health`: database readiness.
- `GET /api/products`: inventory catalog proxy.
- `GET /api/orders`: latest 200 orders, newest first.
- `GET /api/orders/{id}`: persisted order details.
- `POST /api/orders`: requires `Idempotency-Key` (letters/numbers/hyphens/underscores, max 100).

```json
{"customerEmail":"customer@example.com","postalCode":"10001","items":[{"sku":"BOOK-001","quantity":1}],"paymentScenario":"success","shippingScenario":"success"}
```

Prices come from inventory; shipping is fixed at 500 USD cents in this MVP. Successful checkout returns 201 and a full order. Failures return the persisted order including id, status and failureReason. Reusing a key with different input returns 409; identical completed requests return the original outcome without external calls. Requests already in progress return their latest persisted state and HTTP 409.

## Dependency flow

1. Persist pending order/idempotency key.
2. Reserve inventory through `INVENTORY_URL`.
3. Persist payment uncertainty, authorize through `PAYMENT_URL`.
4. Create shipment through `SHIPPING_URL`.
5. Atomically persist confirmed order and notification outbox event.
6. Background publisher sends durable `order.confirmed` messages with publisher confirms.

Definite payment declines release stock. Other payment responses, including conflict/transport errors/5xx, retain the reservation and mark `payment_unknown`: the provider may already have charged. Definite shipment rejections (4xx) refund and release; failed compensation becomes `manual_review`. Shipment timeouts/5xx are also manual review because the carrier may have accepted the request. External HTTP calls have an 8-second deadline and 2-second connection timeout; the coordinator does not retry financial effects blindly.

Intermediate states are durable. A process crash can leave pending/reserved/paid/payment_unknown records: they intentionally block replay and require operator reconciliation. This MVP does not implement an automated reconciliation or reservation-expiry job. Compensation failures likewise require inspection. Do not treat this as production-ready financial software.

## Configuration

- `SPRING_DATASOURCE_URL`: JDBC PostgreSQL URL, e.g. jdbc:postgresql://postgres:5432/orders.
- `SPRING_DATASOURCE_USERNAME`, `SPRING_DATASOURCE_PASSWORD`.
- `INVENTORY_URL`, `PAYMENT_URL`, `SHIPPING_URL`: base HTTP URLs without trailing slash.
- `SPRING_RABBITMQ_HOST`, `SPRING_RABBITMQ_PORT`, `SPRING_RABBITMQ_USERNAME`, `SPRING_RABBITMQ_PASSWORD`.

Aliases ORDER_DATABASE_URL/USER/PASSWORD and RABBITMQ_HOST/PORT/USER/PASSWORD also exist for local configuration. Spring standard environment names take precedence. Defaults are local demonstration values only.

Queue `order.confirmed` uses the default exchange, durable messages, DLX `""`, dead-letter routing key `order.confirmed.dead`. The dead queue is durable. Outbox delivery is at least once; consumers must deduplicate eventId. Broker outages leave orders confirmed and outbox events pending. A later publisher poll retries delivery.

## Run and test

Use the central [CommerceLens](https://github.com/nagv/CommerceLens) Compose project. `docker build -t commercelens-orders .` compiles and runs tests. `mvn verify` runs checkout behavior tests. Configure TEST_JDBC_URL, TEST_DB_USER and TEST_DB_PASSWORD against a disposable PostgreSQL database to run the concurrent idempotency integration test.

Graphify extraction precedes OpenWiki documentation: `graphify extract . --code-only --force`, then `openwiki --update --print`.

