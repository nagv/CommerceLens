# CommerceLens documentation assistant and evaluation runbook

This implementation answers questions and produces high-level change plans from documentation. It never scans application source code at query time. Plans describe affected services, APIs/events, data, sequence, tests/rollout and unknowns, not code-file or line changes.

## Storage

| Artifact | Location | Role |
|---|---|---|
| Service wikis | Individual repositories, openwiki/ | Detailed source documentation |
| Service summaries | catalog/service-cards/*.json | Reviewed compact summaries and dependency evidence |
| Master wiki | openwiki/ | Application overview and workflows |
| Consolidated relationships | catalog/relationships.json | Versioned deterministic graph; literal unknowns retained |
| Derived documentation chunks | .data/corpus.jsonl (ignored) | Heading-aware text, stable snapshot IDs, links and hashes |
| Vectors + text/metadata | Pinecone index / dedicated namespace | Semantic retrieval; application/service/level/topic/source/version metadata |
| Sync manifest and recovery journal | .data/pinecone-manifest.json* (ignored) | Incremental upserts, obsolete-ID deletion, failed-sync recovery |
| Golden cases | evals/golden.jsonl | Factual references, high-level plan rubrics and evidence hashes |
| Local evaluation outputs | evals/results/<run>/ (ignored) | Every repeated result, scores, missing/error states and aggregate summary |
| Traces and experiments | LangSmith, explicitly enabled | Request traces, dataset-linked experiment runs and feedback |

Master summaries are not independent corroboration of the underlying wiki. Navigation and instruction pages are excluded; service-card prose is not embedded again where represented by master pages. Chunks carry repository-relative paths and clickable source URLs. Relationship lookup uses service cards; pub/sub queue nodes connect producers and consumers. Unknown identities stay unresolved instead of becoming guessed edges.

## Environment

From CommerceLens (PowerShell):

```powershell
python -m venv .ai-venv
.ai-venv\Scripts\python.exe -m pip install -r requirements-ai.txt
# Create .env from .env.example only if you do not already have .env.
```

Configure Nebius chat/embedding keys, PINECONE_API_KEY, and optionally LANGSMITH_API_KEY in the ignored .env. The actual Nebius embedding model Qwen/Qwen3-Embedding-8B was probed at 4096 dimensions; never substitute another embedding model in an existing populated namespace. Generic CHAT_API_KEY/CHAT_BASE_URL/CHAT_MODEL and EMBEDDING_API_KEY/EMBEDDING_BASE_URL/EMBEDDING_MODEL override Nebius aliases; use explicit settings when mixing vendors. `--env-file <path>` selects exactly that file, not a secret-file search. Process environment wins over file values.

RAGAS is isolated from the notebook environment. requirements-ai.txt pins ragas 0.4.3 and langchain-community 0.4.1 to avoid an upstream ChatVertexAI import incompatibility with community 0.4.2. The main assistant needs only PyYAML plus Python standard library; LangSmith/RAGAS are optional evaluation dependencies.

## Build, provision and index

```powershell
.ai-venv\Scripts\python.exe -m commercelens_ai status
.ai-venv\Scripts\python.exe -m commercelens_ai build
.ai-venv\Scripts\python.exe -m commercelens_ai dependencies order-service --direction both --hops 1
.ai-venv\Scripts\python.exe -m commercelens_ai setup
.ai-venv\Scripts\python.exe -m commercelens_ai ingest
```

`setup` probes embedding size with a harmless phrase, creates or verifies the named cosine dense index in AWS us-east-1 and saves its non-secret host in the selected env file. It never deletes or changes an incompatible index, upgrades a plan or edits existing application indexes. Wait for `ready: true` before ingestion (rerunning setup is safe). Pinecone operations can consume the account's quota. Index deletion protection is enabled.

`ingest` sends documentation text to the configured embedding provider, then vectors/text/metadata to Pinecone. It updates only changed records and deletes obsolete IDs owned by its dedicated namespace/manifest. It uses a single-writer lock and a pending-write journal. Keep the manifest between runs; do not share this namespace with another ingestion process. On lost local state use a new namespace rather than assuming orphan records were removed. Metadata changes can also trigger upserts. Data-plane visibility can lag successful writes; check search before declaring ingestion ready.

After wiki changes: refresh the service/master catalog first using docs/OPENWIKI.md, then build and ingest. Source-documentation contradictions are preserved and should be resolved in the source wiki. Stable content hashes track snapshots; source URLs point to main and may later change.

## Ask, plan and browser UI

```powershell
.ai-venv\Scripts\python.exe -m commercelens_ai ask "What is CommerceLens and how are services connected?"
.ai-venv\Scripts\python.exe -m commercelens_ai plan "Plan order cancellation before shipment"
.ai-venv\Scripts\python.exe -m commercelens_ai --trace serve --port 8090
```

Open http://127.0.0.1:8090. Ask and Plan share the same bounded engine used by evaluations. Each UI request is independent; include needed context. The assistant is a separate local UI, not yet embedded in the commerce customer portal. It binds loopback and is not a production multi-user/authenticated deployment.

Use `--backend local` before the command for an explicit credential-free lexical retrieval backend (generation still uses the configured chat provider). Pinecone is the default, and provider errors never silently fall back. Example: `python -m commercelens_ai --backend local search "payment timeout"`. Local retrieval quality is not equivalent to Pinecone vector search.

Budgets default to 12 retrieval/relationship calls, 3 model calls, 6 candidate services and 24,000 context characters. The master provides broad orientation; details are retrieved per service. Plans expand documented dependencies. A coverage warning lists omitted services when the budget is exceeded; large requests should be scoped or split. Future 30-service growth does not mean loading every wiki in every prompt. Context truncation is recorded. Citations are checked for valid retrieved IDs, not automatically proven semantically correct.

## Evaluations

```powershell
# Baseline deterministic checks and run statistics; no external judge or upload.
.ai-venv\Scripts\python.exe -m commercelens_ai evaluate --repetitions 3
# Add model judging, RAGAS factual metrics and dataset-linked LangSmith experiment.
.ai-venv\Scripts\python.exe -m commercelens_ai --trace evaluate --repetitions 3 --judge --ragas --langsmith
```

The initial 14 cases cover factual Q&A, conflicting documentation and high-level planning. Treat them as an MVP seed set, not production acceptance proof. Review/extend them using real questions, adversarial cases and changes; keep held-out cases when tuning retrieval. Repetitions estimate variation. The default model judge uses the same configured model as generation; calibrate against human review and optionally use a different provider/model in the Python API.

Deterministic metrics include expected-service recall, retrieved citation validity, phrase coverage, tool/model calls and latency. Phrase coverage is explicitly lexical, not factual correctness. The judge scores factual groundedness, completeness, uncertainty and plan quality. For plans, proposed changes are not hallucinations merely because they are new; factual premises must still be grounded.

RAGAS runs only for factual ask cases: faithfulness, answer relevancy, reference-based context precision/recall and factual correctness. It is skipped for proposed plans, which have no unique factual reference answer. Missing configurations, parsing errors, provider failures and absent scores are reported separately; averages include only valid scores with coverage counts. Scores do not certify correctness. Review traces and individual failures before interpreting averages.

`--trace` sends request inputs/evidence/results to the configured LangSmith project. `--langsmith` uploads golden examples and run outputs to a new immutable snapshot dataset with a linked experiment and numeric feedback. These are explicit external transfers. Find traces under the project and experiments from the generated dataset/experiment name in summary.json. No emails or messages are sent.

An interactive entry point is evals/CommerceLens_Evals.ipynb. It invokes the isolated CLI environment rather than modifying the earlier notebook environment.

## Verification

```powershell
.ai-venv\Scripts\python.exe -m unittest discover -s tests
```

Tests fake external APIs and exercise real local HTTP endpoints. Windows sandbox restrictions may require running the suite outside the restricted shell for loopback sockets. Unit tests are not live Pinecone or quality validation; record live ingestion, query and experiment checks separately.
