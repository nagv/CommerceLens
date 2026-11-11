# Plan evaluation and review

Review status: 18 Plan-mode cases are stored in golden.jsonl: all 18 approved. All 24 Ask cases remain approved. Plan 12 now follows the investigation-only debugging policy. Replan UI/API is implemented. Both Replan cases call the structured engine operation shared with POST /api/replan.

## Scoring contract

Actual implementation plans receive eight separate semantic scores and reasons. Behavioral responses and debugging leads use their own acceptance criteria instead:

| Dimension | What sufficient detail means |
|---|---|
| Overall strategy | A clear, coherent approach with responsibilities, assumptions and boundaries |
| Service impacts | Necessary services and reasons, distinguishing required from conditional changes |
| Per-service details | Separate high-level descriptions of changes, interactions and relevant failure handling |
| Implementation order | Organized stages with prerequisites, dependencies and possible parallel work |
| Requirement coverage | Break the request into parts and explain how the approach satisfies each |
| Alternatives | Brief but meaningful variations and trade-offs when applicable |
| Recommendation rationale | Explain why the selected approach fits better and when another would be preferable |
| Grounding | Correct current facts; proposals and unverified assumptions explicitly distinguished |

Scores: 0 = missing/incorrect, 1 = relevant but vague/incomplete, 2 = specific and sufficient. Headings or length alone do not earn credit. Multiple valid approaches can pass review. Ground truth concerns current facts, not one mandatory implementation.

Alternatives policy is per case: required when reviewers know meaningful alternatives exist; not_applicable when they do not; conditional when applicability needs judgment. Only alternatives may receive null, with an explanation. Null is excluded from averages, not treated as a perfect score. Missing alternatives must score 0 when required. A plan must still explain why the recommended approach fits even if alternatives do not apply.

The existing plan_quality summary is the mean of applicable dimension scores divided by two (0–1). Individual dimensions remain 0–2; groundedness is grounding divided by two. Critical issues and explanations are retained locally; dimension explanations accompany LangSmith feedback. No production acceptance threshold has been set: a high mean must not hide a critical unsupported premise.

Factual RAGAS metrics remain skipped for plans. These rubrics use an LLM judge and require human calibration. Path/hash evidence identifies sources but is not file content supplied to the judge. verified_current_facts are reviewer-checked facts; retrieved contexts remain the assistant's runtime evidence.

## Dataset coverage

| Category | Cases | Review focus |
|---|---:|---|
| Single service | 2 | Useful scoped changes without invented dependencies |
| Cross-service | 4 | Integration, sequence and compatibility |
| Application-wide | 2 | Coherent strategy and phased adoption |
| External dependencies | 2 | Provider capability checks, boundaries and alternatives |
| Missing information or constraints | 2 | Clarification, assumptions and conditional recommendations |
| Irrelevant or infeasible requests | 2 | Appropriate response instead of an invented implementation |
| Replan | 2 | Respect selected alternative and original requirements; structured revision tests |
| Debugging | 2 | Missing email and misleading payment diagnosis; investigation leads only |

Behavioral cases use behavior-specific grading. Debugging cases (including Plan 12) use response_policy=investigation_leads: grade known/unknown separation, relevant services, grounded hypotheses, ordered checks and evidence requests. Do not reward implementation plans, service changes or selected fixes. plan_quality is null. Application factual claims still need citations. All debugging examples are approved; no live evaluation of the completed set is claimed.

## Approved detailed examples

These examples show the required depth and organization. Implementation examples are embedded as example_plan; behavioral expected answers are stored as reference, alongside their acceptance criteria. They are not exact-match references, and proposals must not be treated as existing facts.

- [Plan 1: destination-based shipping](plan-examples/destination-shipping.md) — approved; expanded overall strategy, separate service changes, ordered stages, requirement mapping and justified alternatives.
- [Plan 2: recover failed notifications](plan-examples/notification-replay.md) — approved; operator-controlled recovery, history and duplicate protection, conditional interface impacts and alternative approaches.

