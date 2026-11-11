# commercelens-payment-service
Python/FastAPI HTTP boundary for payment authorization and refunds. Calls an external HTTP provider; defaults to the central, explicitly simulated mock-provider. Real processors require a compatible provider adapter.

## API

- GET /health returns status ok.
- POST /api/payments: `{orderId,amountCents,currency:"USD",scenario:"success"|"decline"|"timeout"}` -> `{paymentId,status:"authorized"}`.
- POST /api/payments/{paymentId}/refund: `{orderId}` -> `{status:"refunded"}`.

Amounts must be positive integer cents. Provider POST /payments uses Idempotency-Key equal to orderId; POST /refunds uses `refund:orderId:paymentId`. Provider must durably enforce these keys and reject conflicting payloads. No blind retries of ambiguous payment writes.

402 means explicit decline; 504 timeout has unknown outcome; 502 unavailable/invalid provider responses also require reconciliation. A timeout does not prove that no charge occurred.

## Run and test

Use Docker Compose in nagv/CommerceLens for the full workflow. `docker build -t commercelens-payment .` builds the service. `docker build --target test -t commercelens-payment-test .` runs provider contract tests.

Environment: PAYMENT_PROVIDER_URL (default http://mock-provider:8080), PROVIDER_TIMEOUT_SECONDS (3). Port 8080. OpenAPI at /docs. No credentials needed for mocks. This local demo has no end-user authentication: expose only on private networks or loopback.
