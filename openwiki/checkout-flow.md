---
title: Documented business flows
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

# Documented business flows

These per-service flow summaries preserve documented boundaries. Use the linked detailed pages for exact state transitions; the master does not infer one universal sequence for unrelated services.

## customer-portal

- User browses storefront product catalog
- User adds or removes items in cart
- User enters email, postal code, and selects demo payment/shipping scenarios
- Frontend validates checkout inputs and stock availability
- Frontend persists Idempotency-Key and Checkout payload in sessionStorage
- Frontend POSTs checkout to backend with Idempotency-Key header
- Frontend displays order status, tracking, error explanation, or network warning
- User views order history and notification records in the Operations tab

Read more: [openwiki/service-context.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/customer-portal/openwiki/service-context.md)

## order-service

- Client POST /api/orders with Idempotency-Key
- Create pending order and idempotency record
- Reserve inventory via Inventory Service
- Checkpoint order to reserved
- Checkpoint order to payment_unknown before payment call
- Authorize payment via Payment Service
- Checkpoint order to paid
- Create shipment via Shipping Service
- Checkpoint order to confirmed
- Insert order_outbox event for RabbitMQ delivery
- Return 201 with confirmed order

Read more: [openwiki/service-context.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/order-service/openwiki/service-context.md) · [openwiki/workflows/failure-handling.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/order-service/openwiki/workflows/failure-handling.md)

## inventory-service

- List products from inventory_products catalog
- Receive reservation request with orderId and items
- Validate JSON body size, unknown fields, and item constraints
- Lock product rows with FOR UPDATE and serialize order with advisory lock
- Read authoritative prices from inventory_products and decrement available stock
- Store reservation and return priced items with subtotal and reserved status
- Receive release request for orderId
- Restore stock to inventory_products and mark reservation released

Read more: [openwiki/service/api.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/inventory-service/openwiki/service/api.md) · [openwiki/service/dependencies.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/inventory-service/openwiki/service/dependencies.md) · [openwiki/service/overview.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/inventory-service/openwiki/service/overview.md)

## payment-service

- Accept payment or refund request from upstream consumer
- Validate input with Pydantic
- Assign durable idempotency key
- Forward request to external payment provider
- Validate provider response
- Return JSON result to caller

Read more: [openwiki/service-context.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/payment-service/openwiki/service-context.md)

## shipping-service

- Receive shipment creation request with orderId, postalCode, and scenario
- Validate input constraints before invoking provider
- Send POST /shipments to provider with Idempotency-Key header equal to orderId
- Validate provider response structure and fixed shippingCents value
- Return shipment details or map failures to HTTP 502/504/422 with outcome status

Read more: [openwiki/integrations/provider.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/shipping-service/openwiki/integrations/provider.md) · [openwiki/service/overview.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/shipping-service/openwiki/service/overview.md)

## notification-worker

- Consume order.confirmed AMQP message
- Parse and validate JSON payload
- Upsert notification_deliveries and acquire advisory lock on hashtext(eventId)
- Evaluate status gate (sent, dead, pending)
- If pending, POST /email to HTTP provider with Idempotency-Key header
- Persist final status, attempts, and last error to PostgreSQL
- Ack sent messages or nack without requeue to dead-letter exhausted/invalid messages

Read more: [openwiki/service-context.md](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/services/notification-worker/openwiki/service-context.md)

[Master entry point](quickstart.md)
