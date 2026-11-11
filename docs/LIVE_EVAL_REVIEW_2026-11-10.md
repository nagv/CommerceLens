# CommerceLens live evaluation and Replan verification — 2026-11-10

## Delivered behavior

- Replan controls appear below successful implementation plans. The operator enters the selected alternative and optional constraints.
- POST /api/replan and Assistant.replan retain the original request and prior proposal, validate bounded inputs, and retrieve fresh documentation.
- Both Replan golden cases now use the structured operation shared with the API, not a concatenated-question approximation.
- Debugging requests use investigation leads only. The evaluator applies behavioral criteria rather than implementation-plan dimensions.
- RAGAS now uses bounded metric concurrency and retries (120-second task timeout, one attempt, two metric workers), avoiding its default ten-attempt retry behavior.
- Browser verification: generated an email-recovery plan, submitted the command alternative excluding Portal/Order changes, observed one provider failure with inputs preserved, retried and received a revised plan respecting those scope constraints. A further Replan action appeared below the revision.
- Browser UI is available at http://127.0.0.1:8091 while the local server is running. Context is browser-memory only; reloading discards the conversation. No persistent user chat history was added.

## Verification

114 local tests passed, including API validation, structured Replan routing, fresh retrieval and behavioral evaluator tests. JavaScript syntax and git whitespace checks passed. Reference hashes validated for the entire 42-case dataset.

## Live baseline

Pinecone retrieval, configured Nebius Qwen generation/judging, and RAGAS were used. One generation per case, four independent workers. This is a baseline, not a production reliability estimate or a variability study.

| Outcome | Count |
|---|---:|
| Approved cases attempted | 42 |
| Valid responses | 37 |
| Execution/validation failures | 5 |
| Successful semantic judge assessments | 37 |
| Applicable RAGAS assessments completed | 10 |

The other 32 RAGAS entries are skipped because the case/response is behavioral or a proposed plan, or generation failed. They are not scored as perfect or averaged as zero.

Five evaluator connection failures were rescored against unchanged saved answers. The portal-capabilities assessment stalled in default RAGAS retries; its original successful response was recovered from its LangSmith trace and scored with bounded retries. No replacement answer was generated for that recovery. Original evaluator errors and provenance are retained in the output files.

## Scores and coverage

| Metric | Mean | Scored runs |
|---|---:|---:|
| Semantic correctness (Ask/behavioral responses) | 0.894 | 26 |
| Behavior appropriateness | 0.910 | 26 |
| Implementation-plan quality | 0.608 | 11 |
| RAGAS faithfulness | 0.918 | 10 |
| RAGAS answer relevance | 0.880 | 10 |
| RAGAS context recall | 0.933 | 10 |
| RAGAS context precision | 0.539 | 10 |
| RAGAS factual correctness (F1) | 0.401 | 10 |

These metrics have different scopes. The gap between semantic correctness and RAGAS factual correctness needs human review and judge calibration, not selective reporting. No agreed pass/fail threshold exists. Both Replan cases received 1.0 from the semantic judge; those are model judgments, not guarantees. The browser answer still contained excessive technical details, and the judge can over-credit alternatives and safety claims.

## Failures and follow-up priorities

| Case | Initial result | Separate retry |
|---|---|---|
| Reliable event delivery (outbox) | Invalid citations: grouped source tokens such as S1, S7 were rejected | Valid response |
| Application responsibilities | Model/provider error | Valid response |
| Shipment tracking plan | Model-response validation ValueError | Valid response |
| Incompatible tracking requirements | Model-response validation ValueError | Same failure |
| Missing confirmation email investigation | Model-response validation ValueError | Same failure |

The five-case retry experiment is separate: 3 valid responses and 2 failures. Original failures remain part of the baseline; successful retries do not replace them or imply all cases passed.

Additional content findings:

- The live-stock question failed to acknowledge unavailable live information (semantic correctness and behavior scores 0).
- The loaded-order filter plan expanded scope into backend changes (plan quality 0).
- The readiness plan asked for clarification instead of producing the expected plan (plan quality 0).
- Slow-checkout investigation gave insufficient leads (correctness 0.2, completeness 0.3).
- Destination-based shipping missed important coverage and alternatives (plan quality 0.4375).
- Payment-timeout debugging correctly challenged the premise and supplied investigation leads (correctness 1.0, completeness 0.85).

Priorities are model-response/citation formatting reliability, correct unknown/clarification behavior, preserving requested service scope, high-level plan depth and alternatives, and human calibration of the judges. These issues were measured, not silently fixed or removed from the test set. No OpenWiki, catalog or Pinecone reindexing was performed.

## Artifacts

- evals/golden.jsonl: approved 24 Ask + 18 Plan-mode cases.
- evals/results/live-complete-parallel-20261110/summary.json: aggregate scores and LangSmith identifiers.
- runs-baseline.jsonl: original generation outcomes and initial evaluator results (with explicitly documented portal recovery).
- runs-rescored.jsonl: same generated answers with failed evaluator calls rescored.
- scoring-retries.jsonl and recovered-portal-trace.json: retry/provenance audit.
- evals/results/live-generation-retries-20261110/: separate five-case generation retry experiment.
- evals/results/live-complete-20261110/: interrupted initial sequential attempt, not the full baseline.

Raw outputs are local and git-ignored. Source changes and reviewed cases have not been committed or pushed in this task.

## LangSmith

- [Complete 42-case experiment](https://smith.langchain.com/o/7ca977ce-d907-4402-9fdb-1c997438986a/projects/p/9803d275-4d50-4818-b459-2425f8120de3)
- [Separate five-case generation retry experiment](https://smith.langchain.com/o/7ca977ce-d907-4402-9fdb-1c997438986a/projects/p/f55e2bcc-1a9c-43a0-9499-111289c972c7)
- [Golden dataset snapshot](https://smith.langchain.com/o/7ca977ce-d907-4402-9fdb-1c997438986a/datasets/d8724115-40bc-4da5-8b7d-cbf76bce069d)
