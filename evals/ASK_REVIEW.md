# Ask golden dataset review

24 single-turn Ask cases: 24 approved references and no pending review candidates. Four existing Plan cases remain in golden.jsonl and have not been changed by this expansion.

Primary categories: 3 single-service, 5 cross-service, 2 application overview, 2 external dependencies, 3 unknown information, 3 insufficient evidence, 2 irrelevant, 4 incomplete.

The two external-dependency cases also cover single-service behavior. Category counts are coverage targets, not production traffic weights. Multi-turn follow-up flows are excluded.

Run Ask only: `.ai-venv/Scripts/python.exe -m commercelens_ai evaluate --mode ask --judge --ragas --langsmith`

All 24 Ask cases have been approved by the user. This development set is not a held-out production benchmark. RAGAS is skipped for behavioral cases; semantic judging evaluates the expected behavior. See ASK_POLICY.md for scoring rules.

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

Review: **approved** | Category: `single_service` | Expected behavior: `answer`

**Question:** What can a user do in the Customer Portal?

**Expected response:** Customer Portal lets users browse products, manage a cart, submit checkout, and view order details and notification delivery status.

**Acceptance criteria:**

- Mention shopping and checkout as well as order and notification visibility.
- Do not invent accounts, loyalty programs or order editing.
- Use high-level language and do not invent unsupported facts.

**Sources:** `openwiki/checkout-flow.md`, `../commercelens-customer-portal/openwiki/service-context.md`

## 11. application-purpose

Review: **approved** | Category: `application_overview` | Expected behavior: `answer`

**Question:** What does CommerceLens do for a customer?

**Expected response:** CommerceLens is a demo shopping application where customers browse products and place orders. Its services coordinate stock reservation, payment, shipment creation and confirmation emails.

**Acceptance criteria:**

- Explain business purpose and the customer journey without implementation details.
- Use high-level language and do not invent unsupported facts.

**Sources:** `openwiki/checkout-flow.md`, `openwiki/service-catalog.md`

## 12. application-responsibilities

Review: **approved** | Category: `application_overview` | Expected behavior: `answer`

**Question:** What are the core services in CommerceLens, and what is the purpose of each?

**Expected response:** Customer Portal provides the user interface. Order Service coordinates checkout. Inventory Service owns product prices and stock. Payment Service handles payment and refund requests through a payment provider. Shipping Service creates shipments through a shipping provider. Notification Worker sends confirmation emails through an email provider.

**Acceptance criteria:**

- Cover all six service responsibilities and distinguish services from their providers.
- Use high-level language and do not invent unsupported facts.

**Sources:** `openwiki/service-catalog.md`, `openwiki/dependencies.md`

## 13. unknown-live-orders

Review: **approved** | Category: `unknown_information` | Expected behavior: `unknown`

**Question:** How many orders were placed today?

**Expected response:** I don't have information about how many orders were placed today.

**Acceptance criteria:**

- Clearly acknowledge unavailable live data.
- Do not fabricate a count, order status or claim to have queried a live system.
- Use high-level language and do not invent unsupported facts.

**Sources:** `evals/ASK_POLICY.md`

## 14. unknown-order-status

Review: **approved** | Category: `unknown_information` | Expected behavior: `unknown`

**Question:** Has order CL-98765 been shipped?

**Expected response:** I don't have information about the shipping status of order CL-98765.

**Acceptance criteria:**

- Clearly acknowledge unavailable live data.
- Do not fabricate a count, order status or claim to have queried a live system.
- Use high-level language and do not invent unsupported facts.

**Sources:** `evals/ASK_POLICY.md`

## 15. unknown-live-stock

Review: **approved** | Category: `unknown_information` | Expected behavior: `unknown`

**Question:** How many units of BOOK-001 are available right now?

**Expected response:** I don't have information about the current stock available for BOOK-001.

**Acceptance criteria:**

- Clearly acknowledge unavailable live data.
- Do not fabricate a count, order status or claim to have queried a live system.
- Use high-level language and do not invent unsupported facts.

**Sources:** `evals/ASK_POLICY.md`

## 16. uncertain-email-guarantee

Review: **approved** | Category: `insufficient_evidence` | Expected behavior: `uncertain`

**Question:** Can you guarantee that confirmation emails are never duplicated?

**Expected response:** Notification Worker tracks delivery to avoid duplicate emails, but prevention also depends on the email provider. I cannot guarantee that duplicates will never occur.

**Acceptance criteria:**

- Explain documented protection and its dependency on the provider.
- Do not claim exactly-once delivery or an unconditional guarantee.
- Use high-level language and do not invent unsupported facts.

**Sources:** `../commercelens-notification-worker/openwiki/service-context.md`

