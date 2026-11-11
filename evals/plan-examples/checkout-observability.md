# Plan 7: application-wide troubleshooting

Question: Plan a change that lets support staff follow a checkout across all services and identify where it failed or became delayed.

Status: Approved. Illustrative plan, not an exact-match answer. Proposed capabilities are not existing functionality.

## Verified current behavior

Order identifiers pass between checkout services; notification events carry order and event identifiers. Inspected request paths do not establish consistent end-to-end tracing.

## Overall implementation strategy

Connect diagnostics across Portal, Order, Inventory, Payment, Shipping and Notification using structured logs and distributed tracing. Logs describe outcomes; traces show sequence and duration. Associate business order/event identifiers with diagnostic context while distinguishing requests and retries. Do not replace duplicate-prevention identifiers with tracing identifiers.

Start with checkout, then asynchronous notification and recovery flows. Support should be able to search by order or support reference to identify completed, failed and uncertain stages.

## Impacted services and implementation details

- **Customer Portal:** Display a support reference for checkout problems, including failures before order creation. Associate attempts with responses and keep customer-facing messages concise without exposing internal diagnostics.
- **Order Service:** Associate incoming requests, orders and downstream work; record inventory, payment, shipment and confirmation transitions and durations. Distinguish definitive failure from uncertainty and preserve context through confirmation publication.
- **Inventory Service:** Record reservation/release outcomes and duration, distinguishing insufficient stock from technical failure without recording unnecessary sensitive payloads.
- **Payment Service:** Record provider-interaction timing, interpreted outcomes and available provider references. Distinguish decline from timeout/unavailability and exclude credentials and sensitive payment data.
- **Shipping Service:** Record shipment outcomes, timing and available provider references. Distinguish explicit rejection from uncertain response; do not claim visibility inside an unsupported external provider.
- **Notification Worker:** Connect asynchronous processing to the original order/event. Record waiting/processing delay, individual attempts and final outcomes while retaining their common notification association.
- **Shared operations:** Provide searchable collection, access controls, retention, sampling and sensitive-data handling. Diagnostic collection failures must not block business processing.

## Implementation order

1. Agree identifiers, outcomes, timings, data-handling rules and tooling suitable for different service stacks.
2. Establish collection and Order orchestration instrumentation.
3. Instrument Inventory, Payment and Shipping in parallel after the diagnostic contract is agreed; verify each boundary.
4. Connect event-based Notification processing and Portal support references.
5. Validate success, stock rejection, uncertain payment, shipment failure and delayed email journeys; verify searchable continuity and sensitive-data exclusion.

## How this approach satisfies the request

- Shared context links related work across services.
- Meaningful outcomes locate failures rather than reporting only generic errors.
- Timing distinguishes slow service calls, external waits and notification delays.
- Separate attempts preserve retry visibility without losing the original order relationship.
- Portal references let customers give support a searchable identifier.

## Alternatives and recommendation

- **Structured logs plus distributed tracing — recommended:** Combines searchable outcomes with service sequence/timing; requires coordinated instrumentation and collection operations.
- **Structured logs only:** Simpler initial delivery, but reconstructing journeys and delays is more manual.
- **Business-status dashboard:** Focused operational progress view, requiring additional application work and offering less technical delay insight than traces.

Prefer logs plus tracing because both failure location and delay diagnosis are required. A logs-only phase is acceptable under time constraints if its limitations are explicit.
