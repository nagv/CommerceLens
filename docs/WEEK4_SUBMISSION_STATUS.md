# Week 4 submission checkpoint

Decision recorded November 11, 2026: submit the existing evaluation work. Additional tracing implementation is deferred. The tracing follow-up only inspected code; it made no implementation changes and started no new live evaluation.

## Submission materials

- [Editable submission report](https://docs.google.com/document/d/1ux1LwuwI7vnoIDpm0Al7Hu3mF1pXlyC0xSnSyrH_XhY/edit)
- [Repository report snapshot](WEEK4_SUBMISSION_REPORT.md)
- [Numbered experiment history](../evals/EXPERIMENTS.md)
- [Detailed evaluation comparison](EVAL_003_004_RESULTS.md)
- [Frozen 45-case golden dataset](../evals/baselines/v1-20261111/golden.jsonl)
- [Failure categories and case-level explanations](../evals/experiment-history/eval-003-004-comparison.json)

## Completed

- Six-service demo application in a monorepo, service documentation, master catalog, Pinecone retrieval, and Ask/Plan/Replan interface.
- Reviewed references, deterministic checks, semantic judge, applicable RAGAS metrics and human calibration review.
- Preserved V1 baseline and numbered subsequent experiments. Eval 003 and Eval 004 each ran the same 45 cases twice and uploaded 90 results to separate LangSmith projects.
- Targeted application changes, repeated measurements, regression analysis and documented rollback of the experimental Ask path.
- Final evaluated application version: `d534241`. Latest report snapshot commit before this checkpoint: `9b2ee46`. The final application version passed 152 unit tests.

## Latest measured outcome

Eval 004: 90/90 application executions succeeded; 52 critical passes, 36 quality failures and two unassessed judge errors. RAGAS completed on 24 applicable responses with no errors and was skipped on 66 others. Overall quality did not meaningfully improve over Eval 002's 51 critical passes. These results do not establish production readiness.

## Disclosed limitations, deferred

- Separate native LangSmith child spans for each model/tool call and consistent links from experiment rows to application traces are incomplete. Existing top-level traces and result-embedded steps remain available.
- Quality failures, two judge-validation errors and 8/10 calibration agreement remain unresolved.
- Explicit adversarial coverage, tracked question provenance, a held-out set and a mapping to the recommended scenario distribution need strengthening.
- Release targets in the report are retrospective. Failure costs are qualitative estimates. Changes were tested together, without isolated per-change causal measurements.
- Plan latency increased; production monitoring is proposed rather than deployed.

## User's final submission steps

Record the video and add its Loom link to the Google Doc. Confirm reviewer access to repository and LangSmith evidence. Submit the report, evidence and video through the course submission form. No course submission or sharing-permission changes have been performed by the assistant.
