---
type: Workflow
title: Idempotency and Concurrency
description: End-to-end rules and guarantees for the POST /api/orders idempotency mechanism, including request canonicalization, database-level uniqueness enforcement, concurrent-race behavior, and the intentional blocking of replays for in-flight or uncertain states.
tags: [idempotency, concurrency, orders, postgresql, database, replay]
sources:
  - id: openwiki-source-7fc81aadbff6a8f3966ae5d8
    resource: repo://src/main/java/com/commercelens/orders/Checkout.java
  - id: openwiki-source-16a5a13276943dc522d2add4
    resource: repo://src/main/java/com/commercelens/orders/OrderController.java
  - id: openwiki-source-108cb54cf02515bb6eae368e
    resource: repo://src/main/java/com/commercelens/orders/OrderStore.java
  - id: openwiki-source-2995ce030e79da17d6712043
    resource: repo://src/main/resources/schema.sql
  - id: openwiki-source-4b0a0ba7c029fed22eb0542d
    resource: repo://src/test/java/com/commercelens/orders/OrderStoreTest.java
generated: { by: "openwiki/0.7.2", at: "2026-11-08T23:01:58.880Z" }
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T01:28:27.799Z
---

# Idempotency and Concurrency

The `POST /api/orders` endpoint guarantees exactly-once checkout saga execution per idempotency key. The mechanism spans three layers: HTTP header validation in `OrderController`, request canonicalization and hashing, and database-level uniqueness enforcement in PostgreSQL. No distributed locks or external caches are used.

---

## Idempotency-Key Header Rules

Every `POST /api/orders` request must include an `Idempotency-Key` header.

| Attribute | Value |
|---|---|
| Name | `Idempotency-Key` |
| Required | yes |
| Format | `^[A-Za-z0-9_-]{1,100}$` (1 to 100 letters, digits, hyphens, or underscores) |
| Failure | `400 Bad Request` with message if missing or malformed |

The controller validates the header before any body parsing or saga execution.

```java
if (key == null || !key.matches("^[A-Za-z0-9_-]{1,100}$")) {
    throw new IllegalArgumentException(
        "Idempotency-Key header required (1-100 letters, numbers, hyphens or underscores)");
}
```

**Relevant source:** `OrderController.create` (`repo://src/main/java/com/commercelens/orders/OrderController.java#L18-L19`).

---

## Request Canonicalization and Hashing

Before touching the database, `OrderController` computes a SHA-256 hash of a **canonical JSON representation** of the request body. Two semantically identical requests must yield the same hash even when their raw JSON ordering differs.

The canonicalization steps are:

1. **Sort items by `sku`** in ascending order.
2. **Materialize defaults** for optional `paymentScenario` and `shippingScenario` (both default to `"success"`).
3. **Serialize** the canonical `Checkout.Request` with `ObjectMapper` to JSON bytes.
4. **Digest** the bytes with `MessageDigest.getInstance("SHA-256")`.

```java
private String hash(Checkout.Request req) {
    var sorted = req.items().stream()
        .sorted(Comparator.comparing(Checkout.Item::sku))
        .toList();
    var canonical = new Checkout.Request(
        req.customerEmail(),
        req.postalCode(),
        sorted,
        Objects.requireNonNullElse(req.paymentScenario(), "success"),
        Objects.requireNonNullElse(req.shippingScenario(), "success"));
    return HexFormat.of().formatHex(
        MessageDigest.getInstance("SHA-256")
            .digest(json.writeValueAsBytes(canonical)));
}
```

**Relevant source:** `OrderController.hash` (`repo://src/main/java/com/commercelens/orders/OrderController.java#L25`).

This hash is stored alongside the idempotency key in the `orders` table and is used to distinguish safe replays from conflicting reuse of a key.

---

## Database-Level Idempotency

The `orders` table declares `idempotency_key` as `UNIQUE NOT NULL` (`repo://src/main/resources/schema.sql#L3`). `OrderStore.create` uses PostgreSQL's `ON CONFLICT ... DO NOTHING` to turn the unique constraint into an atomic insert-or-skip operation.

```java
public boolean create(Checkout.Order order, String key, String hash) {
    return jdbc.update(
        "INSERT INTO orders(id, idempotency_key, request_hash, body) " +
        "VALUES(?, ?, ?, ?::jsonb) " +
        "ON CONFLICT(idempotency_key) DO NOTHING",
        order.id, key, hash, encode(order)) == 1;
}
```

**Relevant source:** `OrderStore.create` (`repo://src/main/java/com/commercelens/orders/OrderStore.java#L15`).

- Returns `true` (1 row inserted) when the key is new.
- Returns `false` (0 rows affected) when the key already exists.

Because the conflict resolution happens inside a single SQL statement, concurrent duplicate submissions race at the database level. PostgreSQL serializes the conflicting inserts; exactly one transaction wins and the rest are safely rejected without application-level locking.

### Concurrent-Race Verification

`OrderStoreTest.postgresAcceptsOnlyOneConcurrentIdempotencyKey` verifies this directly against a real PostgreSQL instance:

