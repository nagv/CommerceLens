---
type: guide
title: Quickstart
description: >
  Quick-start guide for running the CommerceLens customer portal locally,
  navigating the repository, and finding deeper documentation across
  architecture, workflows, operations, and testing.
tags: [quickstart, react, vite, docker, local-development, commercelens]
sources:
  - id: openwiki-source-bb1ebe868e35e9e500714501
    resource: repo://Dockerfile
  - id: openwiki-source-f8d10828394c4129061d5b0e
    resource: repo://index.html
  - id: openwiki-source-5b54a58d1b51cd490b0e7162
    resource: repo://package.json
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-9d47595c2a2ea0b2c9b2cc8d
    resource: repo://src/api.ts
  - id: openwiki-source-5e8484dc0b3fa8bdb35ced77
    resource: repo://src/domain.ts
  - id: openwiki-source-95bfccfd0c712f6e72040e0d
    resource: repo://src/main.tsx
  - id: openwiki-source-5e1b077422a94ae165e88e4e
    resource: repo://vite.config.ts
generated: { by: "openwiki/0.7.2", at: "2026-11-08T23:02:37.496Z" }
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T01:28:21.917Z
---

# Quickstart

The **CommerceLens customer portal** is a React 19 + Vite storefront and operations UI. It runs entirely in the browser as a single-page application, consumes backend APIs over HTTP, and is designed for local sandbox development.

## Repository layout

| Path | Role |
|------|------|
| [`index.html`](repo://index.html) | HTML shell that loads the React application |
| [`src/main.tsx`](repo://src/main.tsx) | Application root — renders the storefront and operations tabs |
| [`src/domain.ts`](repo://src/domain.ts) | Pure domain functions and TypeScript types |
| [`src/api.ts`](repo://src/api.ts) | Thin fetch wrapper with timeout and error handling |
| [`src/domain.test.ts`](repo://src/domain.test.ts) | Vitest unit tests for domain logic |
| [`Dockerfile`](repo://Dockerfile) | Multi-stage build and runtime image |
| [`nginx.conf`](repo://nginx.conf) | Reverse proxy rules for the production container |
| [`vite.config.ts`](repo://vite.config.ts) | Development server and API proxy configuration |

## Run locally

You need Node 24. Clone the repository, then:

```sh
npm ci      # install dependencies
npm test    # run Vitest unit tests
npm run dev # start Vite dev server on 127.0.0.1
```

The dev server proxies API calls for you:
- `/api` → `http://127.0.0.1:8080` (order/catalog services)
- `/api/notifications` → `http://127.0.0.1:8085` (notification worker)

See [`vite.config.ts`](repo://vite.config.ts) if your local backend ports differ.

To create a production build:

```sh
npm run build
```

This runs `tsc -b` for type checking, then `vite build` to emit static assets into `dist/`.

## Build with Docker

The project ships a multi-stage `Dockerfile`:

1. **Build stage** — installs dependencies, runs tests, and produces the production bundle.
2. **Runtime stage** — copies the bundle into an nginx image and exposes port 80.

```sh
docker build -t commercelens-portal .
```

For full deployment details, read [Deployment and Infrastructure](operations/deployment.md).

## Where to go next

- **[Service Context](service-context.md)** — Service identity, consumed APIs, checkout and operations flows, failure behavior, and session lifecycle.
- **[API Client](architecture/api-client.md)** — How `request()` wraps `fetch`, handles timeouts, parses JSON, reports errors, and carries `Idempotency-Key`.
- **[Domain Models](architecture/domain-models.md)** — `cartSummary`, `validateCheckout`, `checkoutAttempt`, `money`, and their invariants.
- **[User Checkout Flow](workflows/user-checkout.md)** — End-to-end checkout from browsing through cart management, validation, submission, retry, and result display.
- **[Operations Monitoring Flow](workflows/operations-monitoring.md)** — The Operations tab, order history, notification delivery records, and refresh behavior.
- **[Deployment and Infrastructure](operations/deployment.md)** — Docker multi-stage build, nginx routing, health checks, and development proxy.
- **[Testing and Verification](testing/verification.md)** — Domain unit tests, build-time type checking, and Docker CI verification.
