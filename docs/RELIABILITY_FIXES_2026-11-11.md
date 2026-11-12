# Reliability fixes — first iteration

## Frozen baseline
See [baseline guide](../evals/BASELINE.md). Original run and 45-case golden dataset are preserved with SHA256 checksums in evals/baselines/v1-20261111. Categories: 15 application failures, 10 judged quality failures, 6 evaluator error records. Skipped assessments are not failures of answer correctness.

## Changes
- Grouped source aliases such as [S1, S3] normalize to individual citations. Every identifier is still validated; invented sources remain rejected.
- The literal input-field label [replan_context] is rendered as a label, not a documentary citation. Factual claims still require real evidence.
- Malformed JSON envelopes receive one format-repair attempt within the existing model-call budget. Repair failure remains an error, with response_schema diagnostics.
- Main and repair prompts explicitly distinguish Plan request mode from allowed response behaviors. A live diagnostic reproduced behavior=plan before and after the original repair, explaining a remaining failure.
- Provider failures now expose safe categories, HTTP status and attempt count. Transient connection/timeouts and selected retryable HTTP errors receive at most one retry; authentication errors do not. Request bodies, credentials and raw provider errors are not logged. Retrying increases potential latency/cost and does not guarantee availability.

## Verification
132 regression tests passed, including eight new reliability tests. Baseline checksums and configured-secret scan passed. Golden answers and judge/rubric code were not changed.

| Targeted run | Execution result | Scope |
|---|---|---|
| reliability-failed15-20261111 | 9/15 accepted; 6 schema failures | Initial citation/retry/repair changes |
| reliability-schema-followup-20261111 | 6/6 accepted; 0 failures | Six remaining cases after mode/behavior prompt correction |

These are execution-only targeted checks: semantic judge and RAGAS were intentionally not run. They do not prove the answers are correct or that quality scores improved. Do not combine them into a claimed single 15/15 run: application versions differ, and the latest version has not yet run the entire frozen dataset.

## Remaining evaluation work
Run all 45 frozen cases on the final fix version with the unchanged judge/RAGAS settings, then repeat to measure variability. Review the 10 original quality failures and 6 evaluator errors separately. No claim is made that those issues are fixed by this reliability iteration. Baseline and targeted-run failures remain preserved.
