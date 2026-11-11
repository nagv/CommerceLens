---
title: Documented dependencies
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

# Documented dependencies

For consumes, the listed service consumes from the target; for publishes, it publishes to the target. Workspace membership is not a runtime connection. Names matching registered IDs after case/space normalization link to those service wikis. Other targets remain literal documented targets, not guessed service matches.

| Caller / participant | Relationship | Target | Interface | Evidence |
|---|---|---|---|---|
| customer-portal | consumes | [order-service](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/order-service/openwiki/quickstart.md) | HTTP /api/products, /api/orders, /api/orders/{id} | [Service documentation](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/customer-portal/openwiki/service-context.md) |
| customer-portal | consumes | [notification-worker](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/notification-worker/openwiki/quickstart.md) | HTTP /api/notifications | [Service documentation](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/customer-portal/openwiki/service-context.md) |
| order-service | http | [inventory-service](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/inventory-service/openwiki/quickstart.md) | POST /api/reservations, POST /api/reservations/{id}/release, GET /api/products | [Service documentation](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/order-service/openwiki/service-context.md) |
| order-service | http | [payment-service](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/payment-service/openwiki/quickstart.md) | POST /api/payments, POST /api/payments/{paymentId}/refund | [Service documentation](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/order-service/openwiki/service-context.md) |
| order-service | http | [shipping-service](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/shipping-service/openwiki/quickstart.md) | POST /api/shipments | [Service documentation](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/order-service/openwiki/service-context.md) |
| order-service | database | PostgreSQL | orders table, order_outbox table | [Service documentation](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/order-service/openwiki/service-context.md) |
| order-service | publishes | RabbitMQ | order.confirmed queue, order.confirmed.dead DLQ | [Service documentation](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/order-service/openwiki/service-context.md) |
| inventory-service | database | PostgreSQL | TCP/Unix socket, SQL via pgxpool | [Service documentation](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/inventory-service/openwiki/service/dependencies.md) |
| payment-service | http | Payment provider | POST /payments and POST /refunds with JSON body and Idempotency-Key header | [Service documentation](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/payment-service/openwiki/service-context.md) |
| shipping-service | http | Shipping provider | POST /shipments | [Service documentation](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/shipping-service/openwiki/service/overview.md) |
| notification-worker | external | email-provider | POST /email with Idempotency-Key header | [Service documentation](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/notification-worker/openwiki/service-context.md) |
| notification-worker | consumes | rabbitmq | Queue order.confirmed (durable, DLX to order.confirmed.dead) | [Service documentation](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/notification-worker/openwiki/service-context.md) |
| notification-worker | database | postgresql | Table notification_deliveries (CRUD + advisory lock) | [Service documentation](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/notification-worker/openwiki/service-context.md) |

[Master entry point](quickstart.md)
