---
type: testing-strategy
title: Testing Strategy
description: Unit tests for the checkout saga using FakePorts and integration tests for OrderStore idempotency against PostgreSQL. Describes test structure, environment requirements, and failure-invariant verification.
tags: [testing, checkout, integration-tests, unit-tests, postgresql]
sources:
  - id: openwiki-source-bb1ebe868e35e9e500714501
    resource: repo://Dockerfile
  - id: openwiki-source-7fc81aadbff6a8f3966ae5d8
    resource: repo://src/main/java/com/commercelens/orders/Checkout.java
  - id: openwiki-source-108cb54cf02515bb6eae368e
    resource: repo://src/main/java/com/commercelens/orders/OrderStore.java
  - id: openwiki-source-2995ce030e79da17d6712043
    resource: repo://src/main/resources/schema.sql
  - id: openwiki-source-ee4d53553f132f0e92588af5
    resource: repo://src/test/java/com/commercelens/orders/CheckoutTest.java
  - id: openwiki-source-4b0a0ba7c029fed22eb0542d
    resource: repo://src/test/java/com/commercelens/orders/OrderStoreTest.java
generated: { by: "codex/openwiki-lifecycle-review", at: "2026-11-08T23:17:43.833Z" }
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T01:28:27.799Z
---

# Testing Strategy

The project uses two complementary test groups to verify the [checkout saga](../architecture/checkout-saga.md) and its persistence layer:

* **Unit tests** (`CheckoutTest`) exercise the saga orchestrator in memory with a mock `Ports` implementation.
* **Integration tests** (`OrderStoreTest`) validate idempotency and concurrent-safety guarantees against a real PostgreSQL database.

Both groups are executed by `mvn verify` during the build.

---

## Unit Tests: Checkout Saga with FakePorts

`CheckoutTest` mocks the `Checkout.Ports` interface with `FakePorts`—a lightweight, in-memory fake that controls failure points and records side effects. It is a unit-test mock, not a sandboxed integration with real external systems.

### FakePorts fields and semantics