- Spins up an 8-thread fixed executor.
- Submits 20 `Callable<Boolean>` tasks, all calling `store.create(...)` with the **same** idempotency key.
- Asserts that exactly **one** task returns `true`.
- Asserts the stored `request_hash` matches the shared value.

The test requires three environment variables:

| Variable | Purpose |
|---|---|
| `TEST_JDBC_URL` | JDBC URL of a writable test PostgreSQL database |
| `TEST_DB_USER` | Database username |
| `TEST_DB_PASSWORD` | Database password |

The test is skipped when `TEST_JDBC_URL` is absent.

**Relevant source:** `OrderStoreTest` (`repo://src/test/java/com/commercelens/orders/OrderStoreTest.java#L15-L26`).

---

## Replay Behavior

When `OrderStore.create` returns `false`, the controller falls back to `OrderStore.byKey(key)` and compares the stored hash with the incoming request hash.

### Same request replay (hash matches)

The existing order is returned with its stored `httpStatus`. No external effects are triggered, and no saga steps rerun.

### Different request replay (hash mismatch)

Returns `409 Conflict` with:

```json
{
  "message": "Idempotency-Key already used with different request",
  "id": "<existing-order-id>"
}
```

### In-progress requests

An order that is still running through the saga (states `pending`, `reserved`, or `payment_unknown`) is already persisted with `httpStatus = 409` (the default in `schema.sql#L6`). A replay therefore returns the **latest persisted state** with `409`, signaling to the caller that the request is still in flight or ended in an uncertain state.

```java
if (!store.create(order, key, hash)) {
    var existing = store.byKey(key);
    if (!existing.hash().equals(hash)) {
        return ResponseEntity.status(409).body(Map.of(
            "message", "Idempotency-Key already used with different request",
            "id", existing.order().id));
    }
    return ResponseEntity.status(existing.order().httpStatus).body(existing.order());
}
```

**Relevant source:** `OrderController.create` replay branch (`repo://src/main/java/com/commercelens/orders/OrderController.java#L20-L21`).

---

## Intentional Blocking of Replays for Uncertain States

Crash recovery and saga replay are **intentionally blocked** when the order record is in an intermediate or uncertain state:

| State | Meaning | Replay behavior |
|---|---|---|
| `pending` | Order created, saga not yet started | Returns `409` with the `pending` record |
| `reserved` | Inventory held, payment not yet attempted | Returns `409` with the `reserved` record |
| `payment_unknown` | Payment initiated; outcome may be unknown | Returns `409` with the `payment_unknown` record |

These states occur because the saga checkpoints after every external effect and before uncertain calls (see [Checkout Saga](../architecture/checkout-saga.md)). If the process crashes during a payment or shipping call, the record already exists in the database with the idempotency key. Automatic replay is impossible because the next `POST` with the same key collides with the existing row.

This is by design: a crash during `payment_unknown` means a charge may have been created at the provider. Replaying blindly could double-charge the customer. Instead, an operator must reconcile with the payment provider and decide whether to retry using a **new** idempotency key.

Similarly, a crash in `pending` or `reserved` leaves a row that blocks reuse of the same key, preventing concurrent or retried submissions from spawning duplicate sagas.

**Relevant sources:** `OrderController.create` (`repo://src/main/java/com/commercelens/orders/OrderController.java#L18-L21`); `Checkout.run` `payment_unknown` checkpoint (`repo://src/main/java/com/commercelens/orders/Checkout.java#L43-L44`).

---

## End-to-End Flow

<!-- openwiki: mermaid parse failed and this diagram was converted to a text fence so it does not break rendering. Fix the diagram source and restore the mermaid fence. Parser error: Heuristic: an unescaped angle bracket inside a label breaks rendering; rephrase the label. -->
```text
flowchart TD
    A["POST /api/orders<br>Idempotency-Key + body"] --> B{"Validate header<br>^[A-Za-z0-9_-]{1,100}$"}
    B -->|invalid| C["400 Bad Request"]
    B -->|valid| D["Canonicalize and SHA-256 hash"]
    D --> E["OrderStore.create"]
    E -->|insert=0| F["OrderStore.byKey"]
    F --> G{"hash == stored?"}
    G -->|no| H["409 Conflict<br>different request"]
    G -->|yes| I["return existing order<br>with stored httpStatus"]
    E -->|insert=1| J["run Checkout saga"]
    J --> K["store.finish<br>update httpStatus"]
    K --> L["return order"]
```

**Caption:** Idempotency key processing from header validation through hash comparison, concurrent insert race, and saga execution.

---

## Related Pages

- [HTTP API Surface and Idempotency](../architecture/api-surface.md) — full REST endpoint reference and exception handling
- [Checkout Saga](../architecture/checkout-saga.md) — saga state machine and checkpointing details
- [Data Model](../architecture/data-model.md) — `orders` and `order_outbox` schema
- [Service Context](../service-context.md) — runtime topology and environment wiring
