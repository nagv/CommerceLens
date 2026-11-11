---
type: quickstart
title: "Order Service Quickstart"
description: "Task-routing map for coding agents working on the CommerceLens Order Service. Directs readers to the documentation that covers each change domain."
tags: [quickstart, order-service, routing, tasks, documentation-map]
sources:
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-7fc81aadbff6a8f3966ae5d8
    resource: repo://src/main/java/com/commercelens/orders/Checkout.java
  - id: openwiki-source-27e0466d222e980bd7b01ba9
    resource: repo://src/main/java/com/commercelens/orders/OrderApplication.java
  - id: openwiki-source-16a5a13276943dc522d2add4
    resource: repo://src/main/java/com/commercelens/orders/OrderController.java
  - id: openwiki-source-108cb54cf02515bb6eae368e
    resource: repo://src/main/java/com/commercelens/orders/OrderStore.java
  - id: openwiki-source-7964e1e0e7a9acfd2ed60030
    resource: repo://src/main/java/com/commercelens/orders/OutboxPublisher.java
  - id: openwiki-source-d4a4dd9b29d01cb7f79aeb3f
    resource: repo://src/main/java/com/commercelens/orders/RemoteServices.java
  - id: openwiki-source-2995ce030e79da17d6712043
    resource: repo://src/main/resources/schema.sql
  - id: openwiki-source-ee4d53553f132f0e92588af5
    resource: repo://src/test/java/com/commercelens/orders/CheckoutTest.java
  - id: openwiki-source-4b0a0ba7c029fed22eb0542d
    resource: repo://src/test/java/com/commercelens/orders/OrderStoreTest.java
generated: { by: "codex/openwiki-lifecycle-review", at: "2026-11-08T23:17:43.833Z" }
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T01:28:27.799Z
---

# Order Service Quickstart

Use this page to route your task to the right documentation. The CommerceLens Order Service is a Java 21 / Spring Boot checkout coordinator that orchestrates inventory reservation, payment authorization, and shipment creation, persisting state in PostgreSQL and publishing confirmed events through RabbitMQ (`repo://src/main/java/com/commercelens/orders/OrderApplication.java#L1-L9`). This is a local demonstration service without authentication.

## Task Routing

| If your task involves … | Read this page first |
|---|---|
| Adding, changing, or removing HTTP endpoints; request/response schemas; idempotency rules | [HTTP API Surface and Idempotency](architecture/api-surface.md) |
| Changing checkout orchestration logic, saga states, compensation paths, or the `Checkout.Ports` contract | [Checkout Saga](architecture/checkout-saga.md) |
| Changing the database schema, persistence layer, JSONB mappings, or outbox table structure | [Data Model and Persistence](architecture/data-model.md) |
| Changing messaging, queue declarations, publisher confirms, dead-letter handling, or outbox polling | [Outbox Publishing and Messaging](architecture/outbox-publishing.md) |
| Changing downstream service contracts, HTTP timeouts, or error mapping to `RemoteFailure` | [External Service Integrations](integrations/external-services.md) |
| Changing error handling, compensation flow, `manual_review` triggers, or failure semantics | [Failure Handling and Compensation](workflows/failure-handling.md) |
| Adding or changing tests (unit tests with `FakePorts`, concurrency integration tests) | [Testing Strategy](testing/test-strategy.md) |
| Service identity, owned interfaces, consumed dependencies, configuration variables, or observability | [Service Context](service-context.md) |

## Service Context First

Before making any change, consult [Service Context](service-context.md) for the single source of truth on service identity, provided HTTP interfaces, consumed downstream services, the dependency table with direction and certainty, and the full checkout business flow (`repo://openwiki/service-context.md#L13-L74`). It also lists all environment variables and their aliases (`repo://openwiki/service-context.md#L226-L250`).

## Major Documentation Domains

- **API Surface** — Endpoint-by-endpoint reference for `OrderController`: methods, path variables, request/response schemas, status codes, validation rules, and the idempotency key plus SHA-256 request-hash mechanism.
- **Checkout Saga** — The `Checkout` state machine, `Ports` interface, checkpointing after every external effect, and why intermediate states intentionally block automatic replay.
- **Data Model** — PostgreSQL `orders` and `order_outbox` tables, JSONB storage, `OrderStore` operations, and how the `http_status` column is kept separate from the domain JSONB body.
- **Outbox Publishing** — RabbitMQ transactional outbox with publisher confirms, DLX to `order.confirmed.dead`, scheduled polling every 2 seconds, and at-least-once delivery semantics.
- **External Services** — HTTP contracts with Inventory, Payment, and Shipping: endpoint paths, 8-second request / 2-second connect timeouts, response validation, and error mapping.
- **Failure Handling** — Definite declines, uncertain outcomes (`payment_unknown`, `manual_review`), compensation paths (refund + release), and the deliberate absence of automated reconciliation in this MVP.
- **Testing Strategy** — Unit tests via `FakePorts` for saga branches and integration tests against PostgreSQL for concurrent idempotency.
