---
type: operations
title: Configuration, Deployment, and Observability
description: Environment variables, Docker deployment, timeout settings, and health check behavior for the inventory service.
tags: [operations, deployment, docker, environment-variables]
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

# Configuration, Deployment, and Observability

## Environment Variables

| Variable | Required? | Purpose |
|----------|-----------|---------|
| `DATABASE_URL` | Yes | PostgreSQL connection string used at runtime. The service exits on startup if it is unset. |
| `TEST_DATABASE_URL` | No | Disposable PostgreSQL database used only by integration tests. When set, tests verify concurrent reservation behavior and idempotent releases. |

## Docker Deployment

The repository provides a multi-stage [Dockerfile](../../Dockerfile).

1. **Build stage** (`golang:1.23-alpine`): downloads modules, copies the source, runs `go test ./...`, and produces a statically linked binary named `inventory`.
2. **Runtime stage** (`alpine:3.21`): installs `ca-certificates`, creates an unprivileged `app` user, copies the binary from the build stage, exposes port `8080`, and launches the binary as `ENTRYPOINT ["/inventory"]`.

Set `DATABASE_URL` when running the container; the service initializes its schema on startup and listens on `:8080`.

## Observability

### Health Check

`GET /health` ([Service API](../service/api.md)) queries database readiness by calling `Ping` against the connection pool with a **2-second** context timeout. On success it returns HTTP 200 and `{"status":"ok"}`. On failure it returns HTTP 503.

### Error Handling and Logging

Unexpected errors (those that are not `APIError` values) are logged with `log.Printf` and surfaced to the client as HTTP 503 `{"message":"inventory temporarily unavailable"}`. This provides minimal runtime visibility without structured logging.

### What Is Not Configured

No metrics, request tracing, or structured logging are currently instrumented.

## Server and Handler Timeouts

The HTTP server is configured with the following timeouts:

| Timeout | Value |
|---------|-------|
| `ReadHeaderTimeout` | 5 s |
| `ReadTimeout` | 10 s |
| `WriteTimeout` | 10 s |
| `IdleTimeout` | 30 s |

Individual route contexts apply additional handler timeouts:

- **`GET /health`**: a 2-second context deadline for the `Ping` call.
- **`POST /api/reservations`**: a 5-second context deadline.
- **`POST /api/reservations/{id}/release`**: a 5-second context deadline.

## Related Pages

- [Service API](../service/api.md) — endpoint contracts and behavior
- [Service Dependencies](../service/dependencies.md) — runtime dependency details
- [Service Overview](../service/overview.md) — high-level service responsibilities
