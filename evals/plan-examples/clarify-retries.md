# Plan 11: clarify retry scope

Question: Plan a change to improve retries in CommerceLens.

Status: Approved. Single-turn behavioral reference; not an implementation plan.

Please clarify which operation you want to improve retries for. Possible areas include:

- Checkout or payment: Recovering from interrupted requests or uncertain payment outcomes without charging customers twice.
- Shipment creation: Handling provider failures without creating duplicate shipments.
- Confirmation emails: Adjusting automatic delivery attempts or allowing operators to retry failed notifications.

Also, describe the problem you want to solve—for example, temporary failures, attempts stopping too early, or manual recovery taking too long.

Please re-ask the question with the operation and desired outcome, so I can provide a focused implementation strategy, impacted services, implementation order, and relevant alternatives.
