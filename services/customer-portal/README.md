# CommerceLens customer portal

React 19 + TypeScript + Vite storefront and operations UI. A local demonstration frontend for independently deployed CommerceLens services. External integrations use explicitly labeled HTTP mocks by default.

## Run

Use Docker Compose in [CommerceLens](https://github.com/nagv/CommerceLens). The portal is at `http://localhost:3000`; nginx proxies API requests to the internal services.

For development with Node 24:

```sh
npm ci
npm test
npm run build
npm run dev
```

Vite proxies order/catalog requests to localhost:8080 and notification requests to localhost:8085; change `vite.config.ts` if local ports differ. Production container binds port 80. `GET /health` reports frontend availability, not downstream dependency health.

## User flows

- Browse live inventory; add items and adjust quantities or remove with quantity zero.
- Checkout with email and postal code. Displayed prices are estimates; the backend determines authoritative amounts and stock.
- Select success, declined payment, payment timeout, or shipping failure in the expandable test controls.
- Use an address containing `fail-email` to exercise notification retries and dead-letter behavior.
- Inspect order details, tracking, payment state, and failure reasons.
- Open Operations for order history and notification records; Refresh activity queries service state.
- The application assistant is labeled as a future milestone. No simulated chatbot is presented as a working assistant.

## API boundaries

| Endpoint | Destination |
| --- | --- |
| GET /api/products | order-service → inventory-service |
| POST /api/orders | order-service checkout orchestration |
| GET /api/orders | order-service history |
| GET /api/orders/{id} | order-service detail |
| GET /api/notifications | notification-worker |

POST orders sends `Idempotency-Key` with `{customerEmail, postalCode, items:[{sku, quantity}], paymentScenario, shippingScenario}`. Client prices are never submitted as authoritative values.

## Retry behavior

Before submission, the portal saves the request and a UUID in tab-scoped `sessionStorage`. Retries and page refreshes reuse the original payload and key. Inputs remain locked until the user explicitly starts a different order. Network interruptions are described as unknown outcomes, not declines. Starting a new order asks the user to check history because the previous payment may remain pending. Email and postal code remain in sessionStorage until Start a new order or tab closure; this is a local-demo choice, not a production privacy design.

Browser requests time out at 30 seconds; nginx allows 35 seconds for upstream replies. Failed POST responses with a full order or an `order` property display saved order details. An unavailable notification service does not disable checkout.

## Verification

`npm test` checks money calculations, input/stock validation, and stable retry idempotency. `npm run build` type-checks TypeScript and generates production assets. Docker builds run both commands. Central CommerceLens owns real-service smoke tests.

## Documentation generation

```sh
graphify extract . --code-only --force
openwiki --update --print
```

Keep source and tests included so documentation can describe UI state, API calls, and retry behavior.
