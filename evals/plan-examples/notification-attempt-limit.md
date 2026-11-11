# Plan 6: configurable notification attempts

Question: Plan a change that lets operators configure the maximum number of automatic email delivery attempts without changing service code.

Status: Approved. Illustrative plan; accept justified variations, not exact wording.

## Verified current behavior

Notification Worker allows three delivery attempts, records attempts before contacting the provider, skips completed notifications and stops processing exhausted notifications.

## Overall implementation strategy

Replace the fixed limit with validated worker-owned configuration. Keep three as the default. Define the limit as total attempts including the first, not additional retries. Prefer deployment-time configuration read at startup, avoiding a new administrative UI or configuration service.

## Impacted service and implementation details

### Notification Worker

- Validate the startup setting against an agreed bounded range; reject invalid values clearly rather than allow unlimited attempts.
- Use the configured limit while preserving recorded attempts across interruptions and restarts.
- Record the applicable limit when a notification first enters processing, so later configuration changes do not unexpectedly change its policy. This is proposed new behavior.
- Keep sent and exhausted notifications terminal. Increasing the limit must not automatically replay exhausted notifications.
- Preserve duplicate protections and provider timeouts; additional attempts must not create concurrent sends or unlimited waiting.
- Define compatibility for records without a recorded limit, for example preserving the original three-attempt policy.

### Deployment configuration

- Expose and document the setting, default, permitted range and restart requirement.
- Keep worker instances consistently configured and report the effective value in startup diagnostics.
- No changes to Order, Payment, Shipping, Inventory or Portal are inherently required.

## Implementation order

1. Agree range, default, treatment of existing notifications and rollout policy.
2. Implement worker validation, configurable limits for new notifications and restart-safe attempt/policy preservation.
3. Expose deployment configuration and operator instructions; initially retain the existing default.
4. Validate settings, success before exhaustion, persistent failure, interrupted delivery and configuration changes. Ensure completed or exhausted notifications are not resent. Observe processing delays and provider load before increasing limits broadly.

## How this approach satisfies the request

- Operators adjust deployment settings instead of editing code.
- Explicit total-attempt semantics and bounds make behavior predictable.
- Existing notifications retain their applicable policy through changes.
- Attempt tracking, duplicate protection and terminal outcomes remain intact.

## Alternatives and recommendation

- **Startup configuration — recommended:** Simple and consistent with worker configuration; requires restart or redeployment for changes to affect new notifications.
- **Dynamic configuration:** Changes without restarts, but requires access control, auditing, propagation and consistency rules. Suitable for frequent adjustments.
- **Failure-specific policies:** Different treatment of temporary and permanent errors may improve behavior, but needs reliable classification and exceeds a single-limit requirement.

Prefer startup configuration for a focused change. Dynamic settings become worthwhile when adjustment frequency justifies their operational complexity.
