<!-- Snapshot of the Google Docs submission report. Edit the Google Doc for collaborative review; refresh this snapshot explicitly. -->

Source: [Editable Google Docs report](https://docs.google.com/document/d/1ux1LwuwI7vnoIDpm0Al7Hu3mF1pXlyC0xSnSyrH_XhY/edit)

# CommerceLens: Week 4 Agent Evaluation Report

Own-use-case track | Evaluation snapshot: November 11, 2026

Video: add the Loom link here before submission.

## Executive summary

CommerceLens demonstrates a complete evaluation cycle for an application-documentation assistant: reviewed references, automated scoring, preserved baselines, targeted changes, repeated live runs, and analysis of regressions. Execution reliability improved, while answer quality remains below a proposed release bar. The project is suitable for demonstrating evaluation practice; these results do not establish production readiness.

The latest experiment completed all 90 application runs. It produced 52 critical passes, 36 quality failures and two unassessed judge errors. The previous experiment produced 51 passes from the same 45 questions run twice. This small difference does not demonstrate a meaningful answer-quality improvement. The report retains unsuccessful changes, evaluator disagreements and latency costs.

## Use case and application

Target users are engineers, technical leads and people onboarding to an application. They need to understand service responsibilities and dependencies, ask high-level questions, and plan changes without reading every repository. Ask should explain documented behavior with citations. Plan should identify affected services, describe high-level changes, order implementation, cover the requirement, compare alternatives and justify the recommendation. Replan should honor a selected alternative and revised constraints. Debugging requests should receive investigation leads, not an invented root cause or implementation plan.

The demo is a six-service commerce application: Customer Portal, Order Service, Inventory Service, Payment Service, Shipping Service and Notification Worker. It includes database and event-broker dependencies and explicit mock payment, shipping and email providers. The services use different technology stacks and now live in one monorepo. Real provider integrations and deployment at 30-service scale are outside the demonstrated scope.

Graphify code extraction and service OpenWiki documentation feed compact service summaries and an application catalog. The assistant retrieves documented evidence from Pinecone and reads structured service relationships. The preserved corpus contains 452 chunks, with 14 relationship-graph nodes and 13 edges. The assistant does not access live business data or inspect source code while answering. Code was used by reviewers to verify references.

## Evaluation framework and pass bars

Evaluation one-liner: measure successful execution, critical requirement satisfaction, appropriate response behavior, p95 application latency and logical model-call usage on CommerceLens Ask/Plan/Replan, using 45 reviewed cases, code checks, a calibrated LLM judge and applicable RAGAS metrics. Compare frozen baseline and subsequent numbered experiments, retaining failures and missing scores.

The following release targets are proposed retrospectively for this report. They were not preregistered and did not change historical scores: execution success at least 99%; at least 85% of scheduled cases meeting all critical requirements; behavior match at least 90%; p95 latency at most 20 seconds for Ask and 60 seconds for Plan; no more than three logical application model calls per request. These targets describe future acceptance, not achieved production guarantees.

Execution success is checked in code and distinguishes provider, schema and citation failures from valid unknown/clarification responses. Critical requirements are assessed against approved references, verified current facts and case-specific constraints; passing requires every applicable critical requirement. Behavior checks compare answer, clarification, unknown, uncertainty or redirect with the expected response. Latency uses application timings, excluding judge and RAGAS scoring time. Model calls and reported tokens are cost proxies, not complete billing records.

The semantic judge separates application correctness, documentation grounding, citation support, appropriate detail and case-specific requirements. Plans are also assessed for strategy, service impacts, implementation order, requirement coverage, alternatives and rationale. Proposed designs can differ from the reference if they satisfy the requirement and constraints. Lexical checks remain diagnostics rather than proof of correctness.

RAGAS evaluates applicable factual Ask responses using faithfulness, answer relevance, context precision/recall and factual correctness. It is intentionally skipped for proposed plans and behavioral responses where those factual-Q&A metrics would be misleading. Missing or failed scores are reported separately and excluded from metric averages. The generator and judge use the same configured Qwen model through Nebius, which introduces correlated-error risk.

## Golden dataset and review

The frozen dataset contains 45 cases: 24 Ask and 21 Plan-mode cases. Ask includes 12 factual cases, three unavailable-live-information cases, three insufficient-evidence cases, two irrelevant requests and four clarification cases. Plan-mode coverage includes single-service and cross-service changes, application-wide concerns, external dependencies, three Replan cases, three explicitly labeled debugging cases, and ambiguous or infeasible requests.

Questions and expected responses were developed around the demo application and reviewed with the project owner. References were checked against service code where needed. These are curated, AI-assisted demo scenarios rather than production-log samples; the proportion originally generated by an LLM was not tracked. This limits alignment with the handout's preference for real usage and its guidance to keep purely LLM-generated cases below 20%.

The cases cover common and difficult behaviors, but have not been mapped to the recommended approximate 50% happy / 30% edge / 15% known-failure / 5% adversarial split. Irrelevant requests are covered; explicit prompt-injection and malformed-input cases are not established in this frozen set. There is no held-out test set. Future coverage additions should create a new dataset version, preserving this baseline.

Every experiment uses dataset SHA-256 2dc357b54caddca9684086ec6f7a790fc967f57649bbd37275b7bb93d29f064b. The V1 checksum manifest and all 163 saved Eval 002 files were verified unchanged. The source snapshot validation checks 28 evidence files. Two repetitions per later experiment expose variability, but do not prove statistical significance. No references were rewritten to improve the scores.

## Measured results

Eval 001 contains 45 runs. Eval 002, Eval 003 and Eval 004 each contain 90 runs, comprising two repetitions of the same 45 cases. Compare rates where denominators differ. Unassessed includes execution failures and judge errors; it is not a quality-failure label.

| Metric | Eval 001 | Eval 002 | Eval 003 | Eval 004 |
| --- | --- | --- | --- | --- |
| Runs | 45 | 90 | 90 | 90 |
| Execution OK | 30 | 88 | 90 | 90 |
| Critical passes | 15 | 51 | 51 | 52 |
| Quality failures | 10 | 34 | 39 | 36 |
| Unassessed | 20 | 5 | 0 | 2 |
| Judge errors | 5 | 3 | 0 | 2 |
| RAGAS scored | 9 | 23 | 23 | 24 |
| RAGAS errors | 1 | 0 | 1 | 0 |

Eval 004 repetition 1 passed 25/45 cases (Ask 17/24, Plan 8/21). Repetition 2 passed 27/45 (Ask 17/24, Plan 10/21). Across both repetitions, critical-pass yield rose from 51/90 (56.7%) in Eval 002 to 52/90 (57.8%), a 1.1 percentage-point change. Among successfully judged answers, the pass rate moved from 51/85 (60.0%) to 52/88 (59.1%). Improved execution exposed more assessable failures; it did not establish improved reasoning.

For Eval 002 versus Eval 004, Ask p50/p95 latency changed from 4.59/19.63 seconds to 6.16/17.36 seconds. Plan p50/p95 changed from 18.35/42.97 seconds to 32.22/91.00 seconds. p95 is the nearest-rank percentile, calculated separately across 48 Ask and 42 Plan observations. Mean logical calls were unchanged for Ask at 1.33 and rose for Plan from 1.62 to 2.19. Mean reported application tokens per run rose from approximately 6,937 to 7,117; evaluator, embedding and retry charges are not a complete part of this estimate.

Eval 004 behavior match was 65/90 (72.2%). The retrospective critical-pass, behavior and Plan latency targets were not met. Application execution reached 100%, and Ask p95 was within the proposed 20-second target. These are batch measurements on a small demo dataset, not operational service-level guarantees.

## Targeted changes and measured effects

Reliability controls: bounded retries, response repair and citation normalization targeted the original execution failures. Hypothesis: recover valid answers without accepting invalid evidence. Execution improved from 30/45 in Eval 001 to 88/90 in Eval 002 and 90/90 in Eval 004. Evaluator transport also changed between Eval 001 and Eval 002, so the broader comparison is not an application-only controlled experiment.

Focused service retrieval: semantic Plan routing, per-service queries and more evidence within the existing context budget targeted missing facts and unnecessary services. Hypothesis: improve service-scope accuracy and grounding. In the bundled candidate, Plan passes increased from 17/42 in Eval 002 to 23/42 in Eval 003, but only 18/42 passed in Eval 004. No isolated causal effect can be assigned to retrieval.

Structured Plan responses: schema-guided output and seven rendered sections targeted incomplete plans. Hypothesis: improve coverage and consistency without imposing a plan on debugging or clarification. Structure improved mechanically, but semantic failures remained. A nullable plan allows non-implementation responses and also permits a model to choose the wrong behavior. Headings alone receive no correctness credit.

Bounded answer review and rollback: an optional evidence-aware review targeted unsupported claims and lost constraints. Invalid review output preserves the draft, and review shares the three-call budget. Eval 003 Ask passes fell from 34/48 to 28/48; the enhanced Ask path was disabled by default for Eval 004, restoring 34/48. Plan mean latency rose from 19.6 to 37.6 seconds without a demonstrated aggregate quality benefit. The bundled changes were evaluated together; individual-change deltas are not available.

## Dominant failures and practical cost

The three most frequent failed critical-requirement labels in Eval 004 were truthful_current_claims (27 run-level flags), expected_response (16) and request_outcome (15). These are overlapping judge flags across 90 runs, not 58 distinct failed cases or independently verified root causes. Some rationales are questionable and require human adjudication.

Truthfulness, 27 flags: the unknown-live-stock case answered a request for current stock using a documented sample value of 100 units. Expected behavior is to acknowledge that live stock is unavailable. Practical cost is high: a user could act on invented operational data. Cost estimate is qualitative; no real customer loss or dollar estimate was measured.

Expected response, 16 flags: unknown-live-stock also illustrates a failure to return the required unknown response. Other cases mishandle uncertainty or response scope. Practical cost is medium to high: user confusion, misplaced confidence and a repeated question. The overlap with truthfulness is intentional and must not be summed as separate incidents.

Requested outcome, 15 flags: plan-portal-status-filter asked for filtering already-loaded orders but received unnecessary clarification in repetition 1. replan-provider-quotes similarly asked questions already answered by the selected alternative, losing the requirement to use provider quotes without a regional fallback. Practical cost is medium to high: wasted planning time and potentially incorrect implementation scope. The evidence supports these examples, but not a precise time-loss estimate.

Two Eval 004 judge attempts for plan-production-checkout-evidence failed validation because evidence coverage was marked without required evidence IDs. These answers remain unassessed. Eval 003 had one RAGAS timeout; Eval 004 had no RAGAS errors. The last judge calibration agreed with human labels on 8/10 fixtures. Known disagreements include incomplete-question handling and separating code correctness from documentation grounding. Calibration was not rerun for Eval 003/004.

## Trace evidence and reproducibility

LangSmith stores versioned dataset snapshots, case-level experiment runs, outputs, feedback and timing. Each experiment run is named by case ID and linked to its reference example; repetition metadata distinguishes reruns. Separate application tracing wraps the assistant's top-level run. Tool/model steps and usage are recorded inside the result trace.

Instrumentation limitation: the current wrapper does not emit separate native child spans for every model/tool call. Uploaded experiment rows do not provide a verified direct link to the separate application trace or complete prompt-version metadata on every row. This falls short of the handout's full child-run tracing requirement. The report supplies project links and case IDs rather than claiming that missing span-level evidence is present. A shared immutable dataset in LangSmith Comparison view would also simplify comparison; current uploads create separate snapshots with identical content hashes.

Reproduction uses the repository's runbook and scripts/run-quality-evaluation.py, with a new empty output directory and two repetitions. Secrets remain in local environment configuration. Eval 001 code: 4c00aa4; Eval 002: 450c07b; Eval 003: 593fa1e; Eval 004: d534241. The final application version passed 152 unit tests. Unit tests verify implementation behavior; they do not certify answer quality.

## Next steps and production monitoring proposal

First, adjudicate the disputed judge cases and repair evaluator evidence attribution without weakening criteria. Then separate retrieval sufficiency from answer reasoning: measure whether required evidence was retrieved before tuning the response prompt. Test explicit extraction of requested scope and Replan exclusions, and compare a different judge/model on held-out cases. Add real user questions and adversarial cases in a new dataset version. Instrument native child spans and attach consistent case, dataset and prompt-version identifiers.

Proposed monitoring, not currently deployed: track execution errors and tool failures hourly, alerting above 1% and 5% respectively with at least 20 observations; alert when Ask/Plan p95 exceeds 20/60 seconds over a day with at least 30 runs per mode; review a weekly human-labeled sample and investigate a critical-pass drop of more than five percentage points; investigate a greater than 25% rise in mean application token usage. Retain version and case metadata, distinguish evaluator failures from product failures, and use human review before acting on a low-confidence change plan.

## Submission materials

[Project repository and runnable application](https://github.com/nagv/CommerceLens/tree/codex/commercelens-monorepo)

[Frozen golden dataset](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/evals/baselines/v1-20261111/golden.jsonl)

[Evaluation code and prompts](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/commercelens_ai/evaluation.py)

[Judge calibration and human review](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/evals/CALIBRATION_REVIEW.md)

[Numbered experiment history and failure details](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/evals/experiment-history/eval-003-004-comparison.json)

[Eval 002 baseline comparison project](https://smith.langchain.com/o/7ca977ce-d907-4402-9fdb-1c997438986a/projects/p/20c1a80e-cb6b-4f4b-b370-eb601ea64cdd)

[Eval 003 candidate project](https://smith.langchain.com/o/7ca977ce-d907-4402-9fdb-1c997438986a/projects/p/b81679b4-08de-47dc-8434-1702526de40e)

[Eval 004 final project](https://smith.langchain.com/o/7ca977ce-d907-4402-9fdb-1c997438986a/projects/p/16dde6c6-4301-432a-b14d-7c07b63bc3c8)

[Detailed measured-results report](https://github.com/nagv/CommerceLens/blob/codex/commercelens-monorepo/docs/EVAL_003_004_RESULTS.md)

[Week 4 project requirements](https://docs.google.com/document/d/1sdxmECEBFHqFYxr4vHbpoV_r89f31N3ndrusiZI3VvQ/edit)

Video outline: show one Ask and one Plan/Replan interaction; explain the reviewed dataset and metrics; open a failure such as unknown-live-stock; compare baseline and final results; explain the failed Ask experiment and rollback; close with remaining limitations. Add the Loom link at the beginning of this report. Confirm the reviewer can access the repository and LangSmith evidence before submitting.


