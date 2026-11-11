# commercelens-shipping-service
C# / ASP.NET Core (.NET 8) shipping boundary calling an external HTTP provider. The default is the local CommerceLens mock, not a live carrier.

## API

- GET /health -> `{status:"ok"}`.
- GET /api/shipping/rate -> `{shippingCents:500,currency:"USD"}` (fixed demo rate).
- POST /api/shipments: `{orderId,postalCode,scenario:"success"|"failure"}` -> `{shipmentId,status:"created",trackingNumber,shippingCents:500}`.

Provider POST /shipments receives Idempotency-Key equal to orderId. Provider must persist idempotency and reject conflicting keys. HTTP 422 explicit rejection maps to status failed. Timeouts, server failures, and invalid success responses map to status unknown: callers must reconcile instead of assuming no shipment exists. No automatic retry of ambiguous writes.

Environment: SHIPPING_PROVIDER_URL (http://mock-provider:8080), PROVIDER_TIMEOUT_SECONDS (3). Listens on 8080. Production carrier authentication belongs in a provider-specific adapter.

## Build and test

`docker build -t commercelens-shipping .` builds the service. `docker build --target test -t commercelens-shipping-test .` runs xUnit provider contract tests. Use central CommerceLens Compose for integration. This local demo is unauthenticated; expose only on loopback/private networks.
