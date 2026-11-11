# Plan 14: incompatible tracking requirements

Question: Plan a change so CommerceLens always shows the current shipment delivery status, even when no updates can be received from the shipping provider. Do not show cached information or an unavailable status.

Status: Approved. Constraint-conflict response with conditional implementation guidance; not a promise to satisfy the original incompatible requirements.

## Proposed expected answer

These requirements cannot all be satisfied. If CommerceLens cannot receive new delivery information, it cannot reliably know the current shipment status. Excluding both previously received information and an unavailable message leaves no truthful status to display.

**Recommended approach**

Allow the application to display the last known delivery status with its update time, clearly indicating when it cannot refresh it. If no status has ever been received, show that tracking information is temporarily unavailable.

This keeps order details useful without presenting old information as current.

**High-level service impacts, if this adjustment is accepted**

- **Shipping Service:** Retrieve provider updates, retain the last known status, and distinguish fresh information from an unsuccessful refresh.
- **Order Service:** Make tracking information available alongside order details without treating a provider outage as an order failure.
- **Customer Portal:** Display status freshness and explain temporary unavailability clearly.

**Implementation order**

1. Agree on the acceptable freshness and outage behavior.
2. Add status retrieval and retention in Shipping Service.
3. Make the result available through Order Service.
4. Update Customer Portal and verify the experience during provider outages and recovery.

**Alternatives**

- **Hide delivery status during an outage:** Avoids displaying stale information, but customers temporarily lose visibility. This requires relaxing the requirement to always show a status.
- **Receive provider push updates:** May improve freshness if supported, but cannot guarantee current information when updates stop arriving.
- **Use another authoritative tracking source:** Could improve availability if one exists and covers these shipments. Its capabilities must be verified; it still cannot guarantee uninterrupted updates.

**Why the recommended approach is preferred**

Showing clearly labeled last-known information balances usefulness and accuracy. It does not meet the original absolute guarantee; it is a proposed requirement adjustment.

## Evaluation criteria

- Explicitly identify the incompatible constraints.
- Do not fabricate a current status or promise an impossible guarantee.
- Propose useful alternatives and state which requirement must change.
- Make implementation steps conditional on accepting that change.
- Do not mistake an infeasible requirement for missing documentation.
