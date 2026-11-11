---
type: concept
title: Testing and Verification
description: >
  Test coverage for storefront domain logic, build-time TypeScript type checking,
  and the Docker CI verification pipeline.
tags: [testing, ci, typescript, vitest, docker, domain-logic]
sources:
  - id: openwiki-source-bb1ebe868e35e9e500714501
    resource: repo://Dockerfile
  - id: openwiki-source-5b54a58d1b51cd490b0e7162
    resource: repo://package.json
  - id: openwiki-source-10b9c8d78c84abf3aa463c75
    resource: repo://src/domain.test.ts
generated: { by: "openwiki/0.7.2", at: "2026-11-08T23:02:37.496Z" }
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T01:28:21.917Z
---

# Testing and Verification

The CommerceLens storefront verifies correctness through three layers: unit tests for the [domain layer](../architecture/domain-models.md) (via Vitest), build-time type checking (via the TypeScript compiler), and an integrated Docker build stage that fails the image if any check does not pass.

## Domain unit tests

The [`src/domain.test.ts`](repo://src/domain.test.ts) suite runs with Vitest and covers the pure functions in `src/domain.ts`: [`cartSummary`](repo://src/domain.ts#L6-L11), [`validateCheckout`](repo://src/domain.ts#L12-L22), and [`checkoutAttempt`](repo://src/domain.ts#L23-L25).

### `cartSummary`

Tests verify that `cartSummary` computes pricing internally from the trusted local product list rather than from caller-supplied prices. When the cart contains two units of a product priced at `2900` cents, the summary returns `subtotalCents: 5800`, `shippingCents: 500`, `totalCents: 6300`, and `count: 2` ([`src/domain.test.ts#L7-L8`](repo://src/domain.test.ts#L7-L8)). For an empty cart it returns all-zero values and no shipping ([`src/domain.test.ts#L9`](repo://src/domain.test.ts#L9)).

### `validateCheckout`

The guard returns human-readable error strings for each invalid condition:

- **Empty cart** — rejects a body with no items with the message *"Add a product to your cart."* ([`src/domain.test.ts#L12`](repo://src/domain.test.ts#L12)).
- **Invalid email** — rejects a malformed `customerEmail` field with *"Enter a valid email address."* ([`src/domain.test.ts#L13`](repo://src/domain.test.ts#L13)).
- **Out of stock** — rejects quantities exceeding the available inventory with *"Your cart exceeds available stock. Refresh the catalog."* ([`src/domain.test.ts#L14`](repo://src/domain.test.ts#L14)).
- **Non-whole quantity** — rejects fractional quantities with *"Quantities must be positive whole numbers."* ([`src/domain.test.ts#L15`](repo://src/domain.test.ts#L15)).

A fully valid body returns `null` ([`src/domain.test.ts#L16`](repo://src/domain.test.ts#L16)).

### `checkoutAttempt` and idempotency

When a previous attempt exists, `checkoutAttempt` reuses the same `Attempt` object rather than creating a new one, preserving the original `key` and body snapshot even if the caller later changes unrelated fields such as `postalCode` ([`src/domain.test.ts#L18-L22`](repo://src/domain.test.ts#L18-L22)). This guarantees idempotency across retries and avoids accidental mutation of the payload before the checkout completes.

## Build-time type checking

The TypeScript configuration in [`tsconfig.json`](repo://tsconfig.json) enables strict mode (`"strict": true`), `ESNext` modules, and React JSX compilation. It targets the `src` directory and produces no standalone emit (`"noEmit": true`).

The `build` script in [`package.json`](repo://package.json#L8) runs two commands in sequence:

```json
"build": "tsc -b && vite build"
```

- `tsc -b` (the build mode invocation of the TypeScript compiler) performs full-project type checking, including cross-module consistency, strict null checks, and excess property checks.
- `vite build` bundles the React application and emits optimized production assets under `dist/`.

Running `npm run build` therefore fails immediately if any type error exists anywhere in `src/`, before Vite begins production bundling.

## Test runner

Tests are executed with Vitest. The `test` script in [`package.json`](repo://package.json#L9) is:

```json
"test": "vitest run"
```

`vitest run` discovers `*.test.ts` files (including `src/domain.test.ts`), executes them, and exits with a non-zero status if any assertion fails.

## Docker CI verification

The [`Dockerfile`](repo://Dockerfile) assembles the storefront into an Nginx-served container, but it also treats the build stage itself as a continuous-integration gate. Stage order and commands are:

```dockerfile
FROM node:24-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY tsconfig.json index.html ./
COPY src ./src
RUN npm test && npm run build
```

Because [`RUN npm test && npm run build`](repo://Dockerfile#L7) is part of the image build graph, the Docker engine halts the entire image creation if the Vitest suite fails or if the TypeScript compiler reports type errors. There is no separate CI script or secondary `docker-compose` verification step; the act of building the image is the act of verifying the codebase.

After the build stage succeeds, a second stage copies the resulting `dist/` directory and an Nginx configuration into a production image:

```dockerfile
FROM nginx:stable-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
```

This multi-stage approach keeps the final image free of Node dependencies while ensuring that only artifacts that passed both tests and type checks are deployed.
