---
title: Checkout flow and failure handling
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

# Checkout flow and failure handling

## Successful checkout
1. Portal requests products through Order; Order reads Inventory's product API, backed by its PostgreSQL catalog.
2. Portal submits checkout with an idempotency key retained in browser session storage. Order stores request identity and protects duplicate submissions.
3. Order reserves inventory. Inventory supplies authoritative product prices; Order adds 500 cents shipping.
4. Order records `payment_unknown` before requesting payment authorization. Successful authorization advances to `paid`.
5. Order requests shipment creation. Success produces `confirmed`, with the order and outbox event persisted transactionally.
6. The outbox publisher delivers `order.confirmed` through RabbitMQ. Notification persists delivery state and calls the email provider independently.
7. Portal can query order and notification status through its Nginx routes.

## Failure decisions
| Failure | Recorded outcome / action |
|---|---|
| Inventory reservation error below 500 | `failed` |
| Inventory reservation error at least 500 | `manual_review`, HTTP 503; reservation outcome may be uncertain |
| Payment HTTP 402 | Definite decline: `failed`, release reservation |
| Other payment failures | Retain `payment_unknown` and stock; do not blindly retry or assume no charge |
| Shipping error at least 500 | `manual_review`; retain payment and stock because shipment may exist |
| Definite shipping rejection below 500 | Attempt refund, then release inventory |
| Refund failure | `manual_review`; release is still attempted |
| Release failure | `manual_review`, HTTP 503 |
| Notification delivery failure | Retry/dead-letter independently; confirmed order remains confirmed |

These branches are deliberately different. There is no implemented automatic reconciliation or reservation expiry. Unknown outcomes need explicit investigation.

## Timeouts and demo scenarios
Order's HTTP client connects within two seconds and allows eight seconds per downstream request. Provider adapters default to three-second timeouts; portal fetch allows 30 seconds and Nginx proxy reads 35 seconds.

The mock payment timeout records authorization before delaying its response, demonstrating why a timeout cannot prove payment failure. The mock supports a definite payment decline, shipping rejection and failed email delivery. These scenarios do not charge cards, ship goods or send real email.

## Source evidence

[Reviewed source snapshot](../catalog/source-evidence.json) and [deployment configuration](../compose.yaml). Original source baseline:

- [customer-portal: nginx.conf](https://github.com/nagv/commercelens-customer-portal/blob/1d444dcaa6e0bf3ffb2dd9254c6430ad501c6f95/nginx.conf)
- [order-service: src/main/java/com/commercelens/orders/OrderStore.java](https://github.com/nagv/commercelens-order-service/blob/cd8bdf02b98c4033b203fe554e12d95a46a13225/src/main/java/com/commercelens/orders/OrderStore.java)
- [order-service: src/main/java/com/commercelens/orders/OutboxPublisher.java](https://github.com/nagv/commercelens-order-service/blob/cd8bdf02b98c4033b203fe554e12d95a46a13225/src/main/java/com/commercelens/orders/OutboxPublisher.java)
- [order-service: src/main/java/com/commercelens/orders/Checkout.java](https://github.com/nagv/commercelens-order-service/blob/cd8bdf02b98c4033b203fe554e12d95a46a13225/src/main/java/com/commercelens/orders/Checkout.java)
- [inventory-service: main.go](https://github.com/nagv/commercelens-inventory-service/blob/160854d9317c07a55cb5a23703a0487bb98ab4d8/main.go)
- [notification-worker: src/main.ts](https://github.com/nagv/commercelens-notification-worker/blob/4159264c5465925d8edc99a21fb49565401967d5/src/main.ts)

[Master entry point](quickstart.md)
