---
title: Data ownership and events
type: reference
description: Source-backed application-wide CommerceLens documentation.
tags: [commercelens, catalog, architecture]
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T03:50:36.913Z
sources:
  - id: openwiki-source-b3c12cba5f5c82eed11eede7
    resource: repo://catalog/source-evidence.json
  - id: openwiki-source-e201e686a785f09b6d899f0b
    resource: repo://compose.yaml
generated: { by: "codex/openwiki-lifecycle-review", at: "2026-11-09T03:50:36.913Z" }
---

# Data ownership and events

## Owned stores
| Owner | Database / tables | Purpose |
|---|---|---|
| Order | orders / orders, order_outbox | Idempotency key and request hash, order JSON and HTTP result; pending event publication |
| Inventory | inventory / inventory_products, inventory_reservations | Authoritative product prices and stock; reservation identity, request hash and status |
| Notification | notifications / notification_deliveries | Event identity, payload, status, attempts and last error |
| Mock providers | SQLite /data/providers.db, operations | Durable demo provider idempotency and stable operation results |

Services access their own PostgreSQL databases. The API boundaries carry business requests; there is no cross-service database access in the documented flow. Inventory serializes reservation work with transaction/advisory and row locks; release is idempotent.

## Confirmed-order event
Order stores a confirmed order and its outbox row in one database transaction. The publisher runs every two seconds, reads unpublished rows, sends persistent messages and waits up to five seconds for publisher confirmation before recording publication.

- Queue: `order.confirmed`, durable.
- Event ID: `order-confirmed-` followed by the order ID.
- Payload: `eventId`, `orderId`, `customerEmail`, `totalCents`, `trackingNumber`.
- Consumer: Notification worker, prefetch 1.
- Dead-letter queue: `order.confirmed.dead`, via the default exchange.

This is at-least-once delivery. A crash between broker confirmation and database marking can produce a duplicate. The notification event ID and provider idempotency key protect repeated delivery attempts; this is not an exactly-once guarantee.

## Notification outcomes
The worker locks by event ID, persists attempts before sending and acknowledges a sent delivery. A previously sent matching event is acknowledged without resending. Provider delivery has at most three total attempts with 250/500 ms retry delays; exhausted delivery is dead-lettered. Payload conflicts and invalid events are rejected. Database errors can requeue messages.

Email provider requests use the event ID as `Idempotency-Key`. Notification failure does not roll back the confirmed order. The status API returns the latest 100 deliveries.

## Source evidence

[Reviewed source snapshot](../catalog/source-evidence.json) and [deployment configuration](../compose.yaml). Original source baseline:

- [customer-portal: nginx.conf](https://github.com/nagv/commercelens-customer-portal/blob/1d444dcaa6e0bf3ffb2dd9254c6430ad501c6f95/nginx.conf)
- [order-service: src/main/java/com/commercelens/orders/OrderStore.java](https://github.com/nagv/commercelens-order-service/blob/cd8bdf02b98c4033b203fe554e12d95a46a13225/src/main/java/com/commercelens/orders/OrderStore.java)
- [order-service: src/main/java/com/commercelens/orders/OutboxPublisher.java](https://github.com/nagv/commercelens-order-service/blob/cd8bdf02b98c4033b203fe554e12d95a46a13225/src/main/java/com/commercelens/orders/OutboxPublisher.java)
- [order-service: src/main/java/com/commercelens/orders/Checkout.java](https://github.com/nagv/commercelens-order-service/blob/cd8bdf02b98c4033b203fe554e12d95a46a13225/src/main/java/com/commercelens/orders/Checkout.java)
- [inventory-service: main.go](https://github.com/nagv/commercelens-inventory-service/blob/160854d9317c07a55cb5a23703a0487bb98ab4d8/main.go)
- [notification-worker: src/main.ts](https://github.com/nagv/commercelens-notification-worker/blob/4159264c5465925d8edc99a21fb49565401967d5/src/main.ts)

[Master entry point](quickstart.md)
