---
title: Service catalog
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

# Service catalog

## Services
| Service | Stack | Responsibilities | Owned data | Service wiki |
|---|---|---|---|---|
| Customer portal | React / TypeScript, Nginx | Products, cart, checkout, order and notification visibility | Browser session idempotency key | [Wiki](https://github.com/nagv/commercelens-customer-portal/blob/main/openwiki/quickstart.md) |
| Order | Java / Spring Boot | Checkout orchestration, order lookup, product facade, outbox publication | PostgreSQL orders and order_outbox | [Wiki](https://github.com/nagv/commercelens-order-service/blob/main/openwiki/quickstart.md) |
| Inventory | Go | Product catalog, stock reservation and release | PostgreSQL inventory_products and inventory_reservations | [Wiki](https://github.com/nagv/commercelens-inventory-service/blob/main/openwiki/quickstart.md) |
| Payment | Python / FastAPI | Provider authorization and refund adapter | No own database | [Wiki](https://github.com/nagv/commercelens-payment-service/blob/main/openwiki/quickstart.md) |
| Shipping | C# / ASP.NET Core | Shipment adapter and fixed rate endpoint | No own database | [Wiki](https://github.com/nagv/commercelens-shipping-service/blob/main/openwiki/quickstart.md) |
| Notification worker | Node.js / TypeScript | Consume confirmed orders, send email, expose delivery status | PostgreSQL notification_deliveries | [Wiki](https://github.com/nagv/commercelens-notification-worker/blob/main/openwiki/quickstart.md) |

## Central repository
CommerceLens owns Compose, mock providers, shared documentation instructions and this master wiki. It is not another business service or the frontend. The planned assistant API is not included in the implemented service count.

See [dependencies](dependencies.md) for exact caller/callee relationships and [data and events](data-and-events.md) for storage ownership.

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