Meaningful alternatives are required in the approved cases. The replay case requires Notification Worker; Customer Portal and Order impacts depend on the selected approach. All 18 Plan-mode cases, including the two additional debugging cases, are approved.

- [Plan 3: recover uncertain payment outcomes](plan-examples/payment-reconciliation.md) — approved; original-payment verification, safe continuation, conditional service impacts and recovery alternatives.

- [Plan 4: extend order confirmation emails](plan-examples/order-email-products.md) — approved; event evolution, consumer/provider compatibility, rollout order and preserved delivery protections.

- [Plan 5: filter loaded orders by status](plan-examples/portal-status-filter.md) — approved; single-service UI scope, loaded-data boundaries, accessibility and useful alternatives.

- [Plan 6: configurable notification attempts](plan-examples/notification-attempt-limit.md) — approved; bounded configuration, restart consistency and preservation of terminal outcomes.

- [Plan 7: application-wide troubleshooting](plan-examples/checkout-observability.md) — approved; all-service diagnostics, asynchronous continuity, timing and external visibility limits.

- [Plan 8: application-wide readiness](plan-examples/service-readiness.md) — approved; health semantics, deployment enforcement, capability degradation and recovery.

- [Plan 9: integrate an external payment provider](plan-examples/external-payment-provider.md) — approved; complete provider integration, customer collection, authoritative outcomes and refunds.

- [Plan 10: external shipment tracking](plan-examples/shipment-tracking.md) — approved; provider lookup, freshness, separate order/delivery states and resilient display.

- [Plan 11: clarify retry scope](plan-examples/clarify-retries.md) — approved; single-turn clarification, relevant options and request to re-ask with operation/outcome.

Behavioral Plan cases expecting clarify, redirect, unknown or uncertain use the semantic behavior rubric with plan_quality null; implementation dimensions are not required. Routing is based on the case expectation, not the generated answer label. Optional citations apply only without factual assertions. Plan mode supports early clarification/scope routing. These paths are covered by local mocked tests, not a live judge calibration yet.

- [Plan 12: missing production performance evidence](plan-examples/production-checkout-evidence.md) — approved; acknowledge missing operational evidence and provide investigation leads, ordered checks and evidence requests without proposing fixes. Uses uncertain behavior scoring rather than implementation-plan dimensions.

- [Plan 13: unrelated application request](plan-examples/unrelated-application.md) — approved; brief scope redirect without invented architecture, citations or implementation sections.

- [Plan 14: incompatible tracking requirements](plan-examples/incompatible-tracking-requirements.md) — approved; explicit constraint conflict, no impossible guarantee, and conditional alternatives requiring an agreed requirement change. Uses the existing uncertain behavior route with case-specific criteria; do not confuse constraint infeasibility with missing evidence.

- [Plan 15: replan using provider quotes](plan-examples/replan-provider-quotes.md) — approved; selected-alternative adherence, preserved original requirements, no regional fallback and quote consistency. The original request, full previous proposal and selection are embedded in the question and retained as replan_context. execution_contract=structured_replan: the evaluator calls Assistant.replan, shared with the API. Browser state is not persisted across reloads.

- [Plan 16: replan notification recovery as a command](plan-examples/replan-notification-command.md) — approved; respects excluded Portal/Order changes and preserves recovery safeguards. Structured Replan engine test; API and browser checks are reported separately.
- [Plan 17: missing confirmation email](plan-examples/debug-missing-email.md) — approved; trace publication, messaging, worker and provider as investigation leads without triggering recovery.
- [Plan 18: payment timeout diagnosis](plan-examples/debug-payment-timeout.md) — approved; reject timeout-as-failure, inspect original attempt and provider evidence without proposing another charge.

The assistant receives a debugging-specific instruction even in Plan mode. Local mocked tests verify that this instruction reaches the model and that the judge uses the investigation-only policy with no plan-quality score. They do not demonstrate live-model adherence or calibrated judging; live evaluation remains pending.
