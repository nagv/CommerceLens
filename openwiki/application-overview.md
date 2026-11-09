---
title: Application overview
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

# Application overview

CommerceLens demonstrates a commerce checkout across six services. The portal presents products, cart, checkout and operational information. Order coordinates stock reservation, payment and shipment; a durable event drives email notification.

## Runtime topology
```mermaid
flowchart LR
 UI[Customer portal] --> O[Order service]
 UI --> N[Notification status API]
 O --> I[Inventory service]
 O --> P[Payment service]
 O --> S[Shipping service]
 O --> OD[(Orders PostgreSQL)]
 I --> ID[(Inventory PostgreSQL)]
 O -->|outbox publisher| Q[RabbitMQ order.confirmed]
 Q --> N
 N --> ND[(Notifications PostgreSQL)]
 P --> MP[Payment provider mock]
 S --> MS[Shipping provider mock]
 N --> ME[Email provider mock]
```

## Boundaries
Three PostgreSQL databases have separate owners: Order, Inventory and Notification. Payment and Shipping have no application database. The three provider roles are implemented by one local `mock-providers` container with SQLite persistence. They represent external business dependencies, but no real vendor is contacted by this deployment.

The portal is published at localhost:3000. Nginx routes business API requests into the internal Compose network. RabbitMQ management is exposed on localhost:15672; database and business API ports are not published.

## Current scope
The six business services, portal, Graphify artifacts and service OpenWiki documentation exist. This catalog describes their static architecture and source behavior. Pinecone ingestion, the application assistant/chat UI and the RAG evaluation harness remain future work. Documentation cannot establish live operational status.

## Source evidence

[Reviewed source snapshot](../catalog/source-evidence.json) and [deployment configuration](../compose.yaml). Original source baseline:

- [customer-portal: nginx.conf](https://github.com/nagv/commercelens-customer-portal/blob/1d444dcaa6e0bf3ffb2dd9254c6430ad501c6f95/nginx.conf)
- [order-service: src/main/java/com/commercelens/orders/OrderStore.java](https://github.com/nagv/commercelens-order-service/blob/cd8bdf02b98c4033b203fe554e12d95a46a13225/src/main/java/com/commercelens/orders/OrderStore.java)
- [order-service: src/main/java/com/commercelens/orders/OutboxPublisher.java](https://github.com/nagv/commercelens-order-service/blob/cd8bdf02b98c4033b203fe554e12d95a46a13225/src/main/java/com/commercelens/orders/OutboxPublisher.java)
- [order-service: src/main/java/com/commercelens/orders/Checkout.java](https://github.com/nagv/commercelens-order-service/blob/cd8bdf02b98c4033b203fe554e12d95a46a13225/src/main/java/com/commercelens/orders/Checkout.java)
- [inventory-service: main.go](https://github.com/nagv/commercelens-inventory-service/blob/160854d9317c07a55cb5a23703a0487bb98ab4d8/main.go)
- [notification-worker: src/main.ts](https://github.com/nagv/commercelens-notification-worker/blob/4159264c5465925d8edc99a21fb49565401967d5/src/main.ts)

[Master entry point](quickstart.md)
