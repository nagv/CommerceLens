# Assistant

> God node · 43 connections · `commercelens_ai/engine.py`

**Community:** [Community 0](Community_0.md)

## Connections by Relation

### calls
- .response() `EXTRACTED`
- make_assistant() `EXTRACTED`
- .setUp() `EXTRACTED`
- .test_ask_returns_only_cited_evidence() `EXTRACTED`
- .test_budget_stops_retrieval_and_returns_explicit_status() `EXTRACTED`
- .test_failure_reports_type_and_stage_without_secret() `EXTRACTED`
- .test_global_plan_above_service_cap_keeps_partial_answer_with_warning() `EXTRACTED`
- .test_global_plan_does_not_exhaust_default_budget() `EXTRACTED`
- .test_global_question_includes_each_service_summary() `EXTRACTED`
- .test_invalid_input_never_reaches_model() `EXTRACTED`
- .test_long_master_chunks_do_not_crowd_out_service_evidence() `EXTRACTED`
- .test_missing_citation_is_not_grounded_success() `EXTRACTED`
- .test_obvious_help_needs_no_retrieval_or_citations() `EXTRACTED`
- .test_plan_expands_impacts_and_requests_high_level_sections() `EXTRACTED`
- .test_rejects_invented_citations() `EXTRACTED`
- .test_retrieved_ids_and_usage_are_reported() `EXTRACTED`
- .test_routes_endpoints_and_status_questions_retrieve_details() `EXTRACTED`
- .test_service_limit_is_visible_in_answer() `EXTRACTED`
- .test_short_model_citations_normalize_to_canonical_ids() `EXTRACTED`
- .test_timeout_agreement_question_expands_to_connected_service() `EXTRACTED`
- *…and 8 more `calls` connection(s) not listed (lowest-degree first to go)*

### contains
- engine.py `EXTRACTED`

### imports
- cli.py `EXTRACTED`
- test_ai_behaviors.py `EXTRACTED`
- test_ai_engine.py `EXTRACTED`
- test_ai_replan.py `EXTRACTED`
- commercelens_ai/server.py `EXTRACTED`

### method
- .run() `EXTRACTED`
- .validate_replan() `EXTRACTED`
- .replan() `EXTRACTED`
- .__init__() `EXTRACTED`

### uses
- [AssistantTests](AssistantTests.md) `INFERRED`
- [BehaviorTests](BehaviorTests.md) `INFERRED`
- create_server() `INFERRED`
- ServerTests `INFERRED`
- ReplanTests `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*