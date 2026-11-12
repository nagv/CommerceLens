# Quality improvement experiments: Eval 003 and Eval 004

The new runs completed, but they do not demonstrate a substantial overall answer-quality improvement. Eval 004 produced 52 critical passes, 36 quality failures and 2 unassessed judge errors across 90 runs. All 90 application executions succeeded. The previous Eval 002 produced 51 passes, 34 quality failures and 5 unassessed cases. More successful execution is useful, but it is not the same as better answers.

## Changes and boundaries

- Plan output supports seven structured sections: strategy, service changes, implementation order, requirement coverage, alternatives, recommendation and validation. The host renders these into Markdown.
- Plan service selection uses semantic routing and focused per-service queries, with more evidence per selected service inside the existing context limit.
- One bounded editorial review checks the request and retrieved evidence. Invalid review output or invalid citations preserve the original draft. Routing, generation, repair and review share the existing three-call application budget.
- Provider JSON-schema output is requested for the enhanced path. [Nebius documents this interface](https://docs.tokenfactory.nebius.com/ai-models-inference/json). A schema constrains structure, not correctness. A nullable plan accommodates non-implementation responses; the model can still choose the wrong response behavior or omit a needed plan.
- Eval 003 enabled the enhanced path for Ask and Plan. Ask regressed, so Eval 004 retains the previous Ask path and applies enhancements to Plan. The experimental Ask path is opt-in (`enhance_ask=True`), not the default.

The model, golden dataset, judge implementation and numerical gates were unchanged between Eval 002 and these runs. Service code, service wikis, master documentation and the Pinecone corpus were unchanged. No expected answers were edited to improve scores. All 152 unit tests passed for the final application version (`d534241`).

## Results

Each numbered experiment below contains the same 45 cases executed twice: 24 Ask and 21 Plan cases per repetition. Counts are aggregated across repetitions unless stated otherwise.

| Measure | Eval 002 (previous) | Eval 003 (candidate) | Eval 004 (current) |
|---|---:|---:|---:|
| Accepted application executions | 88/90 | 90/90 | 90/90 |
| Critical passes | 51 | 51 | 52 |
| Critical failures | 34 | 39 | 36 |
| Unassessed | 5 | 0 | 2 |
| Ask passes | 34/48 | 28/48 | 34/48 |
| Plan passes | 17/42 | 23/42 | 18/42 |
| Judge errors | 3 | 0 | 2 |
| RAGAS completed | 23 | 23 | 24 |
| RAGAS errors | 0 | 1 | 0 |
| RAGAS intentionally skipped | 67 | 66 | 66 |

Eval 004 repetition 1: 25 passes, 19 failures, 1 unassessed; Ask 17/24, Plan 8/21. Repetition 2: 27 passes, 17 failures, 1 unassessed; Ask 17/24, Plan 10/21.

Conditional pass rates among successfully judged answers are 51/85 (60.0%) for Eval 002, 51/90 (56.7%) for Eval 003 and 52/88 (59.1%) for Eval 004. The one additional aggregate pass in Eval 004 is not evidence of a meaningful quality gain. The apparent Plan gain in Eval 003 was not consistently reproduced in Eval 004, even though the Plan code path was retained. Model and judge variability remain material; two repetitions are diagnostic, not statistical proof.

Mean application latency increased: Ask averaged 5.9 seconds in Eval 002 and 7.0 seconds in Eval 004; Plan averaged 19.6 seconds and 37.6 seconds respectively. These are application timings, not total evaluation duration or billing estimates. The extra Plan review has a real latency cost without a demonstrated aggregate quality benefit in this experiment.

## Remaining failures and their meaning

Failure categories are retained separately in `evals/experiment-history/eval-003-004-comparison.json`, including case IDs, repetitions and failed requirements. Automated findings require human review; they are not verified facts about the code.

- **Application execution:** none in Eval 003 or Eval 004.
- **Answer quality:** unsupported current-state claims, excessive or incorrect service scope, incomplete requested outcomes, lost Replan constraints, and weak investigation leads remain. Better output formatting alone does not resolve these.
- **Evaluator errors:** `plan-production-checkout-evidence` failed judge validation in both Eval 004 repetitions (`Coverage requires evidence`). The judge marked evidence coverage without the required evidence IDs after two scoring attempts. These two answers remain unassessed; no score was fabricated and validation was not relaxed.
- **RAGAS errors:** Eval 003 had one timeout for `notification-delivery`, repetition 2. Eval 004 had none. RAGAS is intentionally skipped for response types to which its factual-Q&A metrics do not apply.
- **Calibration:** the last calibration remains 8/10; it was not rerun or improved by these application changes. Known judge reasoning issues remain, including the earlier incorrect claim that notification dead-letter handling does not exist. Original automated scores are retained.

These cases failed quality gates in both Eval 004 repetitions:

| Area | Cases |
|---|---|
| Ask | `outbox`, `notification-delivery`, `notification-gaps`, `shipping-contract`, `unknown-live-stock` |
| Implementation scope and facts | `plan-variable-shipping`, `plan-portal-status-filter`, `plan-service-readiness`, `plan-checkout-observability`, `plan-external-payment-provider` |
| Constraints and Replan | `plan-incompatible-tracking-requirements`, `replan-provider-quotes`, `replan-notification-portal` |
| Investigation | `debug-confirmed-decline-stock` |

The next quality work should target evidence selection and explicit request constraints, and separately calibrate the judge on the disputed cases. A retrieval-only check of required evidence can distinguish missing evidence from reasoning errors. Any model or retrieval change needs a new numbered experiment and the same frozen cases; do not rewrite approved answers or silently treat absent documentation as proof of absent code behavior.

## Preserved results and trace links

The V1 baseline manifest and all 163 Eval 002 file hashes were verified unchanged after these runs. Eval 003 evaluates commit `593fa1e`; Eval 004 evaluates `d534241`. Provenance and source hashes are committed under `evals/experiment-history/`. Local raw results remain in their separate `evals/results/eval-003/` and `evals/results/eval-004/` directories.

- [Eval 003 in LangSmith — 90 uploaded runs](https://smith.langchain.com/o/7ca977ce-d907-4402-9fdb-1c997438986a/projects/p/b81679b4-08de-47dc-8434-1702526de40e)
- [Eval 004 in LangSmith — 90 uploaded runs](https://smith.langchain.com/o/7ca977ce-d907-4402-9fdb-1c997438986a/projects/p/16dde6c6-4301-432a-b14d-7c07b63bc3c8)

The projects are named `commercelens-eval-003-20261111` and `commercelens-eval-004-20261111`. Full experiment numbering is in `evals/EXPERIMENTS.md`. Pilots and earlier judge recovery attempts are not merged into these totals.
