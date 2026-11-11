# Documentation assistant verification — November 9, 2026

## Implemented and checked

- Manifest-driven documentation corpus: 452 chunks; no application source-code ingestion.
- Versioned relationship artifact: 14 nodes and 13 evidence-linked edges; queue-mediated service connections and explicit unknown targets.
- Incremental Pinecone sync/provisioning: mocked tests cover create-vs-reuse, mismatched dimensions, payload bounds, metadata filters, deletion, failed-write journal recovery and single-writer CLI lock.
- Ask/Plan CLI, loopback UI and bounded retrieval/generation with canonical citation validation.
- Golden dataset: 14 seed cases (10 factual questions, 4 high-level plans), source evidence hashes validated before live evaluation.
- Local and optional LangSmith/RAGAS evaluation workflow; notebook entry point supplied.
- Full suite: 85 tests passed in 4.550 seconds. External APIs mocked in unit tests; local HTTP tests run with loopback permission.
- Isolated dependency set passes pip check. RAGAS 0.4.3 import verified using pinned langchain-community 0.4.1 and notebook-compatible numerical package builds. Original notebook environment unchanged.

## Live checks

Nebius Qwen/Qwen3-Embedding-8B returned 4096 dimensions for a harmless probe. Nebius Qwen/Qwen3-235B-A22B-Instruct-2507 produced an application explanation and a high-level cancellation plan. The local browser UI answered a product-ownership question with numbered clickable evidence links. Live retrieval backend was explicitly local lexical search, not Pinecone.

First three-case evaluation had one withheld answer because the model abbreviated citation hashes. Short model-facing citation aliases were added; stored answers retain canonical IDs. Timeout/conflict questions now expand documented service relationships.

Follow-up experiment `commercelens-eval-96672c723719` uploaded three runs to LangSmith with zero execution failures. Dataset: `commercelens-golden-11b1e956f9-72054ac5`. Project ID: `7eb218dc-02c4-4cdb-8b04-2340dcecb00c`. Dataset ID: `b16102ed-5237-4fb9-8a68-d69bac7bd605`.

- Model judge: three valid results.
- RAGAS: two valid factual evaluations; one plan intentionally skipped.
- RAGAS mean faithfulness: 0.9706; context recall: 1.0; context precision: 0.6626.
- RAGAS mean factual correctness F1: 0.34; answer relevancy: 0.3860.

These mixed scores are retained, not treated as passing quality gates. The references are narrow and the judge/provider need calibration; the cause of each low score is not assumed. This tiny smoke run proves execution/integration, not production answer quality. Full repeated runs, broader held-out questions, human review and acceptance thresholds remain user evaluation work.

## Pinecone status

Created a separate CommerceLens project under the user's organization:
`b51c0ec7-1eec-4cfe-b86c-5a210843a0cf`.

The new project key and index host are configured in ignored CommerceLens/.env. Index `commercelens-docs` is ready: 4096-dimensional dense vectors, cosine similarity, AWS us-east-1. Namespace `commercelens-docs-v1` contains 452 vectors, confirmed through live index statistics. Existing Default-project indexes were untouched.

First ingestion upserted 452 chunks. Repeat ingestion returned zero upserts, zero deletions and 452 unchanged chunks. The local UI was restarted with the default Pinecone backend; its live chat endpoint answered the price/stock ownership question successfully, selected `inventory-service`, and completed in 6.921 seconds. Its health endpoint returned `ok`.

Live filtered search (`service=inventory-service`, `level=service`, limit 3) returned three inventory service chunks, with matching metadata.

## Live Pinecone evaluation

Three smoke cases were run twice against Pinecone: six successful executions, six valid model-judge results, four valid RAGAS factual results, and two plan runs intentionally excluded from factual RAGAS scoring. Reference evidence hashes validated. Citation validity and expected-service recall were 1.0 across all six runs.

Mean factual RAGAS scores: context recall 1.0, context precision 0.7364, faithfulness 0.7976, factual correctness F1 0.6350, answer relevancy 0.6593. Assistant latency ranged from 4.0 to 147.86 seconds (mean 42.47 seconds). These results validate the integration, not production quality or latency acceptance. The provider returned one generation where answer relevancy requested three; RAGAS proceeded with one, reducing sampling for that metric.

