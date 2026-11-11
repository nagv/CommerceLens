---
type: concept
title: Service Context — commercelens-notification-worker
description: Comprehensive identity and contract reference for the CommerceLens notification worker, covering interfaces, dependencies, business flow, failure behavior, configuration, and observability.
tags: [service-context, commercelens, notification-worker, identity, interfaces, dependencies]
sources:
  - id: openwiki-source-bb1ebe868e35e9e500714501
    resource: repo://Dockerfile
  - id: openwiki-source-5b54a58d1b51cd490b0e7162
    resource: repo://package.json
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-4719c11adbf38d273d13e9ba
    resource: repo://src/delivery.ts
  - id: openwiki-source-bafd370ab4ac08bff65d53c6
    resource: repo://src/lifecycle.ts
  - id: openwiki-source-d4189bbeecb62806cb297b5a
    resource: repo://src/main.ts
generated: { by: "codex/openwiki-lifecycle-review", at: "2026-11-09T01:29:52.130Z" }
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T01:29:52.130Z
---

# Service Context — commercelens-notification-worker

This page provides the comprehensive identity and contract reference for the CommerceLens notification worker. It combines identity, provided and consumed interfaces, dependency relationships, business flow, failure behavior, and operational configuration into a single source of truth for anyone integrating with, deploying, or changing the worker.

## Identity