`FakePorts` exposes the following tunable fields ([CheckoutTest.java#L51](repo://src/test/java/com/commercelens/orders/CheckoutTest.java#L51)):

| Field | Type | Effect |
|---|---|---|
| `paymentFailure` | `Checkout.RemoteFailure` | Thrown from `pay` to simulate payment errors |
| `shippingFailure` | `boolean` | When `true`, `ship` throws a `RemoteFailure` |
| `refundFailure` | `boolean` | When `true`, `refund` throws a `RemoteFailure` |
| `released` | `boolean` | Set by `release` to record inventory deallocation |
| `refunded` | `boolean` | Set by `refund` to record payment compensation |
| `shippingStatus` | `int` | HTTP status used by the thrown `RemoteFailure` from `ship` (default `422`) |

The default `FakePorts` succeeds on every operation except where a failure flag is explicitly set, which lets each test target exactly one code path.

### Test scenarios

Each `@Test` targets a specific saga branch and verifies failure invariants (resource accounting and status transitions) without involving real networks or databases. The production code under test is `Checkout.run(Order, Request)` ([Checkout.java#L39-L60](repo://src/main/java/com/commercelens/orders/Checkout.java#L39-L60)).

| Test | Line | Simulated condition | Expected outcome |
|---|---|---|---|
| `rejectsInvalidQuantitiesAndDuplicateSkus` | [CheckoutTest.java#L8](repo://src/test/java/com/commercelens/orders/CheckoutTest.java#L8) | Item with quantity `0` and duplicate SKU entries | `IllegalArgumentException` from `Checkout.validate` |
| `timeoutKeepsReservationForReconciliation` | [CheckoutTest.java#L14](repo://src/test/java/com/commercelens/orders/CheckoutTest.java#L14) | `paymentFailure` with status `504` (timeout) | Status `payment_unknown`; `released` remains `false` so reservation is retained |
| `declineReleasesReservation` | [CheckoutTest.java#L20](repo://src/test/java/com/commercelens/orders/CheckoutTest.java#L20) | `paymentFailure` with status `402` (declined) | Status `failed`; `released=true`; `refunded=false` |
| `paymentConflictRetainsReservationForReconciliation` | [CheckoutTest.java#L25](repo://src/test/java/com/commercelens/orders/CheckoutTest.java#L25) | `paymentFailure` with status `409` (provider conflict) | Status `payment_unknown`; neither `released` nor `refunded` |
| `shipmentFailureRefundsAndReleases` | [CheckoutTest.java#L30](repo://src/test/java/com/commercelens/orders/CheckoutTest.java#L30) | `shippingFailure=true` (status `422`) | Status `failed`; `released=true`; `refunded=true` |
| `failedCompensationRequiresManualReview` | [CheckoutTest.java#L35](repo://src/test/java/com/commercelens/orders/CheckoutTest.java#L35) | `shippingFailure=true` and `refundFailure=true` | Status `manual_review`; `released=true` (refund fails, but release still runs) |
| `uncertainShipmentRetainsPaymentAndReservation` | [CheckoutTest.java#L40](repo://src/test/java/com/commercelens/orders/CheckoutTest.java#L40) | `shippingFailure=true` with `shippingStatus=504` | Status `manual_review`; `refunded=false` and `released=false` because a timeout may mean the carrier already accepted the shipment |
| `successUsesAuthoritativePrices` | [CheckoutTest.java#L45](repo://src/test/java/com/commercelens/orders/CheckoutTest.java#L45) | All default success paths | Status `confirmed`; `totalCents=3400` (2900 item + 500 shipping) |

These tests encode the saga's core safety principle: *external effects are never retried blindly after uncertain outcomes*. Timeouts on payment or shipping leave resources held for manual reconciliation instead of releasing or refunding them automatically.

---

## Integration Tests: OrderStore Concurrent Idempotency

`OrderStoreTest` validates that PostgreSQL-level uniqueness on `idempotency_key` ([schema.sql#L3](repo://src/main/resources/schema.sql#L3)) is respected under concurrent load, and that the stored hash is retrievable afterward.

### `postgresAcceptsOnlyOneConcurrentIdempotencyKey`

This test ([OrderStoreTest.java#L15](repo://src/test/java/com/commercelens/orders/OrderStoreTest.java#L15)):

1. Requires a disposable PostgreSQL instance.
2. Spins up a fixed thread pool of **8 threads**.
3. Submits **20 concurrent `store.create(...)` calls** using the same idempotency key but different order IDs.
4. Asserts that **exactly 1 call succeeds** and the rest are rejected by the `ON CONFLICT(idempotency_key) DO NOTHING` guard ([OrderStore.java#L15](repo://src/main/java/com/commercelens/orders/OrderStore.java#L15)).
5. Verifies that `store.byKey(key).hash()` returns the expected hash string (`"same-hash"`).
6. Cleans up the inserted row in a `finally` block.

The test also uses `CheckoutTest.request()` as a factory for valid `Checkout.Order` instances, demonstrating shared test data between the unit and integration suites.

---

## Running the Tests

### Default build

```bash
mvn verify
```

`CheckoutTest` runs automatically as part of the standard test phase because it is a pure JUnit 5 test with no external dependencies.

### Integration-test environment

`OrderStoreTest` is **skipped** unless the following environment variables are set:

* `TEST_JDBC_URL` — JDBC connection string for a disposable PostgreSQL database
* `TEST_DB_USER`
* `TEST_DB_PASSWORD`

The test assumes it can run `schema.sql` ([OrderStoreTest.java#L18](repo://src/test/java/com/commercelens/orders/OrderStoreTest.java#L18)) against that database, create and delete rows, and therefore must be pointed at a schema that can be safely mutated.

### Container build

The [Dockerfile](repo://Dockerfile) performs both test groups during image creation:

```dockerfile
RUN mvn -q verify
```

([Dockerfile#L6](repo://Dockerfile#L6))

Because `verify` is executed at build time, both unit and integration tests must pass (or integration tests must be properly skipped when the database is absent) for the Docker image to be produced. In the current configuration, lacking the environment variables will cause the integration test to be skipped via `assumeTrue` rather than fail, so the build still succeeds.

---

## Related Topics

* [Checkout Saga](../architecture/checkout-saga.md) — the orchestration logic under test
* [Failure Handling](../workflows/failure-handling.md) — how the saga reacts to different error codes
* [Idempotency and Concurrency](../workflows/idempotency-and-concurrency.md) — guarantees enforced by `OrderStore` and verified by `OrderStoreTest`
