# Plan 15: replan using provider-supplied quotes

Original request: Replace fixed shipping charges with destination-based rates.

Previous recommendation: Application-managed regional pricing rules (the Plan 1 proposal, not implemented functionality).

Selected alternative and instruction: Replan using provider-supplied shipping quotes instead of application-managed regional rules. Customers must see and confirm the shipping charge before payment. Do not fall back to regional pricing if the provider is unavailable.

Status: Approved. The test passes the prior plan and selection through the structured Replan engine, shared with the implemented API.

## Overall implementation strategy

Use Shipping Service to obtain destination-based quotes from the shipping provider. Replace the previous recommendation of regional pricing rules with provider-supplied pricing.

First verify that the provider supports quotes, their validity period, and how an accepted quote relates to shipment creation. The existing integration does not establish these capabilities.

Introduce a quote-and-confirm step before payment. Customer Portal displays the shipping charge and total; Order Service validates the accepted quote before initiating payment and preserves it with the checkout attempt.

If a valid quote cannot be obtained, explain that pricing is temporarily unavailable and prevent payment from proceeding. Do not substitute regional pricing or the existing fixed charge.

## Impacted services

**Shipping Service**

- Integrate the provider's quote capability and translate its responses into consistent application outcomes.
- Return the amount, destination, quote reference, and validity information needed to recognize and validate the quote.
- Distinguish unsupported destinations, expired quotes, and temporary provider failures.
- Remove the existing fixed-charge assumption from shipment handling. Establish how shipment creation uses the accepted quote and handles any later provider cost difference without silently increasing the customer's charge.

**Order Service**

- Coordinate quoting before checkout confirmation and validate the selected quote before payment.
- Calculate the payment total using the validated shipping amount, rather than trusting an amount supplied by the browser.
- Preserve the accepted quote with the checkout attempt. Retrying an existing attempt must not silently replace its price.
- Require a fresh quote and renewed customer confirmation if the destination or price changes before payment.
- If payment may already have occurred, resolve that attempt before starting another payment.

**Customer Portal**

- Request a quote after the customer provides the destination.
- Display shipping separately from the product subtotal and show the final total before confirmation.
- Refresh quotes when relevant destination information changes and clearly present any price change.
- Explain unavailable pricing and prevent checkout confirmation without a valid quote.
- When recovering an existing checkout attempt, show its accepted amount.

Payment Service does not inherently need a new interface because Order Service supplies the payment amount. Inventory remains responsible for product pricing and stock.

## Implementation order

1. **Confirm provider support and pricing rules.** Establish quote validity, shipment-price commitments, supported destinations, and outage behavior.
2. **Implement Shipping Service quoting.** Add provider integration, validation, and shipment compatibility.
3. **Integrate Order Service.** Introduce quote acceptance, validated totals, and consistent retry handling.
4. **Update Customer Portal.** Add quote display, confirmation, expiry, and unavailable-pricing experiences. UI work can proceed alongside backend integration once the contract is agreed.
5. **Validate the complete flow.** Cover expired quotes, destination changes, provider outages, shipment cost differences, and repeated checkout. Verify that displayed, accepted, and payment-requested amounts agree.

## How the revised approach satisfies the request

- **Provider-supplied pricing:** Rates originate from the provider rather than regional rules.
- **Customer confirmation before payment:** The quote becomes part of an explicit confirmation step.
- **No regional fallback:** Unavailable pricing prevents a new payment instead of substituting another rate.
- **Safe recovery:** Accepted quotes remain associated with their original checkout attempts.

## Variations and recommendation

- **Retrieve a new provider quote for each pricing request:** Simpler freshness behavior, but creates more provider traffic and depends more heavily on availability.
- **Reuse a still-valid provider quote for the same checkout details:** Reduces repeated calls, provided the provider permits reuse and the destination and other pricing inputs remain unchanged. This is reuse of provider pricing, not regional fallback.

Prefer reusing a valid provider quote when its terms allow it. Otherwise, request a new quote and obtain renewed confirmation when the amount changes. Regional and hybrid fallback approaches are excluded by the selected constraint.
