---
type: navigation-hub
title: CommerceLens Payment Service — Quickstart
description: Entry point and reading-order guide for the CommerceLens Payment Service wiki. Summarizes the FastAPI boundary, its role as a provider forwarder, and where to find operational, runtime, and safety documentation.
tags: [quickstart, navigation, fastapi, payments, commerce-lens]
sources:
  - id: openwiki-source-17dded95897e01ee430228e3
    resource: repo://app.py
  - id: openwiki-source-bb1ebe868e35e9e500714501
    resource: repo://Dockerfile
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-aee60addf228e6c9bf133836
    resource: repo://tests/test_app.py
generated: { by: "openwiki/0.7.2", at: "2026-11-08T23:01:22.698Z" }
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T01:29:41.531Z
---

# CommerceLens Payment Service — Quickstart

## Service overview

The CommerceLens Payment Service is a single-file Python/FastAPI HTTP boundary that accepts payment authorization and refund requests, then forwards them to an external payment provider via HTTP with enforced idempotency keys. It listens on port 8080 and exposes a health endpoint, authorization endpoint, and refund endpoint; interactive API documentation is available at `/docs`.

## Service responsibilities

- **Authorize payments**: Accept `POST /api/payments` with `orderId`, `amountCents`, `currency`, and `scenario`, validate the payload, and forward it to the provider as `POST /payments`.
- **Process refunds**: Accept `POST /api/payments/{paymentId}/refund` with `orderId` and forward it to the provider as `POST /refunds`.
- **Enforce idempotency**: Each forwarded request carries an `Idempotency-Key` header derived from the `orderId` (for payments) or from `refund:{orderId}:{paymentId}` (for refunds), so the provider can deduplicate safely.
- **Return safe failure codes**: Translate provider responses into explicit HTTP status codes — `402` for declines, `504` for timeouts with unknown outcome, `502` for unavailable or invalid responses, and `409` for conflicting idempotency keys — so callers never perform blind retries.
- **Health probes**: Provide a lightweight `GET /health` endpoint for deployment health checks.

## Entrypoints and control flow

The entire boundary lives in [`app.py`](../app.py). Key pieces:

- **`provider_client()`** ([`app.py#L23-L28`](../app.py#L23-L28)) — FastAPI dependency that yields an `httpx.AsyncClient` configured with `PAYMENT_PROVIDER_URL` (default `http://mock-provider:8080`) and `PROVIDER_TIMEOUT_SECONDS` (default `3`).
- **`forward()`** ([`app.py#L31-L48`](../app.py#L31-L48)) — Shared helper that POSTs to the provider, attaches the `Idempotency-Key`, and maps provider status codes and exceptions into bounded responses.
- **`authorize()`** and **`refund()`** ([`app.py#L56-L63`](../app.py#L56-L63)) — FastAPI route handlers that accept typed Pydantic models (`Payment`, `Refund`) and invoke `forward()`.

Requests enter through the FastAPI routes, are validated by Pydantic, forwarded to the provider via `httpx`, and the response — or a mapped error — is returned to the caller. No local persistence is used; the provider owns the truth.

## Configuration at a glance

| Variable | Default | Purpose |
|---|---|---|
| `PAYMENT_PROVIDER_URL` | `http://mock-provider:8080` | Target base URL for provider POST `/payments` and `/refunds`. |
| `PROVIDER_TIMEOUT_SECONDS` | `3` | HTTP request timeout to the provider. |
The command `uvicorn app:app --host 0.0.0.0 --port 8080` starts the service on port `8080`. This is fixed in the Dockerfile `CMD` and is not configurable via an environment variable.

Runtime configuration is covered in detail on the [Operations](operations/configuration.md) page.

## Wiki page map

Use these pages to orient yourself before making changes or operating the service.

- **[Service Context](service-context.md)** — Complete service identity, API contracts, dependency table, business flow, failure behavior, and evidence for the payment boundary.
- **[Authorization and Refund Request Flows](runtime/payment-flows.md)** — End-to-end request lifecycles from client through the FastAPI boundary to the external payment provider, with sequence diagrams.
- **[Payment Failure Model, Idempotency, and Reconciliation](safety/failure-model.md)** — Safety-critical rules governing idempotency keys, ambiguous timeouts, and required reconciliation before retries.
- **[Deployment, Configuration, and Observability](operations/configuration.md)** — Environment variables, Dockerfile targets, health checks, and runtime constraints for the payment service.

## Recommended reading order

**For a new coder**
1. Start here (Quickstart) for the overview and nav map.
2. Read [Service Context](service-context.md) to understand the contracts, responders, and external dependencies.
3. Read [Authorization and Refund Request Flows](runtime/payment-flows.md) to trace the request lifecycle and see the sequence diagrams.
4. Read [Payment Failure Model, Idempotency, and Reconciliation](safety/failure-model.md) to learn why blind retries are unsafe and how reconciliation works.
5. Read [Deployment, Configuration, and Observability](operations/configuration.md) to learn how to build, configure, and run the service.

**For a change-task agent**
1. Start here (Quickstart) for the overview and links.
2. Read [Service Context](service-context.md) for the dependency table and contract boundaries relevant to your change.
3. Read [Payment Failure Model, Idempotency, and Reconciliation](safety/failure-model.md) if your change touches retries, error handling, or idempotency logic.
4. Read the [Authorization and Refund Request Flows](runtime/payment-flows.md) page if your change affects request routing or provider integration.
5. Read [Deployment, Configuration, and Observability](operations/configuration.md) only if your change affects build targets, environment variables, or observability.
