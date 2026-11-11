# Plan 10: external shipment tracking

Question: Plan a change that lets customers see the latest shipment delivery status from the shipping provider in their order details.

Status: Approved. Illustrative plan; accept justified alternatives. Proposed capabilities are not existing functionality.

## Overall implementation strategy

Extend the existing shipment integration so customers can see delivery progress alongside their tracking number. Currently, Shipping Service creates shipments, Order Service retains the tracking number, and Customer Portal displays it. Delivery-status retrieval is a new capability.

Start with fetching status when customers open or refresh their order details, using a short-lived cache to limit provider calls. Shipping Service should own the provider integration; Order Service should connect the result to the correct order; Customer Portal should present it clearly.

First verify whether the selected provider supports shipment-status lookup, which identifier it requires, and its request limits. The existing integration does not establish these capabilities.

## Impacted services and implementation details

**Shipping Service**

- Add a provider integration for retrieving delivery progress. Translate provider-specific responses into consistent customer-facing states, such as awaiting pickup, in transit, delivered, or delivery exception.
- Retain the shipment reference and provider association needed for future lookups. The current Order integration keeps only the tracking number; confirm whether that is sufficient or whether the provider's shipment identifier must also be retained.
- Keep the latest known status and its freshness information. Use bounded requests and caching so repeated page refreshes do not overload the provider.
- If the provider is unavailable or returns an unrecognized status, preserve the last known information and report the limitation. Do not invent delivery progress.

**Order Service**

- Connect each order to its shipment and request tracking information through Shipping Service.
- Keep order processing status separate from shipment delivery status. A confirmed order must not automatically appear as delivered.
- Return order details even when tracking is temporarily unavailable. Tracking failure should not prevent customers from viewing their order.
- Ensure customers can access only their own order information. Customer identity and authorization must be established for a production customer-facing experience.

**Customer Portal**

- Display delivery status alongside the tracking number, including when the information was last checked.
- Clearly distinguish shipment not yet created, tracking information unavailable, and a known delivery status.
- When showing previously retrieved information during an outage, explain that it could not be refreshed.
- Provide a refresh action with sensible limits. Avoid promising live tracking when updates depend on provider availability and update frequency.

Payment Service, Inventory Service, and Notification Worker do not require changes for this viewing-only requirement.

## Implementation order

1. **Confirm the provider contract.** Establish lookup support, required shipment identifiers, available statuses, authentication, and request limits.
2. **Implement Shipping Service support.** Preserve the necessary shipment references, retrieve and normalize statuses, and handle unavailable or unfamiliar responses.
3. **Extend Order Service.** Associate tracking information with the correct order and return it without making order details dependent on provider availability.
4. **Update Customer Portal.** Build the status display and refresh experience. UI development can proceed alongside backend work once the response contract is agreed.
5. **Validate the complete flow.** Cover shipments awaiting pickup, delivery progress, delivery exceptions, missing shipment references, provider outages, and repeated refreshes. Confirm that viewing tracking never creates another shipment or changes payment or inventory.

## How this approach satisfies the request

- **Customers can see delivery status:** Order details gain an understandable delivery-progress display.
- **From the shipping provider:** Status comes through Shipping Service's provider integration rather than being inferred from order confirmation.
- **Latest status:** Opening or refreshing details retrieves a recent result, subject to a defined cache window. Freshness information makes that limitation visible.
- **Reliable customer experience:** Order details remain available during provider problems, with honest messaging about missing or stale tracking information.

## Alternatives and why this approach is preferred

- **Provider push updates:** Receive delivery events automatically and update stored status. This can improve freshness and reduce repeated lookups, but requires verified provider support, authenticated events, and handling of duplicate or out-of-order updates.
- **Scheduled polling:** Periodically refresh active shipments in the background. This offers predictable freshness without waiting for customers to open orders, but adds background processing and provider traffic for orders nobody is viewing.
- **Link to the provider's tracking page:** A smaller implementation that lets customers check progress externally. However, it does not fully satisfy showing delivery status within order details.

On-demand retrieval with caching is preferred for the initial implementation because it meets the requested experience with limited operational complexity. Provider push updates become more attractive when shipment volume or freshness requirements increase.
