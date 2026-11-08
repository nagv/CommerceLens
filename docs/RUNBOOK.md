# Run CommerceLens locally

## Prerequisites

- Docker Desktop with Linux containers running.
- Git access to nagv's private CommerceLens repositories.
- PowerShell for the optional bootstrap helper; Python 3.10+ for the smoke script.

This is a local demonstration with synthetic data and mock external providers. It is not hardened for public hosting: the operations UI has no authentication, and simulation controls are intentionally exposed. No real payment, shipment, or email is sent.

## Get the repositories

Clone CommerceLens, then from its directory:

```powershell
./scripts/bootstrap.ps1
docker compose up --build -d
docker compose ps
```

Bootstrap clones missing service repositories beside CommerceLens and preserves existing checkouts. To update existing repositories, review their working trees and pull changes explicitly.

Open http://localhost:3000. Only the portal and RabbitMQ management UI are published to loopback. Internal APIs, mock providers and PostgreSQL stay on the Docker network.

The default RabbitMQ management UI is http://localhost:15672 with local-only demo credentials `commerce` / `local-demo-only`. Override local credentials through `.env` before creating volumes. Changing the environment alone does not rotate credentials in existing database volumes.

## Try the business flow

1. Add one or more products to the cart and set quantities.
2. Enter a demo customer email and postal code.
3. Select the successful checkout scenario and submit.
4. Inspect the confirmed order, tracking reference, and inventory change.
5. Refresh notifications to see asynchronous delivery.
6. Try a declined payment, payment timeout, and rejected shipment.
7. Use `fail-email@example.com` to exhaust notification retries while retaining a confirmed order.

Payment timeout is deliberately ambiguous: the mock provider records authorization before delaying its response. The order is retained for reconciliation; it must not be reported as a definite decline. Manual-review states need operator investigation in this MVP; automated reconciliation is future work.

## Verify the complete flow

```powershell
python scripts/smoke.py
python -m unittest discover -s tests -v
```

The smoke test creates demo orders and consumes a small amount of seeded stock. It checks checkout, authoritative totals, duplicate request behavior, stock compensation, notification delivery/failure, and uncertain payment outcomes. It is not safe to run against real external-provider credentials.

For service-specific tests, follow each repository README. Tests can run using Docker build test stages so Maven, Go and .NET need not be installed on the host.

## Documentation generation

Each service includes generic `openwiki/INSTRUCTIONS.md` and extraction exclusions. Generated wiki/graph artifacts are not included until the actual generators run successfully.

After configuring OpenWiki's OpenAI provider and API key, run from each repository root in this order:

```powershell
graphify extract . --code-only --force
if ($LASTEXITCODE -ne 0) { throw 'Graphify extraction failed' }
openwiki --update --print
if ($LASTEXITCODE -ne 0) { throw 'OpenWiki generation failed' }
```

Preserve source, tests, API contracts, migrations and safe config templates. `lib` and `pages` are not globally excluded because they can contain application code. Generated Graphify code structure supports documentation; it does not independently prove complete runtime service dependencies.

Application-catalog aggregation, Pinecone ingestion, the RAG chatbot, and the RAGAS evaluation runbook are subsequent milestones. The current smoke tests evaluate application behavior, not LLM answers.

## Troubleshooting and shutdown

```powershell
docker compose logs --tail 100 order-service
docker compose logs --tail 100 notification-worker
docker compose down
```

Shutdown preserves named volumes and their orders, stock, notification records and provider operations. Inspect errors before retrying uncertain operations; do not use a new idempotency key to blindly retry a timed-out payment.
