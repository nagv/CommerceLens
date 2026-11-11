# Plan 4: extend order confirmation emails

Question: Plan a change so order confirmation emails include the names and quantities of the purchased products, while preserving reliable delivery.

Status: Approved. This is an illustrative plan, not an exact-match answer or a claim that proposed capabilities already exist.

## Verified current behavior

Order Service retains purchased items, but confirmation events contain order, customer, total and tracking information without product details. Notification Worker validates events, tracks delivery and forwards them to the email provider. The worker detects conflicting content received under the same event identity.

## Overall implementation strategy

Extend the confirmation event with a snapshot of purchased product names and quantities. Notification Worker accepts the additional information and passes it to a provider capable of displaying it in the email. Use recorded order items rather than the current catalog so the email reflects the purchase even after catalog changes.

Introduce the change compatibly: continue processing older events without product details while supporting newly generated extended events.

## Impacted services and implementation details

### Order Service

- Include names and quantities from recorded order items in newly created confirmation events.
- Preserve existing order information and event identity so delivery tracking remains intact.
- Capture product details when creating the event, rather than rebuilding different content on each delivery attempt.
- Do not rewrite already-published events merely to add information; conflicting content under the same identity is rejected by the current worker.

### Notification Worker

- Validate product details when present and prepare information for the email provider.
- Continue accepting old events without those details, using the existing email format as fallback.
- Preserve delivery tracking and duplicate protection; extending content must not cause already-completed notifications to be resent.
- Define handling for malformed product details without endless attempts.

### Email provider integration

- Confirm how the provider accepts and renders product details, and update the integration or template as needed.
- Do not assume that forwarding new information alone makes it visible in an email.
- Retain repeat-request protection and verify the content change does not alter it.

### Other services

Inventory need not change because order records already contain purchased item details. Portal, Payment and Shipping changes are not required unless additional requirements emerge.

## Implementation order

1. Agree the extended event content, validation and old-event fallback; confirm provider support and desired presentation.
2. Prepare the provider integration and Notification Worker to accept old and extended events. Validate both formats before producing new events.
3. Update Order Service to generate product snapshots while preserving event identity and reliable publication.
4. Validate older queued events, new events, repeated delivery, malformed details and provider failures. Verify duplicate delivery protections. Enable the producer change only when compatible consumers and provider integration are ready.

## How this approach satisfies the request

- Product names and quantities reach the email through the order snapshot and worker/provider integration.
- Details reflect the purchase rather than potentially changed catalog information.
- Older notifications remain deliverable through a supported fallback.
- Publication, delivery tracking and duplicate protections remain part of the extended flow.

## Alternatives and recommendation

- **Extend the existing event — recommended:** Self-contained notification processing without a new lookup dependency; requires compatibility with old and extended events.
- **Look up order details when sending:** Smaller events, but adds an Order Service dependency, failure handling and decisions about historical versus current information.
- **Separately versioned event:** Appropriate for incompatible changes or clearer consumer migration boundaries; adds rollout complexity and must avoid sending both notifications for one order.

Prefer an additive extension because the information already belongs to the order and can be added without removing existing fields. Prefer a separate version when consumer or provider requirements make an additive change impractical. Accept other approaches when their requirements, risks and trade-offs are justified.
