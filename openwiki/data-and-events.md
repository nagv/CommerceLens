---
title: Data and events
type: reference
sources:
  - id: openwiki-source-9282d58f9c59816ad510f4a7
    resource: repo://catalog/service-cards/customer-portal.json
  - id: openwiki-source-b7e016f3ec280e840708a027
    resource: repo://catalog/service-cards/inventory-service.json
  - id: openwiki-source-af11939bbf8643c1b828a699
    resource: repo://catalog/service-cards/notification-worker.json
  - id: openwiki-source-b2e7a862b42617e41900fbed
    resource: repo://catalog/service-cards/order-service.json
  - id: openwiki-source-a00b66216a2ae442b9ddaee2
    resource: repo://catalog/service-cards/payment-service.json
  - id: openwiki-source-4ddb29434ca8d6beb19d8c3f
    resource: repo://catalog/service-cards/shipping-service.json
generated: { by: "codex/wiki-summary-catalog", at: "2026-11-11T23:33:01.875Z" }
verified:
  - by: openwiki/0.7.2
    at: 2026-11-11T23:36:30.387Z
---

# Data and events

## customer-portal

### Documented data / persistence (ownership as stated)
- Product catalog (live inventory)
- Cart quantities and client-computed summaries
- Checkout payload: customerEmail, postalCode, items, paymentScenario, shippingScenario
- Order details: id, status, items, subtotalCents, shippingCents, totalCents, paymentId, trackingNumber, failureReason, createdAt
- Order history list
- Notification delivery records
- Tab-scoped idempotency Attempt (key + payload) in sessionStorage

### Events
- Not specified in supplied service documentation.

Read more: [openwiki/service-context.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/customer-portal/openwiki/service-context.md)

## order-service

### Documented data / persistence (ownership as stated)
- PostgreSQL orders table (JSONB bodies, idempotency keys, request hashes, HTTP status, timestamps)
- PostgreSQL order_outbox table (transactional outbox for order.confirmed pending delivery)

### Events
- order.confirmed (durable, with publisher confirms; consumers must deduplicate by eventId)
- order.confirmed.dead (DLQ for unroutable messages)

Read more: [openwiki/service-context.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/order-service/openwiki/service-context.md) · [openwiki/workflows/failure-handling.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/order-service/openwiki/workflows/failure-handling.md)

## inventory-service

### Documented data / persistence (ownership as stated)
- inventory_products (sku, name, price_cents, available)
- inventory_reservations (orderId, items, subtotalCents, status)
- Product
- Reservation
- ReservedItem
- Item

### Events
- Not specified in supplied service documentation.

Read more: [openwiki/service/api.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/inventory-service/openwiki/service/api.md) · [openwiki/service/dependencies.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/inventory-service/openwiki/service/dependencies.md) · [openwiki/service/overview.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/inventory-service/openwiki/service/overview.md)

## payment-service

### Documented data / persistence (ownership as stated)
- Not specified in supplied service documentation.

### Events
- Not specified in supplied service documentation.

Read more: [openwiki/service-context.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/payment-service/openwiki/service-context.md)

## shipping-service

### Documented data / persistence (ownership as stated)
- ShipmentRequest {orderId, postalCode, scenario}
- Shipment {shipmentId, status, trackingNumber, shippingCents}
- ProviderException {Message, Code, Status}
- Fixed rate response {shippingCents:500, currency:"USD"}

### Events
- Not specified in supplied service documentation.

Read more: [openwiki/integrations/provider.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/shipping-service/openwiki/integrations/provider.md) · [openwiki/service/overview.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/shipping-service/openwiki/service/overview.md)

## notification-worker

### Documented data / persistence (ownership as stated)
- PostgreSQL table notification_deliveries (event_id, order_id, payload JSONB, status, attempts, last_error, updated_at)
- Configuration: DATABASE_URL, RABBITMQ_URL, EMAIL_PROVIDER_URL, PROVIDER_TIMEOUT_MS, PORT
- Inbound message schema: eventId, orderId, customerEmail, totalCents, trackingNumber

### Events
- Consumes AMQP order.confirmed
- Dead-letters to AMQP order.confirmed.dead
- Publishes no events/topics

Read more: [openwiki/service-context.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/notification-worker/openwiki/service-context.md)

[Master entry point](quickstart.md)