LangSmith experiment: `commercelens-eval-0f1b4c9a0c85`; project ID `0e2499f2-5733-4f9b-8b8a-aca7bf8c2e5e`. Dataset: `commercelens-golden-11b1e956f9-bf142730`; dataset ID `fcf3e867-f5fe-4727-a881-d0ca27da3949`. All six runs uploaded successfully. Local artifacts: `evals/results/live-smoke-pinecone/summary.json` and `runs.jsonl` (ignored by Git).

## Behavior-aware Ask update

The four evaluation gaps were addressed: expected response behaviors and semantic scoring; conditional citations; abstention separated from execution failure; meaning-based correctness alongside diagnostic keyword checks. Ask intent routing now asks for clarification or redirects unrelated requests before retrieval when no service is identified. Single-turn only; no follow-up dialogue is implemented.

Regression suite: 97 tests passed. A live five-case Pinecone/Nebius smoke experiment after the routing fix completed with zero execution failures and five expected behavior matches. LangSmith experiment `commercelens-eval-00f1c816e61a`, project `1d48b778-142e-4fe0-943c-82942f8255bd`. All five semantic judges completed. RAGAS was intentionally not requested in this smoke run; applicability/skips are unit-tested. The initial live run exposed incorrect unrelated/ambiguous routing, which motivated the pre-retrieval fix. A separate two-answer semantic calibration gave correctness 1.0 to the correct payment-timeout answer and 0.0 to its negated contradiction. These are small checks, not broad judge calibration.

The dataset contains 24 Ask cases (9 approved, 15 pending human review) and 4 unchanged Plan cases. New candidates are documented in evals/ASK_REVIEW.md. Documentation evidence hashes validate. Catalog pages and Pinecone vectors were not changed. Full 24-case repeated evaluation remains pending review. Live answers sometimes still include excessive implementation details despite high-level instructions; the model judge did not consistently penalize that, so perfect smoke judge scores are not final acceptance.

## Plan evaluation extension

Plan rubric v2 adds eight separately explained dimensions on 0–2: strategy, service impacts, service details, implementation order, requirement coverage, alternatives, recommendation rationale and grounding. plan_quality is the normalized applicable-dimension mean; it is not a release gate. Required alternatives cannot be omitted as not applicable. Critical issues are preserved, and dimension rationales are attached to LangSmith feedback. Ask evaluation behavior is unchanged.

Final regression suite: 105 tests passed. Live controlled calibration graded a detailed plan at 1.0 normalized quality, a vague outline at 0.4375, and a plan inventing existing provider capabilities at 0.0625, with grounding zero for the unsupported plan. These were constructed calibration examples, not generated user plans or broad benchmark results.

A live Pinecone-generated Plan run and its scores uploaded successfully to LangSmith experiment `commercelens-eval-47b7a8769db1` (project `8477cd66-efa8-4288-92cd-dc89b8a21205`). That experiment used the initial anchors. Regrading the same saved answer locally with final, stricter anchors produced quality 0.625: service impacts/details and requirement coverage were incomplete and alternatives scored zero. Local artifact: `evals/results/plan-strict-anchor-check.json`. The different grades illustrate judge sensitivity; human calibration remains necessary. No claim of production acceptance is made. The generated plan omitted Portal detail and meaningful alternatives; plan generation itself was not changed in this evaluator task.

All 24 Ask cases are approved. The four existing Plan cases remain pending review; the shipping case now carries verified current facts and dimension-specific acceptance criteria. The proposed 16-case Plan coverage is documented in evals/PLAN_REVIEW.md but has not yet been fully added to the executable dataset. Replan UI/API execution is not implemented. No master catalog, vectorization or Pinecone index changes were made.


## 2026-11-10: completed dataset and structured Replan

See [live evaluation review](LIVE_EVAL_REVIEW_2026-11-10.md) for the 42-case baseline, separate retries, measured failures and limitations. Replan UI/API and structured evaluator dispatch are implemented; 114 local tests passed. This supersedes earlier statements that Replan is pending.
