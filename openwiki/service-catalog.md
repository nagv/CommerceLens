---
title: Service catalog
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
generated: { by: "codex/wiki-summary-catalog", at: "2026-11-09T04:14:05.802Z" }
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T04:25:14.217Z
---

# Service catalog

| Service | Purpose | Stack | Detailed wiki |
|---|---|---|---|
| customer-portal | Provide a browser UI for a local CommerceLens sandbox where users browse products, place demo orders, and inspect order and notification history. | React 19, Vite, nginx | [Open service wiki](https://github.com/nagv/commercelens-customer-portal/blob/main/openwiki/quickstart.md) |
| order-service | Checkout coordinator that orchestrates inventory reservation, payment authorization, shipping creation, and durable outbox publishing. | Java 21, Spring Boot 3.4.2, PostgreSQL, RabbitMQ | [Open service wiki](https://github.com/nagv/commercelens-order-service/blob/main/openwiki/quickstart.md) |
| inventory-service | Internal Go HTTP service that owns authoritative product prices and stock reservations for the CommerceLens platform. | Go 1.23, net/http, PostgreSQL via pgx/v5, Docker multi-stage build | [Open service wiki](https://github.com/nagv/commercelens-inventory-service/blob/main/openwiki/quickstart.md) |
| payment-service | The Payment Service is the payment-authorization and refund boundary within CommerceLens that accepts payment and refund requests from upstream consumers, validates input with Pydantic, assigns durable idempotency keys, forwards the requests to an external payment provider, and returns a JSON result. | Python 3.12, FastAPI, httpx | [Open service wiki](https://github.com/nagv/commercelens-payment-service/blob/main/openwiki/quickstart.md) |
| shipping-service | Exposes HTTP endpoints for retrieving a fixed shipping rate and creating shipments via an external HTTP provider, defaulting to the CommerceLens mock provider. | ASP.NET Core on .NET 8.0 | [Open service wiki](https://github.com/nagv/commercelens-shipping-service/blob/main/openwiki/quickstart.md) |
| notification-worker | Consume durable order.confirmed RabbitMQ messages, send order-confirmation emails via an HTTP provider, and persist delivery state in PostgreSQL. | Node.js 22, TypeScript, amqplib, pg | [Open service wiki](https://github.com/nagv/commercelens-notification-worker/blob/main/openwiki/quickstart.md) |

## customer-portal

- No programmatic interfaces exposed (consumer-only browser frontend)

Read more: [openwiki/service-context.md](https://github.com/nagv/commercelens-customer-portal/blob/main/openwiki/service-context.md)

## order-service

- HTTP GET /health
- HTTP GET /api/products
- HTTP GET /api/orders
- HTTP GET /api/orders/{id}
- HTTP POST /api/orders (requires Idempotency-Key; idempotent by key plus SHA-256 body hash)
- AMQP publisher to order.confirmed on default exchange with DLX order.confirmed.dead

Read more: [openwiki/service-context.md](https://github.com/nagv/commercelens-order-service/blob/main/openwiki/service-context.md) · [openwiki/workflows/failure-handling.md](https://github.com/nagv/commercelens-order-service/blob/main/openwiki/workflows/failure-handling.md)

## inventory-service

- GET /health
- GET /api/products
- POST /api/reservations
- POST /api/reservations/{orderId}/release

Read more: [openwiki/service/api.md](https://github.com/nagv/commercelens-inventory-service/blob/main/openwiki/service/api.md) · [openwiki/service/dependencies.md](https://github.com/nagv/commercelens-inventory-service/blob/main/openwiki/service/dependencies.md) · [openwiki/service/overview.md](https://github.com/nagv/commercelens-inventory-service/blob/main/openwiki/service/overview.md)

## payment-service

- GET /health
- POST /api/payments
- POST /api/payments/{paymentId}/refund
- GET /docs

Read more: [openwiki/service-context.md](https://github.com/nagv/commercelens-payment-service/blob/main/openwiki/service-context.md)

## shipping-service

- GET /health
- GET /api/shipping/rate
- POST /api/shipments

Read more: [openwiki/integrations/provider.md](https://github.com/nagv/commercelens-shipping-service/blob/main/openwiki/integrations/provider.md) · [openwiki/service/overview.md](https://github.com/nagv/commercelens-shipping-service/blob/main/openwiki/service/overview.md)

## notification-worker

- HTTP GET /health
- HTTP GET /api/notifications (unauthenticated, max 100 rows)
- AMQP consume queue order.confirmed (durable, prefetch 1)
- AMQP dead-letter queue order.confirmed.dead
- HTTP POST /email to external provider

Read more: [openwiki/service-context.md](https://github.com/nagv/commercelens-notification-worker/blob/main/openwiki/service-context.md)

[Master entry point](quickstart.md)
