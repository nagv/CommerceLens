---
type: quickstart
title: CommerceLens Inventory Service — Quickstart
description: Init page that routes readers through the CommerceLens Inventory Service wiki hierarchy, summarizing its purpose and linking to domain-area pages.
tags: [quickstart, inventory, service, routing]
sources:
  - id: openwiki-source-bb1ebe868e35e9e500714501
    resource: repo://Dockerfile
  - id: openwiki-source-29b4b6da030f0cb9e2e31279
    resource: repo://main.go
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
generated: { by: "openwiki/0.7.2", at: "2026-11-08T23:01:57.916Z" }
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T01:29:34.529Z
---

# CommerceLens Inventory Service — Quickstart

CommerceLens Inventory is a Go 1.23 HTTP service that runs on port `8080` and owns inventory tables for products and reservations in PostgreSQL. It never accepts prices from checkout callers; instead, it returns authoritative item prices during reservation creation. Tables and seed data initialize automatically when the service starts.

## Primary Workflows

| Workflow | Route | Description |
|----------|-------|-------------|
| Reserve stock | `POST /api/reservations` | Decrement available units, lock SKU rows, and return authoritative pricing. |
| Release stock | `POST /api/reservations/{orderId}/release` | Idempotently restore stock for a previously reserved order. |

## Quick Wiki Guide

- **[Service Overview](service/overview.md)** — Identity, purpose, business capabilities, and technology stack.
- **[HTTP API](service/api.md)** — Exact routes, request/response JSON schemas, and status codes.
- **[Dependencies](service/dependencies.md)** — Runtime and build dependencies, including the PostgreSQL requirement.
- **[Reservation Flow](runtime/reservation-flow.md)** — End-to-end reserve workflow from handler to committed transaction, including validation, locking, and failure behavior.
- **[Release Flow](runtime/release-flow.md)** — End-to-end release workflow and idempotency guarantees.
- **[Data Model](data-model/schema.md)** — Database tables, constraints, initialization, and locking strategy.
- **[Operations/Configuration](operations/configuration.md)** — Environment variables, Docker deployment, server timeouts, and health checks.
- **[Testing](testing/coverage.md)** — Tests and the invariants they enforce.

## Required Configuration

The service requires a single environment variable:

- `DATABASE_URL` — PostgreSQL connection string (e.g., `postgres://commerce:<password>@postgres:5432/inventory?sslmode=disable`).

## Build and Run

Tables and three demo products are initialized automatically at startup without resetting existing data. The Docker build command is:

```bash
docker build -t commercelens-inventory .
```

Run with `DATABASE_URL` configured; do not expose this unauthenticated internal demo API publicly.

## Tests

Run `go test ./...` for validation and fingerprint tests. Set `TEST_DATABASE_URL` to a disposable PostgreSQL database to additionally verify concurrent reservations cannot oversell, conflicting replays fail, and releasing twice restores stock once. Docker build runs unit tests.
