---
type: service-overview
title: CommerceLens Inventory Service — Identity and Overview
description: Identity, purpose, business capabilities, technology stack, entry points, and ownership evidence for the CommerceLens Inventory Service.
tags: [inventory, overview, commerce, go, postgresql]
sources:
  - id: openwiki-source-bb1ebe868e35e9e500714501
    resource: repo://Dockerfile
  - id: openwiki-source-7bd911fdd3026b7b031a01e3
    resource: repo://go.mod
  - id: openwiki-source-1bebaeef76eb2a89dea06f8d
    resource: repo://integration_test.go
  - id: openwiki-source-569e5a25197cee8330354b08
    resource: repo://main_test.go
  - id: openwiki-source-29b4b6da030f0cb9e2e31279
    resource: repo://main.go
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
generated: { by: "openwiki/0.7.2", at: "2026-11-08T23:01:57.916Z" }
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T01:29:34.529Z
---

# CommerceLens Inventory Service — Identity and Overview

The CommerceLens Inventory Service is an internal Go HTTP service that owns authoritative product prices and stock reservations for the CommerceLens platform. It is a single-binary, framework-free service backed by PostgreSQL, deployed via a Docker multi-stage build.

## Purpose and Business Capabilities

The service has a narrow, well-defined responsibility: it manages inventory state and governs how stock moves from available inventory into reserved state for orders. It exposes three primary capabilities to upstream callers (principally a checkout service):

| Capability | What it does |
|-----------|--------------|
| **Catalog listing** | Return every product with its SKU, display name, current price, and available stock count. |
| **Stock reservation** | Lock stock for a given order, returning authoritative item prices and a subtotal. |
| **Stock release** | Restore stock from a previous reservation back to available inventory. |

The service enforces a **critical ownership boundary**: it owns the `inventory_products` and `inventory_reservations` tables, and it **never accepts prices from callers**. All prices are read from `inventory_products` at reservation time and returned authoritatively in the response. Callers cannot influence or override pricing during the reservation flow.

## Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Go 1.23 |
| HTTP server | `net/http` from the Go standard library (no external framework) |
| Database driver | `github.com/jackc/pgx/v5 v5.7.2` |
| Database | PostgreSQL (runtime dependency) |
| Build | Docker multi-stage build (`golang:1.23-alpine` → `alpine:3.21`) |

The dependency footprint is intentionally minimal. The only non-standard library module is `pgx/v5` and its transitive dependencies, which handle connection pooling, authentication, and PostgreSQL wire protocol support.

## Entry Point and Bootstrap

The binary entry point is `main()` in `main.go`. Bootstrapping is small and linear:

1. Read `DATABASE_URL` from the environment. If unset, the process exits immediately with `log.Fatal`. repo://main.go#L260-L263
2. Create a `pgxpool.Pool` with a 15-second startup context. repo://main.go#L266-L269
3. Execute the compiled `schema` const, which creates `inventory_products` and `inventory_reservations` with `IF NOT EXISTS` and seeds three demo products with `ON CONFLICT DO NOTHING`. repo://main.go#L271-L273, repo://main.go#L255-L257
4. Configure an `http.Server` on `:8080` with read, write, and idle timeouts, and register the handler mux from `Store.handler()`. repo://main.go#L274-L277

On startup the service is therefore self-initializing: it creates its tables and demo data if they do not already exist, then begins serving HTTP requests.

## Ownership Evidence

Several structural choices make the service's ownership of inventory data unambiguous:

- **Table namespacing**: Both tables carry the `inventory_` prefix — `inventory_products` and `inventory_reservations` — making it clear which service owns them. repo://main.go#L255-L256
- **Single-binary deployment**: The entire service compiles to one static binary named `inventory`, produced by the Dockerfile's multi-stage build. repo://Dockerfile#L6, repo://Dockerfile#L10-L12
- **No delegation**: There are no outbound HTTP clients, message queues, caches, or external providers. Every business operation is performed directly against the owned PostgreSQL tables.
- **Schema co-location**: The `CREATE TABLE` and seed `INSERT` statements live as a `const` string inside `main.go`, versioned with the application code rather than managed by an external migration tool.

## Core Types

The service defines a small set of domain types in `main.go` that shape the API contract:

| Type | Purpose |
|------|---------|
| `Item` | `{ sku, quantity }` — caller input for a single line item |
| `ReserveRequest` | `{ orderId, items[] }` — payload for `POST /api/reservations` |
| `Product` | `{ sku, name, priceCents, available }` — row from `inventory_products` |
| `ReservedItem` | `{ sku, name, quantity, priceCents }` — authoritative priced item in a reservation |
| `Reservation` | `{ orderId, items[], subtotalCents, status }` — reservation result returned to callers |
| `Store` | `{ pool *pgxpool.Pool }` — thin data-access wrapper around the connection pool |
| `APIError` | Structured error carrying an HTTP status and message |

The `Store` type is the central abstraction: it owns `reserve()`, `release()`, and `products()` methods, and exposes `handler()` which wires them to HTTP routes.

## Key Invariants

- **Price authority**: The service reads `price_cents` from `inventory_products` during reservation and includes it in the response. Callers have no price input. repo://main.go#L111-L125
- **Idempotent reservation**: Replaying the exact same request returns the previously computed result without decrementing stock again. The service detects replays using a SHA-256 fingerprint of the canonical item list. repo://main.go#L67-L73, repo://main.go#L90-L101
- **Idempotent release**: Releasing an already-released reservation succeeds without restoring stock a second time. repo://main.go#L155-L156
- **Overselling prevention**: Reservation transactions lock product rows with `FOR UPDATE` in ascending SKU order, ensuring that concurrent requests cannot decrement stock below zero. repo://main.go#L106-L108
- **Order serialization**: An advisory lock (`pg_advisory_xact_lock`) serializes all operations for the same `order_id`, preventing duplicate reservations and race conditions during release. repo://main.go#L87

## Test Coverage

The repository contains two test files that cover different layers:

- **`main_test.go`** — Fast unit tests for input validation (`validate`) and request fingerprinting (`fingerprint`). These run without a database. repo://main_test.go
- **`integration_test.go`** — A PostgreSQL-backed integration test that verifies concurrent reservations never oversell, exact replays succeed, conflicting replays fail, and double-release is idempotent. It skips unless `TEST_DATABASE_URL` is set. repo://integration_test.go

The Docker build runs `go test ./...` before producing the final binary, so the unit tests execute on every image build. repo://Dockerfile#L6

## Related Pages

- [HTTP API](api.md) — exact routes, request/response schemas, and status codes
- [Dependencies](dependencies.md) — runtime and compile-time dependency details
- [Database Schema](../data-model/schema.md) — table definitions, constraints, and locking strategy
- [Configuration and Deployment](../operations/configuration.md) — environment variables, Docker deployment, and timeouts
