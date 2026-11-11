---
type: reference
title: HTTP API — Provided Interfaces
description: Exact HTTP methods, routes, request/response JSON schemas, and status codes exposed by the CommerceLens inventory service.
tags: [http, api, endpoints, json, reference]
sources:
  - id: openwiki-source-29b4b6da030f0cb9e2e31279
    resource: repo://main.go
generated: { by: "openwiki/0.7.2", at: "2026-11-08T23:01:57.916Z" }
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T01:29:34.529Z
---

# HTTP API — Provided Interfaces

The inventory service exposes four HTTP endpoints on port `8080`. All successful responses and error bodies are JSON. The service does not accept prices from callers; prices are read from the database and returned authoritatively.

## Endpoint Overview

| Method | Route | Purpose |
|--------|-------|---------|
| `GET` | `/health` | Database readiness probe |
| `GET` | `/api/products` | List all products with current stock |
| `POST` | `/api/reservations` | Reserve stock for an order |
| `POST` | `/api/reservations/{orderId}/release` | Release (restore) reserved stock |

## Request Body Guards

`POST /api/reservations` applies three strict guards before decoding:

1. **Size limit** — `http.MaxBytesReader(w, r.Body, 65536)` rejects bodies larger than 64 KiB. repo://main.go#L222
2. **Unknown field rejection** — `json.NewDecoder` is configured with `DisallowUnknownFields`, so extra properties cause a `400`. repo://main.go#L224
3. **Single-object enforcement** — After the first decode, a second `Decode(&struct{}{})` is attempted. If it does not return `io.EOF`, the body contained trailing data and the handler returns `400` with `expected one JSON object`. repo://main.go#L230-L232

The release endpoint does not read a request body.

## GET /health

Returns database readiness with a 2-second ping timeout.

**Handler** (`Store.handler`, lines 204–212): repo://main.go#L204-L212

### Response

```json
{ "status": "ok" }
```

| Status | Meaning |
|--------|---------|
| `200` | PostgreSQL is reachable |
| `503` | Ping failed or unexpected error (`inventory temporarily unavailable`) |

## GET /api/products

Returns every row from `inventory_products` as a JSON array, ordered by SKU ascending.

**Handler** (`Store.handler`, lines 213–220): repo://main.go#L213-L220

### Response Schema

```json
[
  {
    "sku": "BOOK-001",
    "name": "Agentic Systems Handbook",
    "priceCents": 2900,
    "available": 100
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `sku` | `string` | Product SKU (primary key) |
| `name` | `string` | Display name |
| `priceCents` | `int64` | Price in whole cents (always > 0) |
| `available` | `int` | Units currently in stock |

| Status | Meaning |
|--------|---------|
| `200` | Success |
| `503` | Database or unexpected error |

## POST /api/reservations

Reserves stock for the items in a request. The response includes authoritative prices, a subtotal, and the reservation status.

**Handler** (`Store.handler`, lines 221–242): repo://main.go#L221-L242

### Request Schema

```json
{
  "orderId": "order-42",
  "items": [
    { "sku": "BOOK-001", "quantity": 2 }
  ]
}
```

| Field | Type | Constraints |
|-------|------|-------------|
| `orderId` | `string` | Required, 1–100 characters |
| `items` | `array` of `Item` | Required, 1–100 elements, distinct SKUs |

`Item` structure:

| Field | Type | Constraints |
|-------|------|-------------|
| `sku` | `string` | Required, non-empty, 1–100 characters, distinct within the request |
| `quantity` | `int` | 1–1000 |

### Response Schema

```json
{
  "orderId": "order-42",
  "items": [
    {
      "sku": "BOOK-001",
      "name": "Agentic Systems Handbook",
      "quantity": 2,
      "priceCents": 2900
    }
  ],
  "subtotalCents": 5800,
  "status": "reserved"
}
```

`ReservedItem` fields:

| Field | Type | Description |
|-------|------|-------------|
| `sku` | `string` | SKU from the item |
| `name` | `string` | Product name from the database |
| `quantity` | `int` | Reserved quantity |
| `priceCents` | `int64` | Authoritative price from the database |

`Reservation` fields:

| Field | Type | Description |
|-------|------|-------------|
| `orderId` | `string` | Caller-provided order ID |
| `items` | `array` of `ReservedItem` | One element per requested SKU |
| `subtotalCents` | `int64` | Sum of `priceCents * quantity` for all items |
| `status` | `string` | `"reserved"` |

### Status Codes

| Status | Cause |
|--------|-------|
| `200` | New reservation created or exact idempotent replay |
| `400` | Invalid JSON, unknown fields, trailing data, or validation failure (`orderId`/item/SKU/quantity rules) |
| `404` | Requested SKU does not exist |
| `409` | Insufficient stock, or a reservation already exists with different items, or the order was already released |
| `503` | Database or unexpected error |

## POST /api/reservations/{orderId}/release

Restores all reserved stock for the given `orderId` and marks the reservation as `released`. The operation is idempotent: releasing an already-released reservation returns `200` without changing data.

**Handler** (`Store.handler`, lines 243–251): repo://main.go#L243-L251

### Path Parameter

| Parameter | Description |
|-----------|-------------|
| `orderId` | The order ID used when the reservation was created |

### Response

```json
{ "status": "released" }
```

### Status Codes

| Status | Cause |
|--------|-------|
| `200` | Stock restored, or was already released (idempotent) |
| `404` | No reservation found for the given `orderId` |
| `503` | Database or unexpected error |

## Error Response Format

All error responses share this shape:

```json
{ "message": "<human-readable reason>" }
```

Validation and structural errors return `400`. Business-logic errors (unknown SKU, not found, conflict) return `4xx`. Any non-`APIError` failure (database outage, unexpected panic) is logged server-side and returned as `503 inventory temporarily unavailable` through the `fail()` helper. repo://main.go#L193-L200

## Data Types Reference

| Struct | JSON Type | Source |
|--------|-----------|--------|
| `Item` | `{ "sku": string, "quantity": int }` | repo://main.go#L22-L25 |
| `ReserveRequest` | `{ "orderId": string, "items": Item[] }` | repo://main.go#L26-L29 |
| `Product` | `{ "sku": string, "name": string, "priceCents": int64, "available": int }` | repo://main.go#L30-L35 |
| `ReservedItem` | `{ "sku": string, "name": string, "quantity": int, "priceCents": int64 }` | repo://main.go#L36-L41 |
| `Reservation` | `{ "orderId": string, "items": ReservedItem[], "subtotalCents": int64, "status": string }` | repo://main.go#L42-L47 |

## Related Pages

- [Service Overview](overview.md)
- [Reservation Flow](../runtime/reservation-flow.md)
- [Release Flow](../runtime/release-flow.md)
- [Database Schema](../data-model/schema.md)
- [Test Coverage](../testing/coverage.md)
