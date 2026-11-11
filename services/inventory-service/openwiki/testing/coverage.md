---
type: testing-coverage
title: Tests and Invariants
description: Test suite structure, build-time execution, and the inventory invariants enforced by unit and integration tests.
tags: [testing, coverage, invariants, idempotency, postgresql]
sources:
  - id: openwiki-source-bb1ebe868e35e9e500714501
    resource: repo://Dockerfile
  - id: openwiki-source-1bebaeef76eb2a89dea06f8d
    resource: repo://integration_test.go
  - id: openwiki-source-569e5a25197cee8330354b08
    resource: repo://main_test.go
  - id: openwiki-source-29b4b6da030f0cb9e2e31279
    resource: repo://main.go
generated: { by: "openwiki/0.7.2", at: "2026-11-08T23:01:57.916Z" }
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T01:29:34.529Z
---

# Tests and Invariants

The inventory service is tested at two levels: fast unit tests for input validation and request hashing, and a PostgreSQL-backed integration test that exercises concurrency, idempotency, and stock correctness. Tests run automatically during the Docker build.

## Build-Time Execution

The [`Dockerfile`](../../Dockerfile) includes `go test ./...` in the build stage before compiling the binary:

```dockerfile
RUN go test ./... && CGO_ENABLED=0 go build -o /inventory .
```

This means unit tests execute at image-build time and will fail the build if they do not pass. Integration tests are gated on the `TEST_DATABASE_URL` environment variable and skip when it is absent.

## Unit Tests

Unit tests live in `main_test.go` and exercise pure functions with no external dependencies.

### `TestValidateRejectsInvalidAndDuplicateItems`

Lines 5–11 in `main_test.go` verify that `validate()` rejects malformed `ReserveRequest` payloads. The test loops over four invalid item sets and asserts that `validate` returns an error for each:

- Empty items slice.
- Item with quantity `0`.
- Item with negative quantity (`-1`).
- Duplicate SKUs (`BOOK-001` appears twice with different quantities).

The test instantiates `ReserveRequest` directly, so it also implicitly covers the empty-`orderId` and length checks (`orderId` is supplied in the struct literal and is valid).

### `TestFingerprintIndependentOfItemOrder`

Lines 13–23 in `main_test.go` verify the deterministic request-fingerprint function used for idempotency:

- Two requests with the same `orderId` and the same items in **different order** produce the **same fingerprint**.
- Changing the quantity of one item produces a **different fingerprint**.

This confirms that `fingerprint()` sorts items by SKU before hashing with SHA-256 (see `main.go` lines 67–73) so callers are not affected by JSON field ordering.

## Integration Test

`integration_test.go` contains a single end-to-end test that requires a live PostgreSQL database.

### Environment and Setup

The test reads `TEST_DATABASE_URL` from the environment. If the variable is missing, the test is skipped. Otherwise, it:

1. Opens a `pgxpool` connection.
2. Applies the service schema (`CREATE TABLE` statements from `main.go`).
3. Creates a disposable product with stock `5` using a unique SKU based on the current Unix timestamp: `fmt.Sprintf("TEST-%d", time.Now().UnixNano())`.
4. Registers `defer` cleanup for both the product row and any reservation rows created during the test.

### `TestPostgresReservationsNeverOversellAndReleaseIsIdempotent`

Lines 14–82 in `integration_test.go` perform the following steps.

#### Concurrent Reservation Stress Test

- Spawns 20 goroutines, each attempting to reserve a single unit of the test product.
- Waits for all goroutines to complete.
- Asserts that **exactly 5** reservations succeed (`successes.Load() == 5`).
- Queries `inventory_products.available` and asserts it is `0`.

This verifies that PostgreSQL row-level locks (`FOR UPDATE` on `inventory_products` selected in SKU order) prevent overselling under concurrent load.

#### Idempotent Replay

- Picks one successful reservation by `order_id`.
- Replays the **exact same** `ReserveRequest`; asserts that it succeeds without error.
- Modifies the quantity from `1` to `2` in the replay request; asserts that the conflicting replay is **rejected**.

This confirms the `request_hash` check and the order-level advisory lock correctly enforce reservation immutability.

#### Idempotent Release

- Calls `store.release(ctx, id)` once; asserts success.
- Calls `store.release(ctx, id)` a **second** time; asserts success again.
- Queries `inventory_products.available` and asserts it is exactly `1`.

This proves that release is idempotent: the second call is a no-op and does not restore stock twice.

## Invariants Enforced

| Invariant | Verified By | Evidence |
|-----------|-------------|----------|
| Invalid input is rejected before any database work | `TestValidateRejectsInvalidAndDuplicateItems` | `main_test.go` lines 5–11 |
| Fingerprint is order-independent | `TestFingerprintIndependentOfItemOrder` | `main_test.go` lines 13–23 |
| Concurrent reservations cannot oversell | `TestPostgresReservationsNeverOversellAndReleaseIsIdempotent` | `integration_test.go` lines 37–57 |
| Exact replay returns the cached reservation | `TestPostgresReservationsNeverOversellAndReleaseIsIdempotent` | `integration_test.go` lines 58–65 |
| Conflicting replay is rejected | `TestPostgresReservationsNeverOversellAndReleaseIsIdempotent` | `integration_test.go` lines 66–69 |
| Release is idempotent (stock restored exactly once) | `TestPostgresReservationsNeverOversellAndReleaseIsIdempotent` | `integration_test.go` lines 70–81 |

## Related Pages

- [Database Schema](../data-model/schema.md)
- [Reservation Flow](../runtime/reservation-flow.md)
- [Release Flow](../runtime/release-flow.md)
- [HTTP API](../service/api.md)
