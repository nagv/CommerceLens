# Plan 9: integrate an external payment provider

Question: Plan a change to replace the mock payment provider with an external payment provider while preserving safe checkout and refunds.

Status: Approved. Illustrative plan; accept justified alternatives. Proposed capabilities are not existing functionality.

## Verified current behavior

Payment Service forwards authorization/refund requests to a configurable address, distinguishes declines from uncertainty and uses repeat-request protection. Checkout does not collect a real payment method. Changing the address alone is not a complete external integration.

## Overall implementation strategy

Keep Payment Service as the provider boundary, translating application operations into the selected provider's workflow. First confirm payment collection, authorization, refunds and verification of uncertain outcomes. These determine whether the checkout contract needs additional steps. Use a supported secure collection mechanism; order identifier and amount alone do not establish a real payment.

## Impacted services and implementation details

- **Payment Service:** Implement authentication, translation and response interpretation. Distinguish success, decline and uncertainty. Verify repeat-request semantics and retention rather than assuming compatibility. Refund against the original transaction and distinguish confirmed from unresolved refunds. Establish supported lookup or notifications for unresolved outcomes. Exclude credentials and sensitive payment information from logs/responses.
- **Customer Portal:** Integrate hosted checkout or a supported embedded component. Present completion, decline, further customer action and uncertainty clearly. Preserve the original attempt on return/retry. Browser redirects or success messages are not authoritative payment confirmation.
- **Order Service:** Pass required payment/session references and support intermediate states for customer action or delayed confirmation. Fulfill only on authoritative outcomes. Uncertainty does not justify another charge or immediate stock release. Coordinate refunds without assuming immediate completion.
- **Deployment/operations:** Separate test and production configuration, protect credentials, provide investigation/monitoring for unresolved payments/refunds, and confirm provider requirements before real transactions.
- **Other services:** Inventory, Shipping and Notification need no new interfaces inherently; their actions still depend on the appropriate confirmed outcomes.

## Implementation order

1. Confirm collection experience, provider operations, duplicate protections and outcome verification; identify customer-interaction requirements.
2. Build Payment integration in the provider test environment and cover success, decline, timeout, repeated requests and refunds.
3. Adapt Order references/states and safe confirmation/recovery before fulfillment.
4. Integrate Portal collection/return flow. Parallel frontend/backend work is possible once interactions are agreed.
5. Validate abandonment, delayed confirmation, duplicate notifications, uncertainty and repeated refunds; enable gradually. Preserve original provider/attempt associations. Switching providers does not resolve an uncertain existing transaction.

## How this approach satisfies the request

- Replaces the mock through a complete provider integration rather than an address change alone.
- Adds supported customer payment collection.
- Preserves authoritative checkout decisions and original attempt identity.
- Keeps refunds associated with their original transactions and verified outcomes.
- Contains provider-specific behavior primarily within Payment Service.

## Alternatives and recommendation

- **Hosted checkout — preferred initially if supported:** Less custom collection work, but requires redirect/return handling and gives less UI control.
- **Embedded provider component:** Keeps customers in Portal but adds frontend and state-coordination work.
- **Provider-neutral gateway:** Useful for future multiple providers, but adds another dependency and operational layer.

Prefer hosted checkout when supported and compatible with requirements. Prefer embedded collection when staying in Portal is important. Choose based on verified provider capabilities, not assumptions.
