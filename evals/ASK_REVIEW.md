# Ask golden dataset review

24 single-turn Ask cases: 9 approved references and 15 new review candidates. Four existing Plan cases remain in golden.jsonl and have not been changed by this expansion.

Primary categories: 3 single-service, 5 cross-service, 2 application overview, 2 external dependencies, 3 unknown information, 3 insufficient evidence, 2 irrelevant, 4 incomplete.

The two external-dependency cases also cover single-service behavior. Category counts are coverage targets, not production traffic weights. Multi-turn follow-up flows are excluded.

Run Ask only: `.ai-venv/Scripts/python.exe -m commercelens_ai evaluate --mode ask --judge --ragas --langsmith`

New cases remain pending human approval. This development set is not a held-out production benchmark. RAGAS is skipped for behavioral cases; semantic judging evaluates the expected behavior. See ASK_POLICY.md for scoring rules.

## 1. price-owner

Review: **approved** | Category: `single_service` | Expected behavior: `answer`

**Question:** Which service owns authoritative product prices and available stock?

**Expected response:** Inventory Service owns authoritative product prices and available stock.

**Acceptance criteria:**

- Convey the reference meaning accurately in high-level language.
- Do not require table names or implementation mechanisms.
- Support application facts with citations.

**Sources:** `openwiki/checkout-flow.md`

## 2. checkout-coordinator

Review: **approved** | Category: `cross_service` | Expected behavior: `answer`

**Question:** How does checkout coordinate inventory, payment and shipping?

**Expected response:** Order Service coordinates checkout by reserving inventory, requesting payment authorization through Payment Service, and creating a shipment through Shipping Service. On success, it confirms the order and durably records a confirmation event. Before requesting payment, it records an uncertain payment state to support safe recovery.

**Acceptance criteria:**

- Convey the reference meaning accurately in high-level language.
- Do not require table names or implementation mechanisms.
- Support application facts with citations.

**Sources:** `openwiki/checkout-flow.md`

## 3. portal-idempotency

Review: **approved** | Category: `cross_service` | Expected behavior: `answer`

**Question:** How does the portal preserve a checkout attempt across retries?

**Expected response:** Customer Portal saves checkout details in browser storage and reuses the same checkout attempt when retrying. Order Service recognizes the existing attempt to avoid creating duplicate orders.

**Acceptance criteria:**

- Convey the reference meaning accurately in high-level language.
- Do not require table names or implementation mechanisms.
- Support application facts with citations.

**Sources:** `openwiki/checkout-flow.md`, `openwiki/data-and-events.md`

## 4. notification-delivery

Review: **approved** | Category: `cross_service` | Expected behavior: `answer`

**Question:** How are order confirmation emails processed and duplicates prevented?

**Expected response:** Order Service publishes a confirmation event after checkout succeeds. Notification Worker processes the event, sends the confirmation email through an email provider, and tracks delivery to avoid resending completed notifications. Preventing duplicates during interrupted delivery also relies on the email provider recognizing repeat requests.

**Acceptance criteria:**

- Convey the reference meaning accurately in high-level language.
- Do not require table names or implementation mechanisms.
- Support application facts with citations.

**Sources:** `openwiki/checkout-flow.md`, `openwiki/data-and-events.md`

## 5. outbox

Review: **approved** | Category: `cross_service` | Expected behavior: `answer`

**Question:** What ensures order confirmation events can be delivered reliably?

**Expected response:** Order Service saves confirmation events before publishing them and retries when delivery is unsuccessful. It marks an event as published only after the messaging system confirms receipt. Notification Worker handles repeat events to avoid duplicate notifications.

**Acceptance criteria:**

- Convey the reference meaning accurately in high-level language.
- Do not require table names or implementation mechanisms.
- Support application facts with citations.

**Sources:** `openwiki/data-and-events.md`

## 6. payment-timeout-conflict

Review: **approved** | Category: `cross_service` | Expected behavior: `answer`

**Question:** What happens after a payment timeout?

**Expected response:** Order Service treats the payment outcome as uncertain and retains the inventory reservation. The payment must be checked with the payment provider before retrying because a timeout does not mean no charge occurred.

**Acceptance criteria:**

- Convey the reference meaning accurately in high-level language.
- Do not require table names or implementation mechanisms.
- Support application facts with citations.

**Sources:** `openwiki/application-overview.md`, `../commercelens-order-service/openwiki/workflows/failure-handling.md`, `../commercelens-payment-service/openwiki/service-context.md`

## 7. payment-persistence

Review: **approved** | Category: `external_dependencies` | Expected behavior: `answer`

**Question:** Does Payment Service use its own database or messaging system?

**Expected response:** No. Payment Service forwards payment and refund requests to a payment provider. It relies on that provider to retain payment records and prevent duplicate processing.

**Acceptance criteria:**

- Convey the reference meaning accurately in high-level language.
- Do not require table names or implementation mechanisms.
- Support application facts with citations.

