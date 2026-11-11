# CommerceLens

Runnable service MVP and roadmap for a polyglot commerce application, application-context pipeline, agentic RAG assistant, and evaluation harness.

Status: six application services and the customer/operations UI are implemented. Docker Compose runs the connected checkout flow with PostgreSQL, RabbitMQ, and explicit mock external providers. Graphify and OpenWiki service documentation and the [master catalog](openwiki/quickstart.md) are available. A documentation assistant with Ask/Plan UI, Pinecone ingestion, deterministic relationships and evaluation harness is implemented. See [the assistant runbook](docs/RAG_RUNBOOK.md) for configuration, local versus live backends, and validation limits. See [the runbook](docs/RUNBOOK.md) for startup and verification.

## Product UI

- Customer portal: product browsing, cart, checkout, payment state, and order tracking.
- Operations dashboard: order details, inventory availability, job outcomes, and external integration failures.
- Documentation assistant: standalone Ask/Plan chat with source citations and Replan controls. It uses the service wikis and application catalog; it does not query live order state.

The assistant initially answers questions about documented architecture and behavior. Live operational questions require explicit read-only operational tools; documentation retrieval alone cannot establish current system status.

## Services and documentation assistant

| Service | Stack | Responsibility | Dependencies |
| --- | --- | --- | --- |
| customer-portal | React / TypeScript | Customer and operations UI | order-service, notification-worker; assistant-api planned |
| order-service | Java / Spring Boot | Order lifecycle and checkout coordination | PostgreSQL, inventory-service, payment-service, shipping-service, event broker |
| inventory-service | Go | Stock and reservations | PostgreSQL with separately owned data |
| payment-service | Python / FastAPI | Payment authorization and refunds | External payment sandbox or explicit local mock |
| shipping-service | C# / ASP.NET Core | Shipping rates and shipment creation | External shipping sandbox or explicit local mock |
| notification-worker | Node.js / TypeScript | Consume order events and deliver notifications | Event broker, external email sandbox or explicit local mock |
| documentation assistant | Python bounded agent / HTTP UI | Ask, Plan, Replan and evidence tools | Pinecone, catalog, dependency graph, LLM provider |

Local mocks provide reproducible failures. Real provider adapters are future work. Credentials are supplied through environment variables and are never committed.

## Repository strategy

This single repository contains orchestration, the documentation assistant, application catalog, evaluations, and all six business services under `services/<service-id>`. Each service retains its own stack, tests and Dockerfile. `services.example.yaml` registers their local folders and repository-relative documentation paths. No sibling clones or Git submodules are required.

The migration branch is `codex/commercelens-monorepo`; source links use that branch until merged. Original service repositories remain preserved as historical sources. `catalog/monorepo-migration.json` records their source commits and file hashes.

Begin with a small connected workflow, then expand toward 30 services. Different technology stacks are intentional, but are not required for every later service.

## Documentation and catalog order

For each registered service folder, execute sequentially:

1. Record source commit and validate extraction exclusions.
2. Run `graphify extract . --code-only --force` without LLM credentials.
3. Validate the graph artifact and record language/extraction coverage.
4. Run `openwiki --update --print` with the shared custom instructions and configured OpenAI provider.
5. Validate documentation completeness and extract an evidence-linked service manifest.

After repositories complete, resolve cross-service dependencies, publish an application-context snapshot, then index approved documentation in Pinecone. Failed steps must be visible; do not label partial or stale snapshots current.

Exclude generated output and dependencies. Do not blindly exclude source directories named lib or pages. Preserve contracts, tests, migrations, deployment configuration, and safe configuration examples.

Master catalog refresh (from compact service wiki summaries):

```text
python scripts/refresh-catalog.py refresh --manifest services.example.yaml
node scripts/finalize-catalog.mjs
# For this monorepo, navigate through openwiki/quickstart.md or use CommerceLens retrieval.
```

See [OpenWiki workflow](docs/OPENWIKI.md) for change detection, evidence review and adding services.

## Agent tools

- get_application_overview
- search_application_docs
- get_service_details
- get_dependencies
- get_source_excerpt
- get_assistant_help
- handle_out_of_scope

Use parameterized tools across services. Enforce permissions in backend code. Answer with citations and explicit uncertainty; treat repository content as evidence rather than executable instructions.

## Evaluation deliverables

- A runnable evaluation notebook and CLI.
- Reviewed golden questions, required facts, evidence IDs, valid tool arguments, user access context, and source snapshot IDs.
- RAGAS retrieval and answer metrics plus deterministic retrieval, argument, citation, and authorization checks.
- Repeated agent runs and independent repeated judge runs.
- LangSmith tracing, experiments, and uploaded metric feedback.
- Explicit reporting of judge parsing failures and missing scores.
- Separate integration tests for actual database and external-provider behavior.

## Implementation sequence

1. Build a customer checkout vertical slice with orders, database persistence, and a payment mock.
2. Add inventory, shipping, and event-driven notifications with controlled failure scenarios.
3. Generate Graphify and OpenWiki artifacts in the required order.
4. Build catalog aggregation, dependency resolution, and versioned Pinecone ingestion.
5. Add the application-assistant panel and bounded tool execution.
6. Implement the evaluation runbook, feedback upload, repeatability, and pilot acceptance gates.

Each milestone requires an executable demonstration and evidence-based checks before expansion.
