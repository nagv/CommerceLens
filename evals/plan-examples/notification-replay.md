# Plan 2: recover failed notifications

Question: Plan a capability for an operator to retry order confirmation emails that have exhausted their automatic delivery attempts.

This is the user-approved illustrative plan. Evaluate substance and justified variations, not exact wording. Proposed functionality is not existing behavior.

## Overall implementation strategy

Add controlled replay to Notification Worker and expose it through Customer Portal's existing Operations screen. The worker already tracks attempts and outcomes, and the Portal displays notification status. An operator would select an eligible failed notification, request replay and see its result.

Replay the original notification rather than restart checkout or create another order. Preserve history, prevent overlapping attempts and retain existing duplicate protections. Preventing duplicates after interrupted delivery still depends partly on the email provider honoring repeat-request protection.

## Impacted services and implementation details

### Notification Worker

- Introduce a controlled operation for notifications that have exhausted automatic attempts. Check eligibility before starting; do not resend already-delivered notifications or start another concurrent replay.
- Preserve the original delivery history and record the replay separately, including who requested it, when it started and its outcome.
- Allow bounded replay attempts. Persistent failures must return to operator attention instead of creating endless retries.
- Retain the original notification identity for duplicate protection. Confirm the provider's retention and repeat-request behavior before assuming replay remains safe after a long delay.

### Customer Portal — Operations screen

- Add a replay action beside eligible failed notifications, with the previous failure and attempts visible to the operator.
- Require confirmation and disable repeated submissions while processing. Display whether replay was accepted, is running, succeeded or failed.
- Restrict the action to authorized operators. The existing demonstration interface does not establish production operator authorization; the proposed access-control approach must be agreed before enabling replay.

### Order Service

No change is inherently required: the worker retains delivery information, and email failure does not reverse the confirmed order. If the business requires updated customer details or order revalidation, identify that as an additional requirement and explain the conditional Order integration.

## Implementation order

1. **Agree on rules and access.** Define eligibility, limits, replay age, original versus updated details, provider protections and operator authorization.
2. **Implement worker support.** Add eligibility, tracking, concurrency protection and bounded attempts. Make repeated requests safe and return clear outcomes.
3. **Build the operator interaction.** Add the Portal action, confirmation and result display. Portal work can proceed alongside worker implementation once their interface is agreed; access controls must be ready before enablement.
4. **Validate and enable.** Cover success, repeated failures, duplicate submissions, concurrent requests and interrupted delivery. Verify preserved history and unchanged orders. Initially restrict access and review outcomes.

## How this approach satisfies the request

- **Recover exhausted notifications:** Provide an explicit replay path rather than continue rejecting an exhausted notification.
- **Operator control:** Let an operator select the failed item and deliberately request another attempt.
- **Duplicate protection:** Eligibility, concurrency handling and provider repeat-request behavior address different failure windows without promising exactly-once delivery.
- **Visible recovery:** Distinguish an accepted request from actual provider-confirmed sending.
- **Unaffected checkout:** Replay does not repeat payment, shipment creation or order confirmation.

## Alternatives and recommendation

- **Operations screen — recommended for routine use.** Put replay beside existing notification visibility, with confirmation and results. Requires Portal changes and protected operator access.
- **Restricted operational command.** Invoke the same worker capability without Portal changes. Appropriate for rare recovery by technical staff; reduces UI scope but makes selection and result inspection less convenient.
- **Scheduled recovery of eligible failures.** Revisit selected failures after an agreed delay. Useful for frequent, reliably classified temporary failures, but requires stronger rules and monitoring and does not replace the deliberate operator action requested here.

Prefer the Portal approach when recovery is a regular operational task. Prefer a restricted command for infrequent technical recovery. Do not require Portal or Order changes for every valid alternative.
