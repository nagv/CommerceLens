# CommerceLens Inventory Service

Go HTTP service with PostgreSQL-backed products and reservations. Port 8080. It owns inventory tables and never accepts prices from checkout callers.

## API

- `GET /health`: database readiness.
- `GET /api/products`: array of SKU, name, priceCents and available units.
- `POST /api/reservations`: `{ "orderId": "...", "items": [{"sku":"BOOK-001","quantity":1}] }`.
- `POST /api/reservations/{orderId}/release`: idempotent stock release.

Reservation response includes authoritative item prices, subtotalCents, orderId and status. Invalid quantities/duplicate SKUs return 400; missing SKU returns 404; insufficient stock or conflicting replay returns 409. Transactions lock SKU rows in sorted order to prevent overselling/deadlock. An advisory lock serializes duplicate order IDs. Replaying released reservations returns 409 rather than reserving again.

## Run

Set `DATABASE_URL=postgres://commerce:<password>@postgres:5432/inventory?sslmode=disable`. Tables and three demo products are initialized without resetting existing inventory.

Use the central [CommerceLens](https://github.com/nagv/CommerceLens) Docker Compose configuration, or build `docker build -t commercelens-inventory .` and run with DATABASE_URL configured. Do not expose this unauthenticated internal demo API publicly.

## Tests

`go test ./...` runs validation/fingerprint tests. Set `TEST_DATABASE_URL` to a disposable PostgreSQL database to additionally verify concurrent reservations cannot oversell, conflicting replays fail, and releasing twice restores stock once. Tests use unique fixture IDs. Docker build runs unit tests.

## Documentation

Run `graphify extract . --code-only --force` first, then `openwiki --update --print`. PostgreSQL is the only runtime dependency; no LLM or external business provider is used here.
