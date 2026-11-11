# Plan 16: replan notification recovery as a restricted command

Original request: Allow an operator to retry order confirmation emails that exhausted their automatic delivery attempts.

Previous recommendation: Add a replay action to Customer Portal's Operations screen.

Selected alternative and instruction: Replan using a restricted operational command instead of a Portal action. Recovery is infrequent and performed by technical staff. Do not change Customer Portal or Order Service. Preserve delivery history and duplicate protection.

Status: Approved. Structured Replan test; API and UI verification are reported separately.

## Overall implementation strategy

Replace the proposed Portal action with a restricted command that lets authorized technical staff request recovery of a specific failed notification.

Keep recovery rules in Notification Worker. The command should invoke the worker's controlled recovery capability rather than directly modify stored delivery records or send emails independently.

Replay the original notification without restarting checkout. Preserve its history, prevent overlapping attempts, and retain its identity for provider duplicate protection. Provider behavior and retention limits must be verified; the application should not promise exactly-once delivery.

## Impacted components

**Notification Worker**

- Add a controlled recovery operation for notifications that exhausted their automatic attempts.
- Check eligibility before accepting a request. Already-delivered notifications and notifications currently being processed must not start another delivery.
- Preserve previous attempts and outcomes. Record the operator's recovery request and its result separately.
- Apply a bounded recovery policy so persistent failures return to operator attention.
- Make repeated command submissions safe, including when the operator does not receive a response after submitting a request.
- Reuse the original notification details. Updating customer information is outside this selected scope.

**Restricted operational command**

- Let the operator identify a notification and inspect its eligibility and previous outcome before requesting recovery.
- Require deliberate confirmation before initiating delivery.
- Distinguish recovery accepted from email sent. Provide a way to inspect the final result.
- Use an agreed operator-access mechanism and record who requested recovery. Possession of the command alone should not grant unrestricted access.

**Customer Portal and Order Service**

No changes are included. The command replaces the proposed Portal interaction, and recovery uses the notification information already retained by the worker.

Payment, shipment creation, and order processing must not be repeated.

## Implementation order

1. **Agree on recovery rules and access.** Define eligibility, attempt limits, acceptable notification age, provider duplicate protections, and operator authorization.
2. **Implement worker recovery.** Add eligibility checks, preserved history, bounded attempts, and protection against overlapping or repeated requests.
3. **Build the restricted command.** Add inspection, confirmation, recovery submission, and result lookup. Command development can proceed alongside worker implementation once their interface is agreed.
4. **Validate failure scenarios.** Cover repeated submissions, concurrent operators, interrupted requests, provider timeouts, and notifications already delivered.
5. **Enable controlled operational use.** Document the procedure and verify that operators can distinguish completed, failed, and unresolved outcomes.

## How this revised approach satisfies the request

- **Infrequent technical recovery:** A command provides deliberate operator control without building another UI flow.
- **No Portal or Order changes:** Recovery stays within Notification Worker and operational tooling.
- **Preserved history:** Previous delivery attempts remain available alongside the new recovery attempt.
- **Duplicate protection:** Eligibility checks, concurrency controls, stable notification identity, and verified provider behavior address different duplication risks.
- **Original business outcome:** Operators can recover exhausted confirmation emails without repeating checkout.

## Variations and recommendation

- **Command invoking a protected worker operation — preferred:** Centralizes recovery rules and keeps command behavior consistent with normal worker processing. Requires a protected operational interface.
- **One-off administrative job using the same recovery logic:** Avoids a continuously available administrative interface, but adds execution and result-inspection overhead. It must coordinate with the running worker and preserve the same safeguards.

The command invoking a protected worker operation is preferred for a straightforward support workflow. A one-off job is reasonable where deployment policy prohibits an administrative interface. Neither option requires a Portal change.
