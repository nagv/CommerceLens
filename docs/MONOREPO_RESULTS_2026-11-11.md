# CommerceLens monorepo verification — November 11, 2026

## Migration and documentation
Six services are now in `services/<service-id>` in the CommerceLens repository. Original sibling repositories remain intact. All 72 copied service code/config files were hash-identical to their pre-migration snapshots. Service behavior, database volumes, service IDs and application boundaries were preserved.

The initial OpenWiki regeneration was unnecessary. Its partial output was archived locally; all six original service wikis and the original master prose were restored. Only repository locations/links and evidence metadata were migrated. All six compact summary contents, 45 approved golden questions/answers/rubrics, and 13 relationships were retained. The master lifecycle was finalized locally without an LLM; final metadata reports complete. Evaluation evidence validates 28 unique files and 169 references. Audit records are in catalog/documentation-location-migration.json and evals/monorepo-evidence-migration.json.

OpenWiki 0.7.2's linked-workspace feature requires independent Git roots and cannot register nested service directories. No nested Git repositories were introduced. Use master navigation and CommerceLens/Pinecone retrieval for the monorepo; older OpenWiki workspace registrations still refer to preserved original checkouts. Repository citation links target the published codex/commercelens-monorepo branch.

## Verification
- 124 Python regression tests passed after migration/review fixes.
- Six service build/test checks and connected Docker smoke checks passed, including checkout replay, compensation, concurrent requests and notification retries.
- Graphify code-only extraction completed for seven roots, with no LLM use.
- Corpus: 452 chunks, 14 relationship nodes and 13 edges.
- Pinecone: 452 records upserted and 452 obsolete IDs removed; final sync reported all 452 unchanged.
- Live Inventory-filtered retrieval returned Inventory documentation with monorepo source URLs.
- Credential-value scan found no configured secret values in the 544 candidate repository files.
- Imported service files retain their original whitespace; staged whitespace warnings were not fixed because code/wiki byte preservation was intentional.

## Live evaluation
Dataset SHA256: `2dc357b54caddca9684086ec6f7a790fc967f57649bbd37275b7bb93d29f064b`. One repetition, all 45 cases. [LangSmith experiment](https://smith.langchain.com/o/7ca977ce-d907-4402-9fdb-1c997438986a/projects/p/11e333bc-65d3-4903-8867-8ddab0883791).

| Measure | Result |
|---|---:|
| Successful application executions | 30/45 |
| Execution failures | 15/45 |
| Judge completed | 25 |
| Judge errors | 5 |
| Critical requirements met | 15 |
| Critical requirements failed | 10 |
| Not assessed | 20 |
| RAGAS completed | 9 |
| RAGAS errors | 1 |
| RAGAS not applicable / skipped | 35 |
| LangSmith uploaded runs | 45 |
| Calibration agreement | 8/10 |

Execution failures comprise 12 application error statuses and 3 invalid-citation statuses. Judge errors are output-validation errors; they are not quality passes. The RAGAS API error was on application-purpose. Calibration disagreements: replan-good had a judge error; document-conflict disagreed with the expected judgment. The calibration fixture set is not an independent blind human benchmark.

The final operational runner isolated each RAGAS call in a subprocess with a 180-second ceiling and used the existing metrics/models/rubrics. Feedback upload used four bounded workers. Earlier interrupted runs are retained separately and excluded from this report. No failures were converted to passing scores. This is a single stochastic rerun, not evidence that migration caused the observed quality difference or that the system is production-ready.

## Cases requiring investigation

| Case | Failure |
|---|---|
| notification-delivery | AssistantStatus:error |
| outbox | AssistantStatus:invalid_citations |
| plan-checkout-observability | AssistantStatus:error |
| plan-notification-attempt-limit | AssistantStatus:error |
| plan-portal-status-filter | AssistantStatus:error |
| plan-external-payment-provider | AssistantStatus:error |
| plan-shipment-tracking | AssistantStatus:error |
| plan-service-readiness | AssistantStatus:error |
| plan-incompatible-tracking-requirements | AssistantStatus:error |
| debug-missing-confirmation-email | AssistantStatus:error |
| replan-notification-command | AssistantStatus:invalid_citations |
| debug-payment-timeout-assumption | AssistantStatus:error |
| plan-historical-status-filter | AssistantStatus:error |
| replan-notification-portal | AssistantStatus:invalid_citations |
| debug-confirmed-decline-stock | AssistantStatus:error |

Detailed results and human review template: `evals/results/live-monorepo-preserved-20261111/`. Calibration: `evals/results/calibration-monorepo-20261111/`. These local result folders are ignored by Git; experiment evidence is uploaded to LangSmith.
