---
title: CommerceLens master catalog
type: quickstart
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

# CommerceLens master catalog

This is the application-wide entry point for six independently versioned business services. CommerceLens owns deployment, mock providers and this catalog; the customer portal is the frontend.

## Read the application
- [Application overview](application-overview.md): boundaries and architecture.
- [Service catalog](service-catalog.md): responsibilities, stacks and service wikis.
- [Dependencies](dependencies.md): actual runtime connections.
- [Data and events](data-and-events.md): database ownership and asynchronous delivery.
- [Checkout flow](checkout-flow.md): success, uncertainty and compensation.

## Linked OpenWiki workspace
Run `node scripts/link-wikis.mjs` from this repository after cloning all six siblings. This recreates the CommerceLens workspace in the user's local OpenWiki registry. All seven wikis are searchable together through OpenWiki workspace retrieval. Workspace membership means shared documentation scope, not that every service calls every other service.

## Freshness and maintenance
`python scripts/snapshot-catalog.py --check` compares the reviewed source snapshot against the sibling checkouts. After source changes, review affected service wikis and catalog pages, run `python scripts/snapshot-catalog.py`, then finalize reviewed pages with `node scripts/finalize-catalog.mjs`. The finalizer uses OpenWiki 0.7.2 internal APIs, so revalidate it before upgrading. It records explicit claims; it does not fact-check prose. Stale existing claims intentionally stop finalization for review.

For model-driven updates, use `openwiki --update --print` with [instructions](INSTRUCTIONS.md), then review the result and completion metadata. Linking does not automatically regenerate this master catalog.

The source snapshot contains full reviewed source files, hashes and original commit-pinned URLs. It excludes credentials. Documentation-only commits need not change source hashes. See [deployment runbook](../docs/RUNBOOK.md) to run the demo.

## Source evidence

[Reviewed source snapshot](../catalog/source-evidence.json) and [deployment configuration](../compose.yaml). Original source baseline:

- [customer-portal: nginx.conf](https://github.com/nagv/commercelens-customer-portal/blob/1d444dcaa6e0bf3ffb2dd9254c6430ad501c6f95/nginx.conf)
- [order-service: src/main/java/com/commercelens/orders/OrderStore.java](https://github.com/nagv/commercelens-order-service/blob/cd8bdf02b98c4033b203fe554e12d95a46a13225/src/main/java/com/commercelens/orders/OrderStore.java)
- [order-service: src/main/java/com/commercelens/orders/OutboxPublisher.java](https://github.com/nagv/commercelens-order-service/blob/cd8bdf02b98c4033b203fe554e12d95a46a13225/src/main/java/com/commercelens/orders/OutboxPublisher.java)
- [order-service: src/main/java/com/commercelens/orders/Checkout.java](https://github.com/nagv/commercelens-order-service/blob/cd8bdf02b98c4033b203fe554e12d95a46a13225/src/main/java/com/commercelens/orders/Checkout.java)
- [inventory-service: main.go](https://github.com/nagv/commercelens-inventory-service/blob/160854d9317c07a55cb5a23703a0487bb98ab4d8/main.go)
- [notification-worker: src/main.ts](https://github.com/nagv/commercelens-notification-worker/blob/4159264c5465925d8edc99a21fb49565401967d5/src/main.ts)

[Master entry point](quickstart.md)
