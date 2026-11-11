# Graph Report - CommerceLens  (2026-11-11)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 534 nodes · 1109 edges · 28 communities (21 shown, 7 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 36 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0a506696`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24

## God Nodes (most connected - your core abstractions)
1. `Assistant` - 43 edges
2. `run_evaluation()` - 26 edges
3. `main()` - 22 edges
4. `Model` - 21 edges
5. `AssistantTests` - 20 edges
6. `Retriever` - 20 edges
7. `EvaluationTests` - 20 edges
8. `BehaviorTests` - 19 edges
9. `build_relationships()` - 18 edges
10. `build_corpus()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `main()` --uses--> `Settings`  [INFERRED]
  evals/run_calibration.py → commercelens_ai/config.py
- `BehaviorTests` --uses--> `Assistant`  [INFERRED]
  tests/test_ai_behaviors.py → commercelens_ai/engine.py
- `AssistantTests` --uses--> `Assistant`  [INFERRED]
  tests/test_ai_engine.py → commercelens_ai/engine.py
- `ServerTests` --uses--> `Assistant`  [INFERRED]
  tests/test_ai_engine.py → commercelens_ai/engine.py
- `ReplanTests` --uses--> `Assistant`  [INFERRED]
  tests/test_ai_replan.py → commercelens_ai/engine.py

## Import Cycles
- None detected.

## Communities (28 total, 7 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (11): Assistant, call_tool(), complete(), retrieve(), _BudgetExceeded, BehaviorTests, AssistantTests, Model (+3 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (14): _coverage(), deterministic_checks(), _efficiency_metrics(), _judge(), _number(), _ragas(), _reference_snapshot(), run_evaluation() (+6 more)

### Community 2 - "Community 2"
Cohesion: 0.09
Nodes (20): atomic_write(), entrypoint(), ingest_lock(), main(), make_assistant(), make_retriever(), prepare_knowledge(), _body() (+12 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (11): Settings, channel(), get(), _Client, _NoRedirect, OpenAICompatibleEmbeddings, OpenAICompatibleModel, ProviderError (+3 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (42): inventory-db, inventory-service, mock-providers, notifications-db, orders-db, payment-service, rabbitmq, shipping-service (+34 more)

### Community 5 - "Community 5"
Cohesion: 0.10
Nodes (22): dimensions_for(), judge_contract(), _validate_contract(), judge_plan(), agreement(), main(), grade(), capture() (+14 more)

### Community 6 - "Community 6"
Cohesion: 0.10
Nodes (6): _dict(), _NoRedirect, PineconeHTTPIndex, PineconeRetriever, FakeIndex, PineconeTests

### Community 7 - "Community 7"
Cohesion: 0.13
Nodes (7): Handler, Store, checkout(), main(), request(), wait_notification(), wait_ready()

### Community 8 - "Community 8"
Cohesion: 0.18
Nodes (6): ensure_index(), request(), _http_error(), _NoRedirect, ProvisionTests, Reply

### Community 9 - "Community 9"
Cohesion: 0.11
Nodes (17): application, id, name, repository, repository_ref, pipeline, graphify_command, openwiki_command (+9 more)

### Community 10 - "Community 10"
Cohesion: 0.20
Nodes (7): definitions, root, central, drafts, existing, nested, {roots}

### Community 12 - "Community 12"
Cohesion: 0.29
Nodes (6): create_server(), do_GET(), do_POST(), send(), trusted_host(), serve()

### Community 13 - "Community 13"
Cohesion: 0.18
Nodes (11): PAYMENT_PROVIDER_URL, PROVIDER_TIMEOUT_SECONDS, SHIPPING_PROVIDER_URL, build, depends_on, environment, payment-service, shipping-service (+3 more)

### Community 14 - "Community 14"
Cohesion: 0.31
Nodes (9): conversation, form, node(), question, renderAnswer(), renderInline(), sendRequest(), status (+1 more)

### Community 15 - "Community 15"
Cohesion: 0.20
Nodes (9): build, depends_on, ports, build, volumes, name, services, customer-portal (+1 more)

### Community 18 - "Community 18"
Cohesion: 0.33
Nodes (9): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, environment, image, volumes, environment, environment (+1 more)

### Community 19 - "Community 19"
Cohesion: 0.57
Nodes (8): interval, retries, test, timeout, healthcheck, healthcheck, healthcheck, healthcheck

### Community 20 - "Community 20"
Cohesion: 0.29
Nodes (7): RABBITMQ_DEFAULT_PASS, RABBITMQ_DEFAULT_USER, environment, image, ports, volumes, rabbitmq

### Community 22 - "Community 22"
Cohesion: 0.33
Nodes (6): volumes, inventory-data, notifications-data, orders-data, provider-data, rabbit-data

### Community 23 - "Community 23"
Cohesion: 0.67
Nodes (3): image, volumes, notifications-db

### Community 24 - "Community 24"
Cohesion: 0.67
Nodes (3): image, volumes, orders-db

## Knowledge Gaps
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Assistant` connect `Community 0` to `Community 1`, `Community 2`, `Community 12`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `Assistant` (e.g. with `create_server()` and `BehaviorTests`) actually correct?**
  _`Assistant` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06180733162830349 - nodes in this community are weakly interconnected._
- **Why does `run_evaluation()` connect `Community 1` to `Community 0`, `Community 2`, `Community 11`, `Community 5`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `main()` (e.g. with `Settings` and `.embed()`) actually correct?**
  _`main()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.08123904149620105 - nodes in this community are weakly interconnected._
- **Why does `main()` connect `Community 2` to `Community 1`, `Community 3`, `Community 5`, `Community 8`, `Community 12`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._