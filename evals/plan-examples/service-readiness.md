# Plan 8: application-wide readiness

Question: Plan a change that makes service health reporting consistent and prevents work from being sent to services that are not ready.

Status: Approved. Illustrative plan; justified alternatives are acceptable. Proposed functionality is not existing capability.

## Verified current behavior

Order and Inventory check database connectivity. Payment and Shipping return basic healthy responses. Notification reports startup/connection readiness; Portal checks its web server. These checks do not share one complete readiness contract.

## Overall implementation strategy

Define liveness (process functioning), readiness (able to accept intended work) and dependency status (unavailable/degraded capabilities) separately. External outages must not automatically cause healthy processes to restart repeatedly. Connect readiness to actual routing or consumption controls: reporting not-ready alone does not prevent new work. Migrate gradually and preserve existing checks until their consumers move.

## Impacted services and implementation details

- **Order Service:** Check safe acceptance/persistence of checkout. Distinguish downstream availability from local readiness and preserve useful read capabilities. Define rejecting or deferring unavailable checkout work. Keep normal failure handling because a successful probe cannot guarantee the next operation.
- **Inventory Service:** Separate process liveness from bounded database readiness checks. Avoid monitoring load competing with reservations; reflect storage loss and recovery.
- **Payment and Shipping:** Check initialization/configuration and report provider availability separately. Never make real payments or shipments as health probes. Use safe provider checks only if supported; state visibility limits and avoid unnecessarily disabling unrelated capabilities.
- **Notification Worker:** Check ability to receive work and record delivery state, including dependency changes after startup. Pause new consumption when required dependencies fail. Preserve normal rules for in-progress work; do not acknowledge unfinished messages merely because the worker stops.
- **Customer Portal:** Separate serving the UI from feature availability. Show unavailable checkout/history/notification features clearly while retaining usable functionality. A Portal check must not imply the entire application is healthy.
- **Deployment/operations:** Configure the selected routing/runtime and worker controls to honor readiness. Define intervals, startup allowances and recovery thresholds to avoid flapping. Monitor affected services/capabilities without exposing sensitive configuration.

## Implementation order

1. Agree health semantics, affected work and the deployment enforcement mechanism.
2. Implement service checks independently against the shared contract, preserving old endpoints during migration when needed.
3. Connect routing and consumption controls; validate their response to readiness rather than assume automatic enforcement.
4. Update Portal feature-availability messaging.
5. Exercise delayed startup, storage/messaging loss, provider outages and recovery. Verify correct handling of new and in-progress work and no dependency-driven restart cascade.

## How this approach satisfies the request

- Common distinctions make reporting consistent while retaining service-specific responsibilities.
- Routing/consumption enforcement prevents unsuitable new work.
- Capability-aware reporting avoids unnecessarily disabling the whole application.
- Separate process/dependency states improve diagnosis.
- Normal request error handling addresses failures occurring between probes.

## Alternatives and recommendation

- **Separate liveness, readiness and dependency status — recommended:** Clear operational decisions with reduced restart cascades; requires service/deployment coordination.
- **One comprehensive health check:** Simpler, but conflates failures and can remove useful services or trigger unnecessary restarts.
- **External synthetic monitoring:** Finds integration failures through representative journeys; complements rather than replaces readiness and must avoid unintended business effects.

Prefer separated signals because both accurate reporting and work admission are required. Add synthetic monitoring as complementary application-level validation.
