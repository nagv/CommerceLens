---
type: Service Context
title: Service Context
description: >
  CommerceLens customer portal identity, consumed dependencies, checkout and operations
  flows, failure behavior, session lifecycle, and operational configuration.
tags: [frontend, react, commerce, checkout, nginx, vite]
sources:
  - id: openwiki-source-bb1ebe868e35e9e500714501
    resource: repo://Dockerfile
  - id: openwiki-source-f8d10828394c4129061d5b0e
    resource: repo://index.html
  - id: openwiki-source-ca698d0db8d141f7e7059df0
    resource: repo://nginx.conf
  - id: openwiki-source-5b54a58d1b51cd490b0e7162
    resource: repo://package.json
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-9d47595c2a2ea0b2c9b2cc8d
    resource: repo://src/api.ts
  - id: openwiki-source-10b9c8d78c84abf3aa463c75
    resource: repo://src/domain.test.ts
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

# Service Context

## Identity and role

The **CommerceLens customer portal** is a React 19 single-page application built with Vite. It is a **consumer-only browser frontend**, not a backend service. Its purpose is to provide a UI for a local CommerceLens sandbox where users browse products, place demo orders, and inspect order and notification history.

Entry points:

- `index.html` — the HTML shell that loads `src/main.tsx` [`repo://index.html#L1-L6`](repo://index.html#L1-L6)
- `src/main.tsx` — the React application root rendered with `createRoot` in strict mode [`repo://src/main.tsx#L1-L73`](repo://src/main.tsx#L1-L73)

The application runs in **demo provider mode**: payment, shipping, and email are local HTTP mocks. No real charge or message is sent.

## Provided interfaces

The portal does not expose any programmatic interface. Instead, it consumes backend HTTP APIs and renders their data in the browser. The UI communicates with the following endpoints (schemas follow the [`domain.ts`](repo://src/domain.ts) types and actual usage in [`main.tsx`](repo://src/main.tsx)):

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/products` | Returns live inventory; rendered as the product catalog. |
| `POST` | `/api/orders` | Creates an order. The frontend sends `Idempotency-Key` in the request headers and a [`Checkout`](repo://src/domain.ts#L2) payload. |
| `GET` | `/api/orders` | Retrieves order history, displayed in the Operations tab. |
| `GET` | `/api/orders/{id}` | Retrieves a single order’s details, including tracking, payment state, and failure reasons. |
| `GET` | `/api/notifications` | Retrieves notification delivery records, shown alongside orders. |

### Key request and response schemas

A `POST /api/orders` request body is a [`Checkout`](repo://src/domain.ts#L2):

| Field | Type | Notes |
|-------|------|-------|
| `customerEmail` | `string` | Must be a well-formed email. |
| `postalCode` | `string` | Trimmed; blank or over 20 chars is rejected. |
| `items` | `{sku,quantity}[]` | At least one item; quantities must be positive integers and within stock. |
| `paymentScenario` | `'success' | 'decline' | 'timeout'` | Controls demo payment outcome. |
| `shippingScenario` | `'success' | 'failure'` | Controls demo shipping outcome. |

The response is an [`Order`](repo://src/domain.ts#L4):

| Field | Type | Notes |
|-------|------|-------|
| `id` | `string` | Order identifier. |
| `status` | `string` | Examples: `CONFIRMED`, `PAYMENT_FAILED`. |
| `items` | `{sku, quantity, name?, priceCents?}[]` | Populated by the service. |
| `subtotalCents` | `number` | Authoritative values from the backend. |
| `shippingCents` | `number` | |
| `totalCents` | `number` | |
| `paymentId?` | `string` | Present when payment was processed. |
| `trackingNumber?` | `string` | Present when a shipment was created. |
| `failureReason?` | `string` | Reason when an order did not succeed. |
| `createdAt` | `string` | ISO timestamp. |

### Domain utilities

[`src/domain.ts`](repo://src/domain.ts) defines types and helper functions used across the UI:

- [`cartSummary`](repo://src/domain.ts#L6-L11) — computes subtotal, shipping, total, and count from products and a cart dict. Client prices are **never submitted** as authoritative values.
- [`validateCheckout`](repo://src/domain.ts#L12-L22) — validates email, postal code, item quantities, and stock availability.
- [`checkoutAttempt`](repo://src/domain.ts#L23-L25) — generates or reuses a tab-scoped idempotency key and payload.
- [`money`](repo://src/domain.ts#L26) — formats cents as USD currency.

## Business flow

<!-- openwiki: mermaid parse failed and this diagram was converted to a text fence so it does not break rendering. Fix the diagram source and restore the mermaid fence. Parser error: Heuristic: a semicolon inside a label breaks rendering; rephrase the label. -->
```text
flowchart TD
    A[User browses storefront] --> B[Add items to cart]
    B --> C[Email, postal code, and scenario selection]
    C --> D[Validate checkout on demand]
    D --> E[Save Idempotency-Key + payload in sessionStorage]
    E --> F[POST /api/orders with key]
    F --> G{Response?}
    G --|ok|--> H[Display order status and tracking]
    G --|error with order|--> I[Show order details + explain error]
    G --|network failure|--> J[Warn unknown outcome; offer retry]
    H --> K[Operations tab: order history + notification records]
    I --> K
    J --> K
```

The user starts by browsing the product catalog. Adding items increments cart quantities; setting a quantity to zero removes the item. Before submission, validation ensures:

- At least one item is present.
- The email matches a simple regex (`/^[^\s@]+@[^\s@]+\.[^\s@]+$/`).
- The postal code is 1–20 characters after trimming.
- Quantities are positive integers and do not exceed available stock.

The checkout form includes hidden expandable **scenario controls** that let the user simulate a successful payment, declined payment, payment timeout, or shipping failure. If the email contains `fail-email`, the backend tests notification retries and dead-letter behavior.

When the user places the order, the frontend persists an [`Attempt`](repo://src/domain.ts#L3) — a UUID `key` plus the [`Checkout`](repo://src/domain.ts#L2) payload — to tab-scoped `sessionStorage` under the key `commercelens.checkout.v1` [`repo://src/main.tsx#L7-L8`](repo://src/main.tsx#L7-L8). Retries and page refreshes reuse the same payload and idempotency key. Inputs remain locked until the user explicitly starts a new order.

The **Operations** tab displays order history and notification delivery records. Refresh queries all three services again.

## Consumed dependencies

Backend services are reached via a reverse proxy. There are no runtime environment secrets in the repository; all service URLs are baked into the proxy configuration.

| Direction | Relationship | Target | Interface / Topic | Config variable | Evidence | Certainty |
|-----------|-------------|--------|-------------------|-----------------|----------|-----------|
| Consumes | HTTP proxy | order-service | `/api/products`, `/api/orders`, `/api/orders/{id}` | `vite.config.ts` server proxy; `nginx.conf` location | [`repo://vite.config.ts#L2`](repo://vite.config.ts#L2), [`repo://nginx.conf#L9-L10`](repo://nginx.conf#L9-L10) | High |
| Consumes | HTTP proxy | notification-worker | `/api/notifications` | `vite.config.ts` server proxy; `nginx.conf` location | [`repo://vite.config.ts#L2`](repo://vite.config.ts#L2), [`repo://nginx.conf#L9`](repo://nginx.conf#L9) | High |

### Development proxy

[`vite.config.ts`](repo://vite.config.ts) proxies local dev-server paths:

- `/api/notifications` → `http://127.0.0.1:8085`
- `/api` → `http://127.0.0.1:8080`

### Production proxy

[`nginx.conf`](repo://nginx.conf#L1-L12) runs inside the container and proxies:

- `/api/notifications` → `http://notification-worker:8080`
- `/api/` → `http://order-service:8080`

Static SPA routing uses `try_files` so React Router-style paths fall back to `index.html`.

## Failure behavior

### Request timeouts

Browser `fetch` requests abort after **30 s** using `AbortSignal.timeout(30000)` [`repo://src/api.ts#L5`](repo://src/api.ts#L5). The nginx upstream is configured with `proxy_read_timeout 35s`, giving the backend slightly more headroom than the client before the browser gives up [`repo://nginx.conf#L9-L10`](repo://nginx.conf#L9-L10).

### Network and error responses

POST errors may still carry a partial order payload. The frontend checks the error body for an `order` property or `id` plus `status` and, if present, surfaces those details to the user [`repo://src/main.tsx#L41-L42`](repo://src/main.tsx#L41-L42). Network interruptions are described as *unknown outcomes*, not declines.

### Session recovery and idempotency

Tab-scoped `sessionStorage` preserves the [`Attempt`](repo://src/domain.ts#L3). If the user refreshes the page, `savedAttempt()` restores the key and payload from `commercelens.checkout.v1` [`repo://src/main.tsx#L8`](repo://src/main.tsx#L8). Retries resend the identical payload with the same `Idempotency-Key` header, so the backend can deduplicate.

Starting a new order triggers a confirmation dialog that warns the user to check order history first because a previous payment may still be pending [`repo://src/main.tsx#L47`](repo://src/main.tsx#L47).

### Notification service unavailability

An unavailable notification worker does **not** block checkout. On startup / refresh, the UI fires all three requests in parallel via `Promise.allSettled` and only shows soft warnings for individual failures [`repo://src/main.tsx#L17-L25`](repo://src/main.tsx#L17-L25).

## Configuration and observability

### Health checks

The Dockerfile defines an HTTP health check: `wget -q -O /dev/null http://127.0.0.1/health || exit 1` with a 15 s interval and 3 s timeout [`repo://Dockerfile#L12`](repo://Dockerfile#L12). The nginx configuration returns `{"status":"ok"}` from `GET /health` on port 80 [`repo://nginx.conf#L8`](repo://nginx.conf#L8). This reports **frontend availability only**, not downstream dependency health.

### Build pipeline

The multi-stage `Dockerfile` [`repo://Dockerfile#L1-L12`](repo://Dockerfile#L1-L12):

1. Builds from `node:24-alpine`: installs dependencies, runs tests, and produces the Vite dist.
2. Copies the dist into `nginx:stable-alpine` alongside `nginx.conf`.
3. Exposes port 80 and runs the health check.

Local development commands (from `README.md`):

```sh
npm ci
npm test
npm run build
npm run dev
```

`npm test` (Vitest) covers cart calculations, input/stock validation, and stable idempotency retry behavior [`repo://src/domain.test.ts`](repo://src/domain.test.ts). `npm run build` type-checks TypeScript and generates production assets.

### Loading and error states

The UI surfaces load errors as non-blocking banner warnings. For example, if the notification worker is down, the banner says: *"Notification worker unavailable. Orders can still be placed."* [`repo://src/main.tsx#L23`](repo://src/main.tsx#L23). Form-level errors and success notices appear below the header.

## Related pages

- [API Client](architecture/api-client.md) — describes the `request` helper and `ApiError` class.
- [Domain Models](architecture/domain-models.md) — covers `Product`, `Checkout`, `Order`, and `Notification` in detail.
- [User Checkout](workflows/user-checkout.md) — end-to-end checkout user journey.
- [Deployment](operations/deployment.md) — container and runtime deployment information.
