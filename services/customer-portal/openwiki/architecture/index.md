# Files

- [API Client](api-client.md) - A thin fetch wrapper that adds JSON headers, aborts after 30 seconds, parses JSON, and throws ApiError with status and body on non-2xx responses. Supports idempotent POST with Idempotency-Key.

- [Domain Models](domain-models.md) - Core domain types (Product, Checkout, Attempt, Order, Notification) and pure functions (cartSummary, validateCheckout, checkoutAttempt, money) that enforce checkout invariants and idempotency in the CommerceLens storefront.