**Sources:** `../commercelens-payment-service/openwiki/service-context.md`

## 8. shipping-contract

Review: **approved** | Category: `external_dependencies` | Expected behavior: `answer`

**Question:** What is the shipping charge, and how are duplicate shipment requests handled?

**Expected response:** Shipping Service uses a fixed charge of $5 USD. It identifies repeat requests for the same order so the shipping provider can avoid creating duplicate shipments.

**Acceptance criteria:**

- Convey the reference meaning accurately in high-level language.
- Do not require table names or implementation mechanisms.
- Support application facts with citations.

**Sources:** `openwiki/checkout-flow.md`, `openwiki/data-and-events.md`

## 9. notification-gaps

Review: **approved** | Category: `single_service` | Expected behavior: `answer`

**Question:** What happens if an order confirmation email cannot be delivered?

**Expected response:** Notification Worker retries delivery up to three times. If all attempts fail, it marks the notification as failed; no replay feature is currently implemented. The confirmed order remains unchanged.

**Acceptance criteria:**

- Convey the reference meaning accurately in high-level language.
- Do not require table names or implementation mechanisms.
- Support application facts with citations.

**Sources:** `openwiki/application-overview.md`

## 10. portal-capabilities

Review: **pending** | Category: `single_service` | Expected behavior: `answer`

**Question:** What can a user do in the Customer Portal?

**Expected response:** Customer Portal lets users browse products, manage a cart, submit checkout, and view order details and notification delivery status.

**Acceptance criteria:**

- Mention shopping and checkout as well as order and notification visibility.
- Do not invent accounts, loyalty programs or order editing.
- Use high-level language and do not invent unsupported facts.

**Sources:** `openwiki/checkout-flow.md`, `../commercelens-customer-portal/openwiki/service-context.md`

## 11. application-purpose

Review: **pending** | Category: `application_overview` | Expected behavior: `answer`

**Question:** What does CommerceLens do for a customer?

**Expected response:** CommerceLens is a demo shopping application where customers browse products and place orders. Its services coordinate stock reservation, payment, shipment creation and confirmation emails.

**Acceptance criteria:**

- Explain business purpose and the customer journey without implementation details.
- Use high-level language and do not invent unsupported facts.

**Sources:** `openwiki/checkout-flow.md`, `openwiki/service-catalog.md`

## 12. application-responsibilities

Review: **pending** | Category: `application_overview` | Expected behavior: `answer`

**Question:** How are responsibilities divided across the application?

**Expected response:** Customer Portal provides the user interface. Order Service coordinates checkout; Inventory Service owns product prices and stock; Payment Service connects to the payment provider; Shipping Service connects to the shipping provider; Notification Worker sends confirmation emails through an email provider.

**Acceptance criteria:**

- Cover all six service responsibilities and distinguish services from their providers.
- Use high-level language and do not invent unsupported facts.

**Sources:** `openwiki/service-catalog.md`, `openwiki/dependencies.md`

## 13. unknown-live-orders

Review: **pending** | Category: `unknown_information` | Expected behavior: `unknown`

**Question:** How many orders were placed today?

**Expected response:** I cannot determine today's order count from static application documentation; live order data is needed.

**Acceptance criteria:**

- Clearly acknowledge unavailable live data.
- Do not fabricate a count, order status or claim to have queried a live system.
- Use high-level language and do not invent unsupported facts.

**Sources:** `evals/ASK_POLICY.md`

## 14. unknown-order-status

Review: **pending** | Category: `unknown_information` | Expected behavior: `unknown`

**Question:** Has order CL-98765 been shipped?

**Expected response:** I cannot determine the live shipping status of a specific order from the available documentation. An order or shipment lookup is needed.

**Acceptance criteria:**

- Clearly acknowledge unavailable live data.
- Do not fabricate a count, order status or claim to have queried a live system.
- Use high-level language and do not invent unsupported facts.

**Sources:** `evals/ASK_POLICY.md`

## 15. unknown-live-stock

Review: **pending** | Category: `unknown_information` | Expected behavior: `unknown`

**Question:** How many units of BOOK-001 are available right now?

**Expected response:** I cannot determine current stock from static documentation. A live inventory lookup is needed; example or initial stock values are not current availability.

**Acceptance criteria:**

- Clearly acknowledge unavailable live data.
- Do not fabricate a count, order status or claim to have queried a live system.
- Use high-level language and do not invent unsupported facts.

**Sources:** `evals/ASK_POLICY.md`

## 16. uncertain-email-guarantee

Review: **pending** | Category: `insufficient_evidence` | Expected behavior: `uncertain`

**Question:** Can you guarantee that confirmation emails are never duplicated?

**Expected response:** Notification Worker tracks delivery and avoids resending completed notifications. After interrupted delivery, duplicate prevention also depends on the email provider recognizing repeat requests, so an unconditional no-duplicates guarantee is not established.

