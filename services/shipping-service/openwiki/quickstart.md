---
type: quickstart
title: Quickstart
description: Task-routing entry point for the CommerceLens Shipping Service. Guides readers to the service overview, provider integration details, and contract test coverage.
tags: [quickstart, shipping, commercelens, routing]
sources:
  - id: openwiki-source-bb1ebe868e35e9e500714501
    resource: repo://Dockerfile
  - id: openwiki-source-d14cb4231320f903c4c26a78
    resource: repo://Program.cs
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
generated: { by: "openwiki/0.7.2", at: "2026-11-08T23:01:58.542Z" }
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T01:29:46.596Z
---

# Quickstart

This page is the recommended starting point when you need to understand, operate, or change the CommerceLens Shipping Service. It routes you through the three topics that matter most:

1. **[Service Context and Operations](service/overview.md)** — identity, HTTP interfaces, consumed dependencies, business flow, failure behavior, and operational configuration.
2. **[Shipping Provider Integration](integrations/provider.md)** — outbound HTTP contract, idempotency rules, request/response validation, and the failure-mode mapping that forces callers to reconcile ambiguous outcomes.
3. **[Contract and Failure Tests](testing/contract-tests.md)** — xUnit test coverage, mock HTTP handler behavior, and which provider scenarios are validated versus what requires real integration testing.

## What the service does

The CommerceLens Shipping Service is an ASP.NET Core minimal API running on .NET 8. It exposes three HTTP endpoints:

- `GET /health` — static health check
- `GET /api/shipping/rate` — fixed demo rate (`shippingCents: 500`, `currency: "USD"`)
- `POST /api/shipments` — creates a shipment through an external shipping provider

The default provider is the local CommerceLens mock, not a live carrier. Production carrier authentication belongs in a provider-specific adapter.

## Guiding questions

| If you want to know... | Go to... |
|------------------------|----------|
| What endpoints exist, what they accept and return, and how the service is configured | [Service Context and Operations](service/overview.md) |
| How the outbound provider call is built, what `Idempotency-Key` means, why only `422` is safe to compensate, and what happens on timeout or network failure | [Shipping Provider Integration](integrations/provider.md) |
| Which behaviors are covered by tests, how the mock provider works, and what still needs integration testing | [Contract and Failure Tests](testing/contract-tests.md) |

## Running locally

Build the service:

```bash
docker build -t commercelens-shipping .
```

Run the xUnit provider contract tests:

```bash
docker build --target test -t commercelens-shipping-test .
```

The service listens on port `8080`. Use the `SHIPPING_PROVIDER_URL` and `PROVIDER_TIMEOUT_SECONDS` environment variables to target a different provider or adjust the timeout. The demo is unauthenticated; expose it only on loopback or private networks.
