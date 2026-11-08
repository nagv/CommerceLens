# Service MVP verification

Verified locally on 2026-11-08 with Docker Desktop Linux containers.

| Component | Evidence |
| --- | --- |
| Order (Java) | 9 Maven tests, including PostgreSQL concurrent idempotency and uncertain payment conflict |
| Inventory (Go) | 3 tests, including 20 competing reservations against 5 units and idempotent release |
| Payment (Python) | 3 tests in Docker |
| Shipping (C#) | 3 tests in Docker, including definitive rejection versus unknown outcome |
| Notification (TypeScript) | 6 tests and TypeScript compilation, including channel closure/reconnection signaling |
| Portal (React/TypeScript) | 3 tests, production build, Docker build; successful checkout through browser |
| Mock providers | 7 Python tests, including chunked HTTP bodies from .NET |

The Compose smoke script exercises actual HTTP services, PostgreSQL, RabbitMQ, and mock providers: confirmed checkout, authoritative totals, repeated/conflicting request keys, stock decrement, decline compensation, shipment rejection compensation, invalid quantity, uncertain payment timeout, email success, three failed email attempts, and concurrent checkout idempotency.

Review findings fixed: payment HTTP409 retained as uncertain; timeout test now checks its own order; notification channel error/close clears readiness and reconnects; mock HTTP parser accepts chunked requests.

These checks do not certify production readiness. Authentication, real vendor adapters, automated reconciliation/reservation expiry, load testing, deployment hardening, and RAG evaluations remain outside this service milestone. Uncertain or interrupted checkout workflows require operator reconciliation. Test runs leave synthetic orders and consume seeded stock.
