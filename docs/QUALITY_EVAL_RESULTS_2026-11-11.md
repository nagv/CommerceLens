# Full quality evaluation and evaluator fixes — November 11, 2026

## Scope and integrity
The original V1 baseline remains frozen and checksum-verified. The same 45 golden questions, references and numerical critical gates were used for two full repetitions (90 runs). No service code, wiki content, master summaries or Pinecone documents were changed in this iteration.

Application improvements: cross-service retrieval for coordination/duplicate questions, clearer high-level answer guidance, explicit live-data limitations and differentiation of current versus proposed capabilities. Earlier bounded retries, citation grouping and response-envelope repairs remain enabled.

Evaluator improvements: short evidence aliases restored to canonical IDs before strict validation; exact numbered excerpts instead of asking the model to copy quotations; retained validation reasons and attempt counts; bounded RAGAS SDK retries and isolated 180-second worker limits. These change judge input/transport, not the approved reference or numerical rules. This is therefore not a pure application-only A/B experiment. The model remains stochastic.

## Full-run results
[LangSmith experiment — 90 uploaded runs](https://smith.langchain.com/o/7ca977ce-d907-4402-9fdb-1c997438986a/projects/p/20c1a80e-cb6b-4f4b-b370-eb601ea64cdd). Evaluated application version: `450c07b`; local results: `evals/results/quality-final-20261111/`.

| Measure | V1 baseline | Repetition 1 | Repetition 2 |
|---|---:|---:|---:|
| Accepted execution | 30 | 44 | 44 |
| Application failures | 15 | 1 | 1 |
| Judge completed | 25 | 43 | 42 |
| Judge errors | 5 | 1 | 2 |
| Critical gates passed | 15 | 26 | 25 |
| Critical gates failed | 10 | 17 | 17 |
| Not assessed | 20 | 2 | 3 |
| RAGAS completed | 9 | 12 | 11 |
| RAGAS errors | 1 | 0 | 0 |
| Mean application latency (seconds) | 17.9 | 10.0 | 14.5 |

Execution improved from 30/45 to 44/45 in both repetitions. Conditional critical-gate pass rates among successfully judged answers are 15/25 (60.0%), 26/43 (60.5%), and 25/42 (59.5%). The runs demonstrate improved execution and evaluation coverage, **not a demonstrated answer-quality improvement**. More quality failures are visible because more cases can now be assessed. RAGAS is intentionally not applicable to all cases. Logical model-call metrics are not complete billing measurements: retries can add time and cost.

## Calibration and human-review flags
Calibration completed with no judge execution errors, but agreement remained 8/10. `ask-incomplete` was incorrectly accepted by the judge; `document-conflict` still failed to separate factual correctness from documentary grounding as expected. These are semantic grading disagreements, not successful calibration. Preserve them for review; do not treat automated gates as definitive production acceptance.

Source-backed adjudication note: the judge called dead-lettering nonexistent in notification-gaps. The actual implementation declares the dead-letter queue in services/notification-worker/src/main.ts:28–29 and rejects exhausted messages without requeue at lines 46 and 54. That rationale is incorrect. The same answer can still legitimately fail for excess implementation detail or missing required facts. Original scores were not overwritten.

## Repeat failures to prioritize
The following cases failed critical requirements in both repetitions (automated findings, subject to the calibration caveats):

- notification-delivery
- notification-gaps
- plan-variable-shipping
- plan-notification-replay
- plan-event-contract
- plan-notification-attempt-limit
- plan-service-readiness
- plan-shipment-tracking
- plan-incompatible-tracking-requirements
- debug-missing-confirmation-email

The principal application gaps are incomplete plan strategy/service impacts/implementation order/alternatives, missing cross-service or provider responsibilities, excessive implementation detail in Ask answers, and investigation/uncertainty boundaries. These remain unresolved quality work; execution recovery does not establish correctness.

## Full-run errors and later fixes
- Repetition 1: plan-portal-status-filter rejected a citation range `[S11–S18]`. Added bounded expansion of valid ranges; unknown/reversed ranges remain rejected.
- Repetition 2: checkout-coordinator received HTTP 529. Added this observed provider-overload status to the one-retry policy.
- Judge errors: outbox (invalid evidence assessment), clarify-failure and plan-production-checkout-evidence (invalid dimension). Field-specific schema feedback was added after the full run; saved-answer recovery is recorded separately below.

The two application edge cases were rerun with the later fixes in `evals/results/quality-edge-20261111/`: both executed and both were judged, but both still failed quality gates. Do not merge those results into a claim of 45/45 on the evaluated full-run version.

## Verification
140 regression tests passed, including rejection of fabricated citations, invented excerpt IDs, malformed judgments and unknown/reversed citation ranges. Frozen baseline checksums were verified. Full and targeted runs remain separate; prior interrupted diagnostic runs are not part of the reported 90 runs.

Reproduce a fresh full run with `.ai-venv/Scripts/python.exe scripts/run-quality-evaluation.py --output evals/results/NEW-RUN --repetitions 2`. The output directory must be new or empty. This sends evaluation content to configured providers and LangSmith, as previously authorized.

## Separate evaluator recovery

All three failed assessments were rescored successfully against the saved application answers after field-specific validation feedback. Outbox still failed quality; clarify-failure and plan-production-checkout-evidence passed. No application answer was regenerated and no original full-run error was replaced. Recovery remains stochastic evidence, not proof that the judge will always produce valid or correct assessments.

[Three-case recovery experiment](https://smith.langchain.com/o/7ca977ce-d907-4402-9fdb-1c997438986a/projects/p/264b13ab-0120-4d74-b34b-6734130951e9).
