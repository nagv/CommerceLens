# Revised, reviewed evaluation — 10 November 2026

All 45 application cases were attempted using the revised references. The three new variants and three selected calibration judgments were approved by the user before this run. Application implementation was not changed for this rerun.

Dataset SHA-256: `b0013d20ec9e815db1dbd619cb7a9a1206f0efcaf24ee68bf0b2146841521dc9`.

## Results

- Application responses accepted for evaluation: 36/45.
- Execution failures: 9.
- Critical gates: {"meets_critical_requirements": 15, "not_assessed": 16, "fail": 14}.
- Judge coverage: {"ok": 29, "skipped": 9, "error": 7}.
- RAGAS coverage: {"ok": 8, "error": 3, "skipped": 34}.
- Calibration agreement: 7/10; 2 invalid assessments.

Gate failures are judge findings requiring review. Missing/error assessments are not passes or zero-quality answers. Calibration remains imperfect; this is not a production release certification.

## Execution failures

- `outbox`: AssistantStatus:invalid_citations.
- `plan-event-contract`: AssistantStatus:invalid_citations.
- `plan-notification-attempt-limit`: AssistantStatus:error.
- `plan-shipment-tracking`: AssistantStatus:invalid_citations.
- `plan-incompatible-tracking-requirements`: AssistantStatus:error.
- `replan-provider-quotes`: AssistantStatus:invalid_citations.
- `debug-missing-confirmation-email`: AssistantStatus:error.
- `debug-confirmed-decline-stock`: AssistantStatus:error.
- `replan-notification-portal`: AssistantStatus:error.

## Newly reviewed variants

| Case | Execution | Judge | Critical gate |
|---|---|---|---|
| debug-confirmed-decline-stock | failed | skipped | not_assessed |
| plan-historical-status-filter | ok | error | not_assessed |
| replan-notification-portal | failed | skipped | not_assessed |

## Valid semantic failures

- `portal-idempotency`: truthful_current_claims, expected_response.
- `notification-delivery`: truthful_current_claims, expected_response.
- `notification-gaps`: truthful_current_claims, expected_response.
- `plan-variable-shipping`: truthful_current_claims, request_outcome, feasible_boundaries.
- `plan-payment-reconciliation`: request_outcome, feasible_boundaries.
- `application-purpose`: expected_response.
- `unknown-live-orders`: truthful_current_claims, expected_response.
- `unknown-order-status`: truthful_current_claims, expected_response.
- `unknown-live-stock`: truthful_current_claims, expected_response.
- `clarify-retry`: expected_response.
- `plan-portal-status-filter`: truthful_current_claims, request_outcome, feasible_boundaries, loaded_scope.
- `plan-service-readiness`: request_outcome, feasible_boundaries.
- `plan-external-payment-provider`: truthful_current_claims, request_outcome, feasible_boundaries.
- `plan-unrelated-application`: expected_response.

## RAGAS metrics

| Metric | Mean | Valid count |
|---|---:|---:|
| ragas_answer_relevancy | 0.892 | 8 |
| ragas_context_recall | 0.917 | 8 |
| ragas_factual_correctness(mode=f1) | 0.390 | 8 |
| ragas_faithfulness | 0.915 | 8 |
| ragas_llm_context_precision_with_reference | 0.583 | 8 |

## Interpretation and artifacts

One application attempt per case. The judge may make one bounded format-correction attempt; its history is retained in scoring_attempts/validation_errors. No application answer was regenerated. One RAGAS task remained pending for over 14 minutes and was interrupted; its saved answer was recovered and its semantic judgment rerun because the original in-memory judgment was unavailable. The RAGAS timeout remains an error, with recovery recorded separately. Do not attribute changed results solely to reference review: generation and judging vary, and provider errors affect coverage.

Calibration still exposes invalid Replan assessments and conflation of correctness with grounding on the stale-document fixture. Human approval establishes intended judgments; it does not repair the judge.

LangSmith upload: **ok**. [Experiment](https://smith.langchain.com/o/7ca977ce-d907-4402-9fdb-1c997438986a/projects/p/44702048-2ded-456f-ae14-232c003481ec).

Local records: `evals/results/live-reviewed-v3-20261110/` contains `summary.json`, `runs.jsonl`, saved `generation-*.json`, and `human_review.csv`. Calibration records are in `evals/results/calibration-reviewed-v3-20261110/`. Prior experiments remain unchanged.