| Attribute | Value |
|---|---|
| **Package name** | `commercelens-notification-worker` ([`package.json`](repo://package.json)) |
| **Runtime name** | `notification-worker` (Docker image name) |
| **Purpose** | Consume durable `order.confirmed` RabbitMQ messages, send order-confirmation emails via an HTTP provider, and persist delivery state in PostgreSQL. |
| **Business capabilities** | Event-driven email delivery, bounded retry with dead-lettering, at-least-once delivery idempotency, delivery status introspection. |
| **Technology stack** | Node.js 22, TypeScript (`"type":"module"`), `amqplib`, `pg` (native `node:http` server). |
| **Entry point** | `src/main.ts` compiled to `dist/main.js`; container starts with `CMD ["node","dist/main.js"]` ([`Dockerfile`](repo://Dockerfile#L16)). |
| **Ownership evidence** | Package name and `package.json` version `0.1.0` ([`package.json`](repo://package.json#1)). |

```mermaid
flowchart TD
    subgraph Entities
        AMQP["RabbitMQ order.confirmed"]
        DB["PostgreSQL notification_deliveries"]
        Provider["HTTP Email Provider"]
    end
    Worker["notification-worker src/main.ts"]
    AMQP -->|consume| Worker
    Worker -->|POST /email| Provider
    Worker -->|upsert,query| DB
    Web["HTTP Health/Status API"]
    Worker -->|GET /health, /api/notifications| Web
```
*Simplified architecture: the worker consumes from RabbitMQ, sends emails via HTTP, persists state to PostgreSQL, and exposes a local HTTP API.*

## Provided Interfaces

### HTTP Endpoints

| Method | Route | Status Codes | Response Schema | Description |
|---|---|---|---|---|
| `GET` | `/health` | `200` / `503` | `{status:"ok"}` or `{status:"starting"}` | Returns `200` after DB initialization and RabbitMQ connection are established; `503` during startup or after disconnection. |
| `GET` | `/api/notifications` | `200` / `503` / `404` | Array of `{eventId,orderId,status,attempts,lastError}` (max 100 rows) | Lists the latest 100 delivery rows ordered by `updated_at DESC`. |

> ⚠️ `GET /api/notifications` is **unauthenticated** and intended only for local or private-network demonstration ([`src/main.ts`](repo://src/main.ts#L14-L17)).

The HTTP server listens on `0.0.0.0` at the port specified by the `PORT` environment variable, defaulting to `8080` ([`src/main.ts`](repo://src/main.ts#L19)).

### RabbitMQ Queue

| Queue | Properties | Dead-Letter Routing |
|---|---|---|
| `order.confirmed` | Durable, `prefetch(1)` | `x-dead-letter-exchange: ''`, `x-dead-letter-routing-key: 'order.confirmed.dead'` |

- `order.confirmed.dead` is also declared as a durable queue during startup ([`src/main.ts`](repo://src/main.ts#L28-L29)).
- Producers **must** declare matching queue arguments and publish persistent messages. Cross-repository consumers that create this queue with different arguments will fail channel assertion.

### Database Schema

The worker auto-creates the `notification_deliveries` table on startup if it does not exist:

```sql
CREATE TABLE IF NOT EXISTS notification_deliveries(
  event_id TEXT PRIMARY KEY,
  order_id TEXT NOT NULL,
  payload JSONB NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  attempts INTEGER NOT NULL DEFAULT 0,
  last_error TEXT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

([`src/main.ts`](repo://src/main.ts#L21))

### Published Events / Topics

**None.** The worker does not publish events; it only consumes from RabbitMQ and calls an external HTTP service.

## Consumed Dependencies

| Direction | Relationship | Target Identifier | Interface / Topic | Configuration Variable | Evidence | Certainty |
|---|---|---|---|---|---|---|
| Outbound | HTTP call | Email provider base URL | `POST /email` with JSON body and `Idempotency-Key` header | `EMAIL_PROVIDER_URL` | [`src/main.ts#L48`](repo://src/main.ts#L48) | Confirmed |
| Inbound | AMQP consumer | RabbitMQ broker | Queue `order.confirmed` (durable, DLX to `order.confirmed.dead`) | `RABBITMQ_URL` | [`src/main.ts#L22-L29`](repo://src/main.ts#L22-L29) | Confirmed |
| Outbound | Database writes | PostgreSQL | Table `notification_deliveries` (CRUD + advisory lock) | `DATABASE_URL` | [`src/main.ts#L7,L21`](repo://src/main.ts#L7,L21) | Confirmed |
| Outbound | HTTP health endpoint | Node.js `http` module | Routes `/health` and `/api/notifications` | `PORT` | [`src/main.ts#L10-L19`](repo://src/main.ts#L10-L19) | Confirmed |

### Package Dependencies

| Name | Purpose |
|---|---|
| `amqplib` ^0.10.5 | RabbitMQ AMQP client (runtime) |
| `pg` ^8.13.3 | PostgreSQL client and pool (runtime) |

### Dev Dependencies

| Name | Purpose |
|---|---|
| `@types/amqplib`, `@types/node`, `@types/pg`, `tsx`, `typescript` | Type-checking, compilation, and test execution |

([`package.json`](repo://package.json))

## Business Flow

### Input: order.confirmed Message Schema

Messages on the `order.confirmed` queue must carry a JSON payload with the following shape:

```typescript
type Event = {
  eventId: string;       // non-empty, ≤ 320 characters
  orderId: string;       // non-empty, ≤ 320 characters
  customerEmail: string; // non-empty, ≤ 320 characters, contains '@'
  totalCents: number;    // safe integer, ≥ 0
  trackingNumber: string;// non-empty, ≤ 320 characters
};
```

([`src/delivery.ts#L1`](repo://src/delivery.ts#L1), [`src/delivery.ts#L2-L6`](repo://src/delivery.ts#L2-L6))

### Validation: parseEvent

`parseEvent(raw:string):Event` enforces strict validation before any delivery logic runs:

1. `JSON.parse` must succeed.
2. Required string fields must be strings with length `> 0` and `<= 320`.
3. `totalCents` must be a non-negative safe integer.
4. `customerEmail` must contain the `@` character.

Validation failures result in the message being negatively acknowledged **without requeue**, routing it directly to the dead-letter queue.

### State Changes

The worker uses `notification_deliveries` as the source of truth for delivery state:

1. **Upsert** on every consume attempt: `INSERT ... ON CONFLICT DO NOTHING`.
2. **Advisory lock** on `hashtext(eventId)` serializes concurrent duplicate events across workers.
3. **Payload-mismatch check** via exact JSONB equality prevents idempotency-key collision across semantically different events.
4. **Status gates** (`sent`, `dead`, `pending`) determine whether the worker skips, dead-letters, or attempts delivery.
5. **`deliver()`** manages attempt budgeting (max 3), linear backoff (`250ms × attempt`), and persistence of attempts and last error.

([`src/main.ts#L37-L54`](repo://src/main.ts#L37-L54), [`src/delivery.ts#L7-L15`](repo://src/delivery.ts#L7-L15))

### Output

1. **HTTP POST to provider** at `{EMAIL_PROVIDER_URL}/email` with:
   - `Content-Type: application/json`
   - `Idempotency-Key: <eventId>`
   - Body: the full `Event` JSON
   - Abort signal timeout of `PROVIDER_TIMEOUT_MS` (default 3000 ms)

2. **Database persistence** of final status, attempt count, last error, and `updated_at`.

3. **RabbitMQ acknowledgement or dead-lettering**:
   - `sent` → `channel.ack(message)`
   - `dead` → `channel.nack(message, false, false)` (routes to `order.confirmed.dead`)

### Cross-Repository Boundaries

- **Queue assertion**: Producers declaring `order.confirmed` must use the exact same arguments (`durable: true`, `x-dead-letter-exchange: ''`, `x-dead-letter-routing-key: 'order.confirmed.dead'`). Mismatched arguments cause a channel precondition exception.
- **Idempotency contract**: The provider must durably deduplicate requests by the `Idempotency-Key` header. Without this, retries after a crash between provider success and persistence could send duplicate emails.
- **Dead-letter queue**: `order.confirmed.dead` is declared during startup and must exist (or be creatable) in the same vhost. Manual replay of dead messages is **not implemented**.

## Failure Behavior

| Failure Type | Behavior | Evidence |
|---|---|---|
| **HTTP timeout** | `AbortSignal.timeout(PROVIDER_TIMEOUT_MS)` — default **3000ms**. Throws, triggers retry loop. | [`src/main.ts#L48`](repo://src/main.ts#L48) |
| **Retry count / backoff** | Max **3 attempts** total. Backoff sleep is **250ms × attempt number** (250ms, 500ms). No jitter. | [`src/delivery.ts#L9-L13`](repo://src/delivery.ts#L9-L13) |
| **Idempotency** | `eventId` is sent as `Idempotency-Key` HTTP header. PostgreSQL advisory lock on `hashtext(eventId)` serializes concurrent duplicate events. | [`src/main.ts#L40`](repo://src/main.ts#L40), [`src/main.ts#L48`](repo://src/main.ts#L48) |
| **Compensation** | **None.** Email failure never rolls back confirmed orders. | [`README.md`](repo://README.md#L12) |
| **Dead letters** | Exhausted attempts (`status: 'dead'`) cause `nack` without requeue, routing to `order.confirmed.dead`. Malformed events are also dead-lettered immediately. | [`src/main.ts#L34`](repo://src/main.ts#L34), [`src/main.ts#L44`](repo://src/main.ts#L44), [`src/main.ts#L54`](repo://src/main.ts#L54) |
| **Crash between provider success and persistence** | The idempotency key (`eventId`) is the only safeguard. If the provider processes the request but the worker crashes before persisting `sent` status and acking, redelivery will skip the provider (status gate) once the row is written. If the row was never written, the provider must deduplicate. | [`README.md`](repo://README.md#L10) |
| **Manual intervention** | **Not implemented.** Dead messages are not automatically replayed. | [`README.md`](repo://README.md#L12) |
| **Interrupted delivery** | Any unexpected error after acquiring the advisory lock is caught, the worker sleeps **1000ms**, then nacks **with requeue**, and releases the lock/client in `finally`. | [`src/main.ts#L55-L59`](repo://src/main.ts#L55-L59) |
| **Provider non-OK response** | If HTTP status is not OK or the JSON body does not contain `status: "sent"`, the attempt throws. | [`src/main.ts#L49-L51`](repo://src/main.ts#L49-L51) |
| **Sent redeliveries** | If the DB row already has `status: 'sent'`, the message is acked immediately without calling the provider. | [`src/main.ts#L45`](repo://src/main.ts#L45) |

## Configuration and Observability

### Environment Variables

| Name | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | **Yes** | — | PostgreSQL connection string |
| `RABBITMQ_URL` | No | `amqp://guest:guest@rabbitmq:5672` | AMQP connection string |
| `EMAIL_PROVIDER_URL` | No | `http://mock-provider:8080` | Base URL of the HTTP email provider |
| `PROVIDER_TIMEOUT_MS` | No | `3000` | HTTP request timeout for provider calls (milliseconds) |
| `PORT` | No | `8080` | Port for the worker's own HTTP endpoints |

### Health Check

- `GET /health` returns `200` once the database schema has been initialized and the RabbitMQ connection is active.
- Returns `503` during startup or after connection loss.

### Logging

The worker writes error-level logs to `console.error` for:
- RabbitMQ connection errors ([`src/main.ts#L24`](repo://src/main.ts#L24))
- Database unavailability ([`src/main.ts#L36`](repo://src/main.ts#L36))
- Delivery interruptions ([`src/main.ts#L55`](repo://src/main.ts#L55))
- Worker startup/reconnect failures ([`src/main.ts#L71`](repo://src/main.ts#L71))

There is no structured JSON logging; messages are plain strings.

### Setup

```bash
npm ci        # install dependencies
npm test      # run tests via tsx
npm run build # compile TypeScript to dist/
npm start     # run compiled worker
```

The Docker multi-stage build runs `npm test && npm run build` in the build stage, then copies only production artifacts and runs as user `node` on port `8080`.

## Lifecycle and Connection Management

The worker runs an infinite reconnect loop in `main()`: establish PostgreSQL + RabbitMQ, register a consumer, and wait for the session to end. On session end (error or close), the connection is discarded and the loop retries after 3000ms. `watchSession` from [`src/lifecycle.ts`](repo://src/lifecycle.ts) wraps `EventEmitter`-based connection and channel objects, ensuring that errors on either surface trigger a single teardown path. `SIGTERM` sets `stopping=true`, closes the HTTP server, drains the DB pool, and exits gracefully.

```mermaid
sequenceDiagram
    participant W as Worker (main.ts)
    participant DB as PostgreSQL
    participant RB as RabbitMQ
    participant EP as Email Provider

    loop Reconnect loop
        W->>DB: CREATE TABLE IF NOT EXISTS...
        W->>RB: amqp.connect(RABBITMQ_URL)
        W->>RB: assertQueue order.confirmed.dead
        W->>RB: assertQueue order.confirmed (with DLX args)
        W->>RB: prefetch(1) + consume
        W->>W: ready=true
        RB->>W: order.confirmed message
        W->>DB: parseEvent, advisory lock, upsert
        alt status sent
            W->>RB: ack (skip provider)
        else status pending
            W->>EP: POST /email (Idempotency-Key=eventId)
            EP-->>W: HTTP 200 + {status:"sent"}
            W->>DB: UPDATE status='sent', attempts, lastError
            W->>RB: ack
        end
        RB-->>W: error or close
        W->>W: ready=false
        W->>RB: connection.close()
        W->>W: sleep 3000ms
    end
```
*Sequence diagram showing the startup, steady-state consume/deliver/ack loop, and reconnect cycle.*

## Test Coverage

[`test/delivery.test.ts`](repo://test/delivery.test.ts) covers:
- `parseEvent` rejecting malformed JSON, missing fields, and invalid values.
- `deliver()` stopping after success while preserving prior attempts.
- `deliver()` terminating after exactly 3 failed attempts with the correct error propagation.

[`test/lifecycle.test.ts`](repo://test/lifecycle.test.ts) covers:
- Channel errors and closures marking the session as ended.
- Connection-only closure triggering unavailable callback.
- Early closure and double-stop handling ensuring the callback runs exactly once.

## Related Pages

- [Delivery and Retry Logic](concepts/delivery-retry.md) — Deep dive into `deliver()`, idempotency, and terminal statuses.
- [Message Consumption Flow](flows/message-consumption.md) — Step-by-step trace of a single AMQP message through the worker.
- [Configuration and Operations](operations/configuration.md) — Docker build, npm scripts, and operational reference.
- [Lifecycle Management](concepts/lifecycle.md) — `watchSession` and graceful shutdown details.
