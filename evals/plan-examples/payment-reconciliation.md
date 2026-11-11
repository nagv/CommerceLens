# Plan 3: recover uncertain payment outcomes

Question: Plan high-level handling of uncertain payment outcomes without double charging the customer.

Status: Approved. This example illustrates expected depth and substance; other justified approaches are valid. Proposed capabilities are not existing functionality.

## Verified current behavior

After a payment timeout, Order Service retains the inventory reservation and treats payment as uncertain. Retrying the same checkout returns the saved order; it does not resolve payment or resume checkout. Payment Service supports authorization and refunds, but no payment-status lookup is implemented.

## Overall implementation strategy

Introduce recovery that checks the original payment outcome before taking further action. Order Service coordinates recovery and Payment Service communicates with the provider. Start with operator-triggered reconciliation: an authorized operator requests verification and the system uses confirmed provider information to decide the next step.

- Confirmed payment success: record the payment and safely continue remaining checkout steps.
- Definitive payment failure: mark the attempt accordingly and release reserved stock.
- Still uncertain: retain the unresolved state and escalate instead of charging again.

Confirm provider lookup capabilities and status semantics first. A missing or delayed record does not automatically prove that no payment occurred.

## Impacted services and implementation details

### Payment Service

- Introduce lookup of the original payment attempt using information associated with the order.
- Translate provider responses into confirmed success, confirmed failure or continued uncertainty, and return enough evidence to match the original attempt and amount.
- Separate lookup from authorization: failed lookup must never silently request a new payment.
- If reliable lookup is unsupported, expose the limitation and require an alternative verification process.

### Order Service

- Add controlled recovery for unresolved payments and prevent concurrent requests from independently advancing the same order.
- On confirmed success, record the payment and resume the appropriate stage rather than restart checkout.
- Before shipment creation, check whether fulfillment already started or completed. Avoid duplicate shipments and confirmation events.
- Release inventory only following definitive failure or an explicitly agreed resolution, not merely a timeout.
- Record decisions and outcomes so repeated recovery requests return the latest state consistently.

### Customer Portal — Operations screen

- Distinguish uncertain payments from definitive failures and provide authorized operators with reconciliation controls and outcomes.
- Show verification in progress, unresolved results and orders allowed to proceed.
- Explain that creating a fresh order while payment remains uncertain may cause another charge.
- Establish operator access controls before enabling recovery actions.

### Inventory and downstream services

Inventory already supports reservation release, so a new interface is not automatically necessary. Validate its existing behavior when recovery confirms failure. Shipping and Notification remain downstream participants; require interface changes only if the chosen recovery design cannot safely reuse their existing protections.

## Implementation order

1. Confirm provider lookup, definitive status semantics, unresolved-payment handling, reservation duration and operator permissions.
2. Implement Payment verification with handling for unavailable, delayed and ambiguous responses; verify lookup never initiates a charge.
3. Implement Order recovery transitions, concurrency protection and safe continuation; validate stock release and duplicate downstream protection.
4. Add operator visibility and controls. Portal work can proceed alongside backend development once the recovery interface is agreed.
5. Validate timeouts after successful payment, delayed provider records, duplicate requests, interrupted recovery and provider outages. Begin with restricted operator use before automation.

## How this approach satisfies the request

- Resolves uncertainty by checking the original payment instead of interpreting a timeout as failure.
- Avoids duplicate charges by separating verification from new payments and preserving original checkout identity.
- Allows legitimate orders to complete after confirmed payment.
- Protects inventory and fulfillment through evidence-based release/retention and safe continuation.
- Provides visible outcomes and decision history for operators.

## Alternatives and recommendation

- **Operator-triggered reconciliation — recommended initially:** Controlled recovery while provider behavior and operational rules are established; requires operator effort and can delay resolution.
- **Scheduled automatic reconciliation:** Periodically checks unresolved payments using the same rules; needs bounded retries, monitoring and escalation.
- **Provider event notifications:** Can reduce recovery delay, but requires confirmed support and handling duplicate, delayed and out-of-order updates; periodic lookup may still be needed.

Prefer controlled operator recovery initially because reliable lookup and recovery behavior are not implemented. Automation becomes preferable when capabilities and decision rules are proven. A different approach can be accepted when its provider assumptions, safeguards and trade-offs are justified.
