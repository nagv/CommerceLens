---
title: Application overview
type: reference
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T04:25:14.217Z
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
generated: { by: "codex/wiki-summary-catalog", at: "2026-11-09T04:25:14.217Z" }
---

# Application overview

This application map is assembled from compact service summaries generated from service OpenWiki documentation. It does not independently inspect implementation code or verify live behavior.

- **[customer-portal](https://github.com/nagv/commercelens-customer-portal/blob/main/openwiki/quickstart.md)**: Provide a browser UI for a local CommerceLens sandbox where users browse products, place demo orders, and inspect order and notification history.

- **[order-service](https://github.com/nagv/commercelens-order-service/blob/main/openwiki/quickstart.md)**: Checkout coordinator that orchestrates inventory reservation, payment authorization, shipping creation, and durable outbox publishing.

- **[inventory-service](https://github.com/nagv/commercelens-inventory-service/blob/main/openwiki/quickstart.md)**: Internal Go HTTP service that owns authoritative product prices and stock reservations for the CommerceLens platform.

- **[payment-service](https://github.com/nagv/commercelens-payment-service/blob/main/openwiki/quickstart.md)**: The Payment Service is the payment-authorization and refund boundary within CommerceLens that accepts payment and refund requests from upstream consumers, validates input with Pydantic, assigns durable idempotency keys, forwards the requests to an external payment provider, and returns a JSON result.

- **[shipping-service](https://github.com/nagv/commercelens-shipping-service/blob/main/openwiki/quickstart.md)**: Exposes HTTP endpoints for retrieving a fixed shipping rate and creating shipments via an external HTTP provider, defaulting to the CommerceLens mock provider.

- **[notification-worker](https://github.com/nagv/commercelens-notification-worker/blob/main/openwiki/quickstart.md)**: Consume durable order.confirmed RabbitMQ messages, send order-confirmation emails via an HTTP provider, and persist delivery state in PostgreSQL.

## Documentation gaps and conflicts

### customer-portal
- The portal page uses example status names CONFIRMED/PAYMENT_FAILED; the Order wiki uses lowercase states including payment_unknown. Consult the Order failure-handling page for the documented state distinctions.

Evidence: [openwiki/service-context.md](https://github.com/nagv/commercelens-customer-portal/blob/main/openwiki/service-context.md)

### order-service
- Documentation conflict: service-context.md groups payment 5xx/timeouts under manual_review; workflows/failure-handling.md says non-402 payment failures remain payment_unknown. Resolve this in the service wiki before treating one statement as authoritative.

Evidence: [openwiki/service-context.md](https://github.com/nagv/commercelens-order-service/blob/main/openwiki/service-context.md) · [openwiki/workflows/failure-handling.md](https://github.com/nagv/commercelens-order-service/blob/main/openwiki/workflows/failure-handling.md)

### inventory-service
- Upstream caller identity (checkout service) is mentioned but not formally documented as a dependency in supplied pages
- Database schema details, runtime flows, configuration, and test coverage are referenced but absent from supplied pages
- Reservation fingerprinting algorithm is referenced via code paths but not explained in wiki text
- Exact demo product seed data is not listed in supplied pages

Evidence: [openwiki/service/api.md](https://github.com/nagv/commercelens-inventory-service/blob/main/openwiki/service/api.md) · [openwiki/service/dependencies.md](https://github.com/nagv/commercelens-inventory-service/blob/main/openwiki/service/dependencies.md) · [openwiki/service/overview.md](https://github.com/nagv/commercelens-inventory-service/blob/main/openwiki/service/overview.md)

### payment-service
- A logical external payment-provider boundary is documented; the configured default is a local mock. A production provider deployment is not established by this wiki.

Evidence: [openwiki/service-context.md](https://github.com/nagv/commercelens-payment-service/blob/main/openwiki/service-context.md)

### shipping-service
- A logical external shipping-provider boundary is documented; the default is a local mock. A production provider deployment is not established by these pages.

Evidence: [openwiki/integrations/provider.md](https://github.com/nagv/commercelens-shipping-service/blob/main/openwiki/integrations/provider.md) · [openwiki/service/overview.md](https://github.com/nagv/commercelens-shipping-service/blob/main/openwiki/service/overview.md)

### notification-worker
- Email provider defaults to mock-provider:8080 with no documented production service ID or contract beyond Idempotency-Key deduplication.
- GET /api/notifications is explicitly unauthenticated, creating a potential security conflict if exposed beyond private networks.
- No compensation or rollback exists for email failures against confirmed orders.
- Dead messages lack automatic or manual replay implementation.

Evidence: [openwiki/service-context.md](https://github.com/nagv/commercelens-notification-worker/blob/main/openwiki/service-context.md)

[Master entry point](quickstart.md)
