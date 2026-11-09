# Documentation assistant implementation plan

> **For agentic workers:** Use focused parallel work for independent modules; root integrates and reviews.

**Goal:** Implement documentation-only application Q&A, high-level change planning, Pinecone ingestion, deterministic relationship lookup and repeatable evaluations.

**Architecture:** Manifest-driven documentation corpus plus versioned relationship JSON. Bounded retrieval workflow: identify relevant services, expand documented connections for plans, retrieve details, generate cited answers. Default local lexical backend permits credential-free tests; Pinecone is an explicit production backend, never a silent fallback. Nebius/OpenAI-compatible chat and OpenAI embeddings are configured separately. CLI and local browser chat use identical engine. Evaluation stores local JSONL and optionally publishes experiments/feedback to LangSmith and runs RAGAS.

**Tech Stack:** Python 3.12, standard-library HTTP/CLI/server, PyYAML; optional OpenAI/LangSmith/RAGAS SDKs already available in the notebook environment.

**Spec:** User-approved conversation: master/service wiki indexing, service relationships, /ask and /plan, high-level plans only, citations, repeated evaluation and efficiency measurements.

## Global constraints
- No source-code ingestion or line-level planning.
- Never present local lexical retrieval as Pinecone or skipped judge scores as successful evaluations.
- Explicit API configuration; credentials never enter logs or generated artifacts.
- Version documents, stable chunk IDs, detect deletion and stale records; exclude instructions and navigation noise.
- Plans distinguish evidence, proposed changes and unknowns; conflicting service documentation remains visible.
- Local UI binds loopback by default. Index mutation requires explicit ingest command.

## Tasks
- [x] Knowledge: deterministic relationship aggregation with evidence; heading-aware chunks and metadata; local search and incremental Pinecone sync; unit tests for filters, deletion and dependency direction.
- [x] Assistant: bounded ask/plan routing, citation validation, structured outputs, latency/tool traces; CLI and simple local chat UI; tests with fake model/retriever.
- [x] Evals: versioned golden dataset, repeated runs, deterministic checks, optional judge/RAGAS and LangSmith experiment upload; explicit failed/missing scores; unit tests.
- [x] Integration: configuration/providers, CLI, setup documentation, credential discovery, corpus build, all tests, live smoke where credentials allow; commit and report external blockers honestly.

## Review focus
Cross-service impact omissions; hallucinated citations; stale vector deletion; documentation-instruction injection; external failures reported as failures rather than empty successes.

## Execution record

Code, CLI, UI, tests and live Nebius/RAGAS/LangSmith experiments are complete; see ../../AI_VERIFICATION.md. The dedicated Pinecone index contains 452 chunks; repeat ingestion made no changes, filtered search passed, and the UI uses Pinecone. Three smoke cases repeated twice completed successfully and uploaded to LangSmith. Quality scores and variable latency remain evaluation findings, not production acceptance. No existing index changed. The user explicitly approved Nebius documentation transfer and LangSmith dataset/evidence/result upload.
