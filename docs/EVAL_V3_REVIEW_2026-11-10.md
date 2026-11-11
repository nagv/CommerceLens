# CommerceLens evaluation v3 — 10 November 2026

The evaluation improvements are implemented and all 45 cases were attempted. The run exposes application issues, but the current judge is not reliable enough for an automatic production release gate. Treat semantic failures as review candidates until calibrated against independent human judgments.

## Scope and implementation

- Explicit critical requirements separate from average quality. A high mean cannot compensate for a failed requirement; an uncertain assessment needs review.
- Reviewed application correctness separated from grounding in retrieved documentation and citation support.
- Debugging scored for useful, ordered, discriminating investigation leads, with no unsupported root cause or implementation plan.
- Replan scored for the selected alternative, retained requirements and excluded changes.
- Service-selection precision/F1 and evidence-topic coverage added alongside recall. Keyword checks remain diagnostics.
- Essential facts, prohibited claims and acceptable omissions attached to cases.
- Three controlled variants added: loaded orders versus stored history, payment timeout versus confirmed decline, and command versus Portal recovery. These new references are marked `proposed_variant`, not user-approved.
- Ten controlled judge-calibration fixtures and a reusable calibration runner added. Fixtures are agent-authored, not independent human validation.
- Answers persisted before scoring, bounded parallel evaluation, human-review CSV, and one recorded correction attempt for malformed judge output.
- Reference preflight now checks recorded code-verification hashes as well as document hashes.

No agent, retrieval, relationship catalog or index-manifest changes were made in this evaluation task. Their hashes match the task-start snapshot. Existing Replan UI/API changes from the preceding task were preserved.

## Run results

Dataset: 24 Ask and 21 Plan-mode cases. Original 42 references were reviewed previously; three additional variants await review. One application attempt per case; evaluator-only retries did not regenerate answers.

| Result | Count |
|---|---:|
| Application attempts | 45 |
| Evaluable application responses | 40 |
| Execution failures | 5 |
| Valid semantic assessments after scoring retries | 29 |
| Met critical requirements | 18 |
| Failed one or more critical requirements | 11 |
| Not assessed: remaining judge errors | 11 |
| Not assessed: execution failures | 5 |

The initial scoring pass had 20 valid judgments and 20 malformed judgments, plus five skipped execution failures. All 20 malformed judgments received a separately recorded scoring retry; nine recovered. Invalid assessments are excluded from averages, never counted as passes or zero-quality answers. The stricter quotation/schema validation deliberately rejects fabricated supporting quotations.

All 45 runs were uploaded to [the LangSmith experiment](https://smith.langchain.com/o/7ca977ce-d907-4402-9fdb-1c997438986a/projects/p/0a6c3282-dc76-4294-b45a-8e09f07753e7).

### Execution failures

- `outbox` and `plan-notification-replay`: invalid generated citations.
- `plan-incompatible-tracking-requirements`, `debug-missing-confirmation-email`, and `debug-confirmed-decline-stock`: application error responses.

These failures were retained rather than replaced with favorable regeneration attempts.

### Answer-quality findings and judge limitations

Review candidates include overly technical Ask responses; notification-failure handling; an example stock quantity in a live-stock question; incomplete clarification; and plans missing required scope, prerequisites or service responsibilities. The readiness request received clarification instead of the requested plan.

Do not interpret every correctness flag as a verified code contradiction. For example, the judge called Portal browser-storage/idempotency details invented because the short reference did not enumerate them. Those mechanisms exist in `commercelens-customer-portal/src/main.tsx`. Their technical depth can violate the requested answer style without making the mechanism factually false. This is a concrete false-positive risk in the current judge.

The three contrast pairs are present, but this run did not produce valid judgments for both members of any pair. The confirmed-decline variant failed execution; other pair members encountered malformed judge output. Their automated comparison remains inconclusive; inspect saved answers or rerun after improving judge reliability.

## Calibration

Configured judge/generator: `Qwen/Qwen3-235B-A22B-Instruct-2507` through Nebius.

The final controlled calibration matched all expected checks for **7 of 10 fixtures**. Two Replan fixtures still produced invalid quotations after the bounded correction attempt. The stale-document fixture correctly passed the critical gate and identified a conflict, but incorrectly gave application correctness the same zero score as grounding. Earlier calibration attempts and disagreements are retained.

The same model performs generation and judgment. These controlled fixtures are development checks, not a statistically representative or independently labeled benchmark. Independent human calibration, a more reliable judge, repeated runs and held-out cases remain necessary. Do not tune the application to satisfy false-positive judgments.

## RAGAS and retrieval diagnostics

RAGAS completed on 10 factual responses, timed out on one (`portal-idempotency`), and was skipped on 34 cases because of behavior, plan applicability or execution failure.

| Metric | Mean | Scored cases |
|---|---:|---:|
| Faithfulness | 0.944 | 10 |
| Context precision | 0.546 | 10 |
| Context recall | 0.850 | 10 |
| Factual correctness F1 | 0.447 | 10 |
| Answer relevancy | 0.891 | 10 |
| Service precision | 0.696 | 28 |
| Service recall | 0.842 | 28 |

High faithfulness does not establish correctness against code or coverage of the user's requested answer. Retrieval precision indicates room to reduce irrelevant evidence, but these scores are estimates with limited coverage. v3 rubric scores are not directly comparable to the preceding v2 averages; the application was unchanged and generation remains variable.

## Verification and artifacts

All 122 local tests passed. A further focused evaluation test run covers the final report-persistence adjustment. The combined evidence preflight validated 28 distinct document/code files with no hash mismatches.

Local artifacts under `evals/results/live-v3-20261110/`:

- `runs.jsonl` and `summary.json`: untouched first-pass records and upload result.
- `generation-*.json`: saved application answers before evaluation.
- `judge-retries.jsonl`: evaluator-only retries, including original judge errors.
- `runs-with-scoring-retries.jsonl` and `summary-with-scoring-retries.json`: explicit combined view.
- `human_review_with_retries.csv`: blank human verdict/comment fields; no invented human approvals.
- `evaluation-manifest.json`: model, test count and evidence snapshot.
- `scoring-retries-langsmith.json`: outcome of supplementary feedback upload.

Calibration artifacts: `evals/results/v3-calibration-bounded-20261110/`. Previous calibration directories are retained. See `docs/RAG_RUNBOOK.md` for repeatable commands and interpretation. Changes have not been committed or pushed in this task.
