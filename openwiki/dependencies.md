---
title: Runtime dependencies
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

# Runtime dependencies

## Verified service connections
| Caller | Callee | Interface / purpose |
|---|---|---|
| Portal Nginx | Order | `/api/` proxy: products and orders |
| Portal Nginx | Notification worker | More specific `/api/notifications` proxy: delivery visibility |
| Order | Inventory | GET `/api/products`; POST `/api/reservations`; POST `/api/reservations/{id}/release` |
| Order | Payment | POST `/api/payments`; POST `/api/payments/{paymentId}/refund` |
| Order | Shipping | POST `/api/shipments` |
| Order | Orders PostgreSQL | JDBC order and outbox persistence |
| Inventory | Inventory PostgreSQL | Catalog reads, transactional reservations and releases |
| Order outbox publisher | RabbitMQ | Publish persistent `order.confirmed` messages |
| RabbitMQ | Notification worker | Consume `order.confirmed`; dead-letter failures to `order.confirmed.dead` |
| Notification worker | Notifications PostgreSQL | Delivery deduplication, attempts and status |
| Payment | Payment provider role | HTTP `/payments` and `/refunds` |
| Shipping | Shipping provider role | HTTP `/shipments` |
| Notification worker | Email provider role | HTTP `/email` |

## Deployment versus logical boundaries
Compose supplies `PAYMENT_PROVIDER_URL`, `SHIPPING_PROVIDER_URL` and `EMAIL_PROVIDER_URL` as `http://mock-providers:8080`. All provider roles share that local process; its [implementation](../mock-providers/server.py) persists idempotent operations in SQLite. Individual source defaults can differ from effective Compose configuration.

Order uses configured inventory, payment and shipping service URLs. The inventory service reads its own product database; it does not call another catalog service. Order currently uses a fixed 500-cent shipping amount rather than calling Shipping's rate endpoint.

No runtime edge is inferred from OpenWiki linking or Compose `depends_on`. The latter establishes startup dependencies. The table above is based on source call sites and [Compose wiring](../compose.yaml).

## Source evidence

[Reviewed source snapshot](../catalog/source-evidence.json) and [deployment configuration](../compose.yaml). Original source baseline:

- [customer-portal: nginx.conf](https://github.com/nagv/commercelens-customer-portal/blob/1d444dcaa6e0bf3ffb2dd9254c6430ad501c6f95/nginx.conf)
- [customer-portal: src/api.ts](https://github.com/nagv/commercelens-customer-portal/blob/1d444dcaa6e0bf3ffb2dd9254c6430ad501c6f95/src/api.ts)
- [customer-portal: src/main.tsx](https://github.com/nagv/commercelens-customer-portal/blob/1d444dcaa6e0bf3ffb2dd9254c6430ad501c6f95/src/main.tsx)
- [order-service: src/main/java/com/commercelens/orders/RemoteServices.java](https://github.com/nagv/commercelens-order-service/blob/cd8bdf02b98c4033b203fe554e12d95a46a13225/src/main/java/com/commercelens/orders/RemoteServices.java)
- [order-service: src/main/java/com/commercelens/orders/OrderStore.java](https://github.com/nagv/commercelens-order-service/blob/cd8bdf02b98c4033b203fe554e12d95a46a13225/src/main/java/com/commercelens/orders/OrderStore.java)
- [order-service: src/main/java/com/commercelens/orders/OutboxPublisher.java](https://github.com/nagv/commercelens-order-service/blob/cd8bdf02b98c4033b203fe554e12d95a46a13225/src/main/java/com/commercelens/orders/OutboxPublisher.java)
- [order-service: src/main/java/com/commercelens/orders/Checkout.java](https://github.com/nagv/commercelens-order-service/blob/cd8bdf02b98c4033b203fe554e12d95a46a13225/src/main/java/com/commercelens/orders/Checkout.java)
- [order-service: src/main/java/com/commercelens/orders/OrderController.java](https://github.com/nagv/commercelens-order-service/blob/cd8bdf02b98c4033b203fe554e12d95a46a13225/src/main/java/com/commercelens/orders/OrderController.java)
- [order-service: src/main/resources/schema.sql](https://github.com/nagv/commercelens-order-service/blob/cd8bdf02b98c4033b203fe554e12d95a46a13225/src/main/resources/schema.sql)
- [order-service: src/main/resources/application.properties](https://github.com/nagv/commercelens-order-service/blob/cd8bdf02b98c4033b203fe554e12d95a46a13225/src/main/resources/application.properties)
- [inventory-service: main.go](https://github.com/nagv/commercelens-inventory-service/blob/160854d9317c07a55cb5a23703a0487bb98ab4d8/main.go)
- [payment-service: app.py](https://github.com/nagv/commercelens-payment-service/blob/55a3bce4ebb15f3c4b4558005c46e6bc5a6a53cd/app.py)
- [shipping-service: Program.cs](https://github.com/nagv/commercelens-shipping-service/blob/e12ce558709ff52a0094cd1a1e2f67bdc6f32d00/Program.cs)
- [notification-worker: src/main.ts](https://github.com/nagv/commercelens-notification-worker/blob/4159264c5465925d8edc99a21fb49565401967d5/src/main.ts)
- [notification-worker: src/delivery.ts](https://github.com/nagv/commercelens-notification-worker/blob/4159264c5465925d8edc99a21fb49565401967d5/src/delivery.ts)
- [notification-worker: src/lifecycle.ts](https://github.com/nagv/commercelens-notification-worker/blob/4159264c5465925d8edc99a21fb49565401967d5/src/lifecycle.ts)

[Master entry point](quickstart.md)
