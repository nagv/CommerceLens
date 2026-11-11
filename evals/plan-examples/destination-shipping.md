# Plan 1: destination-based shipping

Question: Plan a high-level change from fixed shipping charges to destination-based rates.

This is an illustrative plan showing the expected depth. Other well-justified approaches are acceptable. Proposed functionality is not a claim about existing capabilities.

## Overall implementation strategy

Replace the fixed shipping charge with a destination-based quote owned by Shipping Service. Order Service should obtain and validate the quote before requesting payment, while Customer Portal shows the resulting shipping charge and total before the customer confirms checkout.

Start with application-managed regional pricing rules, such as supported postal regions and their charges. This provides destination-based pricing without depending on an external quote capability that the current implementation does not establish. Confirm the business pricing rules, supported destinations, quote validity and treatment of provider costs before implementation.

Keep the accepted quote associated with the checkout attempt. A retry must recover that attempt without silently recalculating a different charge. A destination change or expired quote should lead to an explicit updated quote and customer confirmation. This requires a proposed pre-payment quote/confirmation step; the existing checkout currently proceeds through payment and shipment in one orchestrated flow.

## Impacted services and implementation details

### Shipping Service

- Introduce destination-based rate calculation using agreed regional rules. Return the amount, destination and validity conditions needed to recognize the quote later.
- Define clear outcomes for unsupported destinations, invalid destination information and unavailable pricing. Do not silently substitute an arbitrary rate.
- Update shipment handling to remove its existing assumption that the provider charge must equal the fixed amount.
- Define how the accepted customer quote relates to the provider's shipment cost. A later provider cost difference must not silently change what the customer agreed to pay.

### Order Service

- Support obtaining a shipping quote before final checkout confirmation, then validate the accepted quote when processing checkout. Do not trust a client-supplied amount as authoritative.
- Include the validated shipping amount in the total sent to Payment Service and preserve it with the checkout attempt.
- Keep retry behavior consistent with the original attempt. If the destination or quote changes before authorization, request renewed confirmation; if payment may already have occurred, reconcile the existing attempt instead of charging again.
- Continue creating the shipment after successful payment authorization, using information consistent with the accepted quote. Handle unsupported or unavailable quotes before initiating payment.

### Customer Portal

- Request a shipping quote through the backend after the customer supplies the destination, and display shipping separately from the product subtotal and final total.
- Refresh the quote when the destination changes before confirmation. Show any updated charge clearly and require confirmation before checkout proceeds.
- Explain unsupported destinations or unavailable pricing and prevent confirmation without a valid quote.
- When recovering a checkout attempt, display its agreed amount rather than presenting a newly calculated price as if it belonged to the original attempt.

### Other services

Payment Service already accepts the amount supplied by Order Service, so a Payment Service interface change is not inherently required. Inventory remains responsible for product prices and stock. Additional impacts should be justified by the selected pricing approach rather than assumed.

## Implementation order

1. **Agree on pricing behavior and the quote interface.** Define regions, validity, unsupported destinations, quote acceptance, cost differences and failure behavior. Establish how the new pre-payment quote step fits existing checkout and retries.
2. **Build Shipping support.** Implement calculation and quote validation, remove fixed-charge shipment assumptions and preserve existing checkout behavior during integration.
3. **Integrate Order Service.** Obtain and validate quotes, preserve the accepted amount, calculate payment totals and handle expiry or changes before authorization.
4. **Integrate Customer Portal.** Add quote display, destination updates, confirmation and recovery behavior. Portal work may proceed alongside Order work once the interface is agreed; enable the complete customer flow only after both integrations are ready.
5. **Validate and enable gradually.** Check supported and unsupported destinations, price changes, expired quotes, provider failures and repeated checkout. Verify that the displayed, accepted and payment-requested amounts agree, and that an uncertain payment is never treated as permission to charge again.

## How this approach satisfies the request

- **Destination-based rates:** Shipping calculates the amount from the destination instead of returning one uniform charge.
- **Correct payment:** Order validates the quote and includes it before requesting payment.
- **Customer visibility and consent:** Portal shows the charge and total before confirmation, including changes caused by a different destination.
- **Consistent recovery:** The accepted quote stays associated with the original attempt, preventing retry price drift.
- **Safe integration:** Existing fixed-price assumptions are addressed in both checkout and shipment handling, rather than changing only the displayed estimate.

## Alternatives and recommendation

- **Application-managed regional rules — recommended initially.** Pricing is predictable and does not require an unverified external quote interface. The application must maintain the rules and accept that customer charges can differ from provider costs.
- **Provider-supplied quotes.** Shipping requests rates from the provider, potentially reflecting actual carrier pricing and delivery options more closely. This requires confirming provider support and handling outages, quote expiration and price changes. Prefer this when actual provider pricing is a business requirement and the provider supports it.
- **Hybrid, if useful.** Use provider quotes with an explicitly approved regional fallback. This can improve availability but adds pricing-policy and reconciliation complexity; it is not necessary for an initial implementation unless the business needs it.

Regional rules are preferred initially because they fit the verified service boundaries and avoid relying on an undocumented provider capability. This is a conditional recommendation, not the only valid solution: the agreed business pricing requirement and confirmed provider capabilities should determine the final choice.
