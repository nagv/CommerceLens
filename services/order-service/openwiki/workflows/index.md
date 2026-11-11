# Files

- [Checkout Saga — Failure Handling](failure-handling.md) - Detailed failure taxonomy for the checkout saga, covering inventory failures, payment decline versus uncertain outcome, shipping rejection with refund and release compensation, and compensation failures that require manual review. Grounded in Checkout saga logic and CheckoutTest assertions.
- [Idempotency and Concurrency](idempotency-and-concurrency.md) - End-to-end rules and guarantees for the POST /api/orders idempotency mechanism, including request canonicalization, database-level uniqueness enforcement, concurrent-race behavior, and the intentional blocking of replays for in-flight or uncertain states.
