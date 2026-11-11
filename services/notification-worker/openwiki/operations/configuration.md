---
type: operations
title: Configuration and Operations
description: Reference for environment variables, Docker build, health checks, and runtime operational behavior of the notification worker.
tags: [docker, environment-variables, health, operations, configuration]
sources:
  - id: openwiki-source-bb1ebe868e35e9e500714501
    resource: repo://Dockerfile
  - id: openwiki-source-5b54a58d1b51cd490b0e7162
    resource: repo://package.json
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-d4189bbeecb62806cb297b5a
    resource: repo://src/main.ts
generated: { by: "openwiki/0.7.2", at: "2026-11-08T23:14:00.671Z" }
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T01:29:52.130Z
---

# Configuration and Operations

This page describes how to build, configure, and operate the notification worker, including the Docker image, available npm scripts, runtime endpoints, and the complete environment variable surface.

## Docker Multi-Stage Build

The `Dockerfile` uses two stages:

1. **Build stage** (`FROM node:22-alpine AS build`) installs all dependencies (including dev dependencies), copies source and test files, runs `npm test`, then compiles with `npm run build`.
2. **Runtime stage** (`FROM node:22-alpine AS runtime`) installs production dependencies only (`npm ci --omit=dev`), copies the compiled `dist/` artifacts from the build stage, switches to the non-root `node` user, and exposes port **8080**.

The final container starts with `node dist/main.js`.

For more on node lifecycle management and signal handling, see [Lifecycle](../concepts/lifecycle.md).

## Npm Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| `build` | `tsc` | Compiles TypeScript to `dist/` |
| `test` | `tsx --test test/*.test.ts` | Runs the test suite |
| `start` | `node dist/main.js` | Starts the compiled worker |

These scripts are used both locally and inside the Docker build.

## Health Check

`GET /health` returns:

- **HTTP 200** when the worker has initialized the database schema and established a RabbitMQ connection (consumer is active).
- **HTTP 503** while the worker is still starting or after the connection has been lost.

This lets orchestrators wait until the worker is genuinely ready before considering the container healthy.

## Notification Query Endpoint

`GET /api/notifications` returns the latest **100** persisted delivery rows as JSON. Each row contains:

```json
{
  "eventId": "<string>",
  "orderId": "<string>",
  "status": "<string>",
  "attempts": "<number>",
  "lastError": "<string|null>"
}
```

> ⚠️ **Security warning:** This endpoint is **unauthenticated**. It is intended only for local or private-network demonstration and should not be exposed publicly in production.

## Environment Variables

| Name | Required | Default | Purpose |
|------|----------|---------|---------|
| `DATABASE_URL` | **Yes** | — | PostgreSQL connection string used for delivery persistence |
| `RABBITMQ_URL` | No | `amqp://guest:guest@rabbitmq:5672` | AMQP connection string for the `order.confirmed` queue |
| `EMAIL_PROVIDER_URL` | No | `http://mock-provider:8080` | Base URL of the HTTP email provider |
| `PROVIDER_TIMEOUT_MS` | No | `3000` | Per-request HTTP timeout for provider calls (milliseconds) |
| `PORT` | No | `8080` | HTTP port for the worker's own health and notification endpoints |

### Mock Provider and Failure Path

The default `EMAIL_PROVIDER_URL` points to a local mock provider. When the mock is active, the recipient address **`fail-email@example.com`** triggers the failure path, forcing the delivery loop through its retry logic without affecting the underlying order.
