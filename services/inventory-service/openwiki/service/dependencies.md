---
type: dependencies
title: Dependencies and Integration Points
description: Runtime and compile-time dependencies of the inventory service, including PostgreSQL connectivity via pgx/v5 and the absence of external HTTP or message queue integrations.
tags: [dependencies, postgresql, pgx, go-modules, integration-tests]
sources:
  - id: openwiki-source-bb1ebe868e35e9e500714501
    resource: repo://Dockerfile
  - id: openwiki-source-7bd911fdd3026b7b031a01e3
    resource: repo://go.mod
  - id: openwiki-source-1bebaeef76eb2a89dea06f8d
    resource: repo://integration_test.go
  - id: openwiki-source-29b4b6da030f0cb9e2e31279
    resource: repo://main.go
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
generated: { by: "openwiki/0.7.2", at: "2026-11-08T23:01:57.916Z" }
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T01:29:34.529Z
---

# Dependencies and Integration Points

The inventory service maintains a minimal external footprint. At runtime it consumes only PostgreSQL, accessed through the `jackc/pgx/v5` driver and connection pool. It exposes an HTTP API on port 8080. There are no outbound HTTP calls, event brokers, caches, message queues, or external business providers.

## Dependency Table

| Direction | Relationship Type | Target Identifier | Interface/Topic | Configuration Variable | Supporting Evidence | Certainty |
|-----------|-------------------|-------------------|-----------------|------------------------|---------------------|-----------|
| Consumed | Runtime | PostgreSQL (≥ version compatible with pgx v5) | TCP/Unix socket, SQL via pgxpool | `DATABASE_URL` (runtime), `TEST_DATABASE_URL` (tests) | `repo://main.go#L18-L19`, `repo://main.go#L259-L266`, `repo://integration_test.go#L15-L18`, `repo://README.md#L16-L22` | Confirmed |
| Consumed | Compile-time (direct) | `github.com/jackc/pgx/v5 v5.7.2` | Go package import (database driver & pool) | none | `repo://go.mod#L5` | Confirmed |
| Consumed | Compile-time (transitive) | `github.com/jackc/pgpassfile v1.0.0` | Go package import | none | `repo://go.mod#L8` | Confirmed |
| Consumed | Compile-time (transitive) | `github.com/jackc/pgservicefile v0.0.0-20240606120523-5a60cdf6a761` | Go package import | none | `repo://go.mod#L9` | Confirmed |
| Consumed | Compile-time (transitive) | `github.com/jackc/puddle/v2 v2.2.2` | Go package import | none | `repo://go.mod#L10` | Confirmed |
| Consumed | Compile-time (transitive) | `golang.org/x/crypto v0.31.0` | Go package import | none | `repo://go.mod#L11` | Confirmed |
| Consumed | Compile-time (transitive) | `golang.org/x/sync v0.10.0` | Go package import | none | `repo://go.mod#L12` | Confirmed |
| Consumed | Compile-time (transitive) | `golang.org/x/text v0.21.0` | Go package import | none | `repo://go.mod#L13` | Confirmed |
| Provided | Runtime | Inventory Service HTTP API | JSON over HTTP, port 8080 | none | `repo://main.go#L202-L252`, `repo://Dockerfile#L11` | Confirmed |

The standard Go library packages (`net/http`, `crypto/sha256`, `encoding/json`, etc.) are used but are not listed as external targets because they ship with the Go toolchain.

### Runtime Dependency Details

PostgreSQL is the only external system the service contacts at runtime. On startup `main()` reads `DATABASE_URL` from the environment, creates a `pgxpool.Pool`, and uses it for all subsequent queries including health checks, product listings, reservations, and releases. If `DATABASE_URL` is unset the process exits immediately.

### Compile-time Dependency Details

All non-standard dependencies are introduced by the single direct requirement `github.com/jackc/pgx/v5`. The transitive modules handle PostgreSQL password files, service files, connection pooling, cryptography, synchronization primitives, and text encoding. These are compile-time dependencies only; they are statically linked into the binary produced by the Docker build.

### Integration Tests Require a Real Database

The integration test suite has no mocks for PostgreSQL. `TestPostgresReservationsNeverOversellAndReleaseIsIdempotent` skips unless `TEST_DATABASE_URL` is set, then creates a live `pgxpool`, initializes the schema, runs concurrent goroutines against the real database, and validates stock counts with SQL queries. Tests must target a disposable database because they create and delete transient fixture rows.

### Absent Dependencies

The codebase does not contain integrations with:

- Outbound HTTP clients (other than the server-side `net/http` handler)
- Message queues or event brokers
- In-memory caches
- External business providers or LLM services
- Any database other than PostgreSQL

This is confirmed by inspection of `main.go` and `go.mod`: no imports or module requirements exist for such systems.

## Related Pages

- [Configuration and Deployment](../operations/configuration.md) — environment variable details and Docker deployment
- [Database Schema](../data-model/schema.md) — PostgreSQL tables and locking strategy
- [Service API](../service/api.md) — HTTP endpoint contracts