**Acceptance criteria:**

- Explain documented protection and its dependency on the provider.
- Do not claim exactly-once delivery or an unconditional guarantee.
- Use high-level language and do not invent unsupported facts.

**Sources:** `../commercelens-notification-worker/openwiki/service-context.md`

## 17. uncertain-payment-guarantee

Review: **pending** | Category: `insufficient_evidence` | Expected behavior: `uncertain`

**Question:** Do safe checkout retries guarantee that a payment provider can never charge twice?

**Expected response:** The application reuses checkout attempts and sends repeat-request identifiers to the payment provider. Preventing duplicate charges also depends on the provider honoring those identifiers; the application documentation does not establish an unconditional guarantee.

**Acceptance criteria:**

- Describe safeguards at a high level and explain provider dependence.
- Neither guarantee duplicate prevention nor claim duplicates definitely occur.
- Use high-level language and do not invent unsupported facts.

**Sources:** `openwiki/checkout-flow.md`, `../commercelens-payment-service/openwiki/service-context.md`

## 18. uncertain-email-arrival

Review: **pending** | Category: `insufficient_evidence` | Expected behavior: `uncertain`

**Question:** If notification delivery is marked successful, can we be certain the customer received and read the email?

**Expected response:** The worker records success when the email provider confirms sending. That does not establish that the customer received or read the email; the available evidence does not provide that confirmation.

**Acceptance criteria:**

- Distinguish provider sending confirmation from customer receipt and reading.
- Do not invent read receipts or mailbox telemetry.
- Use high-level language and do not invent unsupported facts.

**Sources:** `../commercelens-notification-worker/openwiki/service-context.md`

## 19. irrelevant-travel

Review: **pending** | Category: `irrelevant` | Expected behavior: `redirect`

**Question:** Recommend a holiday destination.

**Expected response:** I can help with CommerceLens application questions and high-level change plans. Please ask about the application.

**Acceptance criteria:**

- Briefly and politely state the assistant scope.
- Do not perform the unrelated request or invent a connection to CommerceLens.
- Use high-level language and do not invent unsupported facts.

**Sources:** `evals/ASK_POLICY.md` (behavior policy; no application factual claims required).

## 20. irrelevant-poem

Review: **pending** | Category: `irrelevant` | Expected behavior: `redirect`

**Question:** Write a poem about the moon.

**Expected response:** I can help with CommerceLens application questions and high-level change plans. Please ask about the application.

**Acceptance criteria:**

- Briefly and politely state the assistant scope.
- Do not perform the unrelated request or invent a connection to CommerceLens.
- Use high-level language and do not invent unsupported facts.

**Sources:** `evals/ASK_POLICY.md` (behavior policy; no application factual claims required).

## 21. clarify-failure

Review: **pending** | Category: `incomplete` | Expected behavior: `clarify`

**Question:** What happens if it fails?

**Expected response:** Which operation do you mean: payment, shipping, or notification delivery?

**Acceptance criteria:**

- Ask a focused clarification question identifying the missing subject or operation.
- Do not assume a service or give a definitive application answer.
- Evaluate only this response, without a follow-up conversation.
- Use high-level language and do not invent unsupported facts.

**Sources:** `evals/ASK_POLICY.md` (behavior policy; no application factual claims required).

## 22. clarify-provider

Review: **pending** | Category: `incomplete` | Expected behavior: `clarify`

**Question:** Which provider does it use?

**Expected response:** Which integration do you mean: payment, shipping, or email?

**Acceptance criteria:**

- Ask a focused clarification question identifying the missing subject or operation.
- Do not assume a service or give a definitive application answer.
- Evaluate only this response, without a follow-up conversation.
- Use high-level language and do not invent unsupported facts.

**Sources:** `evals/ASK_POLICY.md` (behavior policy; no application factual claims required).

## 23. clarify-retry

Review: **pending** | Category: `incomplete` | Expected behavior: `clarify`

**Question:** Is retrying safe?

**Expected response:** Which operation are you retrying, and what happened on the previous attempt?

**Acceptance criteria:**

- Ask a focused clarification question identifying the missing subject or operation.
- Do not assume a service or give a definitive application answer.
- Evaluate only this response, without a follow-up conversation.
- Use high-level language and do not invent unsupported facts.

**Sources:** `evals/ASK_POLICY.md` (behavior policy; no application factual claims required).

## 24. clarify-data

Review: **pending** | Category: `incomplete` | Expected behavior: `clarify`

**Question:** Where is it stored?

**Expected response:** Which information do you mean, such as product information, orders, or notification status?

**Acceptance criteria:**

- Ask a focused clarification question identifying the missing subject or operation.
- Do not assume a service or give a definitive application answer.
- Evaluate only this response, without a follow-up conversation.
- Use high-level language and do not invent unsupported facts.

**Sources:** `evals/ASK_POLICY.md` (behavior policy; no application factual claims required).