## 17. uncertain-payment-guarantee

Review: **approved** | Category: `insufficient_evidence` | Expected behavior: `uncertain`

**Question:** Do safe checkout retries guarantee that a payment provider can never charge twice?

**Expected response:** The application recognizes repeat checkout attempts to help prevent duplicate charges, but prevention also depends on the payment provider. I cannot guarantee that duplicate charges will never occur.

**Acceptance criteria:**

- Describe safeguards at a high level and explain provider dependence.
- Neither guarantee duplicate prevention nor claim duplicates definitely occur.
- Use high-level language and do not invent unsupported facts.

**Sources:** `openwiki/checkout-flow.md`, `../commercelens-payment-service/openwiki/service-context.md`

## 18. uncertain-email-arrival

Review: **approved** | Category: `insufficient_evidence` | Expected behavior: `uncertain`

**Question:** If notification delivery is marked successful, can we be certain the customer received and read the email?

**Expected response:** A successful status means the email provider confirmed sending the email. It does not confirm that the customer received or read it.

**Acceptance criteria:**

- Distinguish provider sending confirmation from customer receipt and reading.
- Do not invent read receipts or mailbox telemetry.
- Use high-level language and do not invent unsupported facts.

**Sources:** `../commercelens-notification-worker/openwiki/service-context.md`

## 19. irrelevant-travel

Review: **approved** | Category: `irrelevant` | Expected behavior: `redirect`

**Question:** Recommend a holiday destination.

**Expected response:** I can help with questions about CommerceLens. Please ask something related to the application.

**Acceptance criteria:**

- Briefly and politely state the assistant scope.
- Do not perform the unrelated request or invent a connection to CommerceLens.
- Use high-level language and do not invent unsupported facts.

**Sources:** `evals/ASK_POLICY.md` (behavior policy; no application factual claims required).

## 20. irrelevant-poem

Review: **approved** | Category: `irrelevant` | Expected behavior: `redirect`

**Question:** Write a poem about the moon.

**Expected response:** I can help with questions about CommerceLens. Please ask something related to the application.

**Acceptance criteria:**

- Briefly and politely state the assistant scope.
- Do not perform the unrelated request or invent a connection to CommerceLens.
- Use high-level language and do not invent unsupported facts.

**Sources:** `evals/ASK_POLICY.md` (behavior policy; no application factual claims required).

## 21. clarify-failure

Review: **approved** | Category: `incomplete` | Expected behavior: `clarify`

**Question:** What happens if it fails?

**Expected response:** Which operation are you referring to—for example, checkout, payment, shipping, or notification delivery? Please re-ask your question with more details.

**Acceptance criteria:**

- Ask which operation the user means and offer relevant examples.
- Ask the user to re-ask the question with more details.
- Do not assume a service or give a definitive application answer.
- Evaluate only this response, without a follow-up conversation.

**Sources:** `evals/ASK_POLICY.md` (behavior policy; no application factual claims required).

## 22. clarify-provider

Review: **approved** | Category: `incomplete` | Expected behavior: `clarify`

**Question:** Which provider does it use?

**Expected response:** Which service are you referring to—for example, payment, shipping, or email notifications? Please re-ask your question with more details.

**Acceptance criteria:**

- Ask which service the user means and offer relevant examples.
- Ask the user to re-ask the question with more details.
- Do not assume a service or give a definitive application answer.
- Evaluate only this response, without a follow-up conversation.

**Sources:** `evals/ASK_POLICY.md` (behavior policy; no application factual claims required).

## 23. clarify-retry

Review: **approved** | Category: `incomplete` | Expected behavior: `clarify`

**Question:** Is retrying safe?

**Expected response:** Which operation are you retrying—for example, checkout, payment, or notification delivery? Please re-ask your question with more details, including what happened on the previous attempt.

**Acceptance criteria:**

- Ask which operation the user is retrying and offer relevant examples.
- Ask the user to re-ask with more details, including the outcome of the previous attempt.
- Do not assume a service or assert that retrying is safe.
- Evaluate only this response, without a follow-up conversation.

**Sources:** `evals/ASK_POLICY.md` (behavior policy; no application factual claims required).

## 24. clarify-data

Review: **approved** | Category: `incomplete` | Expected behavior: `clarify`

**Question:** Where is it stored?

**Expected response:** Which information are you referring to—for example, product information, orders, or notification status? Please re-ask your question with more details.

**Acceptance criteria:**

- Ask which information the user means and offer relevant examples.
- Ask the user to re-ask the question with more details.
- Do not assume a data type or give a definitive application answer.
- Evaluate only this response, without a follow-up conversation.

**Sources:** `evals/ASK_POLICY.md` (behavior policy; no application factual claims required).

