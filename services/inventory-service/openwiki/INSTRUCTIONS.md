# Application-context documentation brief

Document this repository as a component of CommerceLens using current source, tests,
API contracts, migrations, safe configuration templates and deployment manifests.

Maintain a service-context page covering:
- Identity: purpose, business capabilities, technology stack, entry points and ownership evidence.
- Provided interfaces: exact HTTP methods/routes, schemas and published event/topic names.
- Consumed dependencies: outbound calls, configuration variable names, subscribed events,
  databases, caches and external providers. Separate runtime from package dependencies.
- Business flow: input, validation, state changes, output, and cross-repository boundaries.
- Failure behavior: timeout, retry count/backoff, idempotency, compensation, dead letters,
  uncertainty and manual intervention. Do not claim current production status.
- Configuration and observability: safe variable names, health checks, logs and setup.
- Evidence: repository-relative paths, symbols/line ranges, unresolved references and conflicts.

Include a dependency table with direction, relationship type, target identifier,
interface/topic, configuration variable, supporting evidence and certainty.

Read the Graphify code-only artifacts as supporting structural evidence, checking
source where needed. Do not invent relationships missing from source. Do not infer a
runtime service dependency solely from a shared package or similar name. Mark missing
information as unknown. Clearly identify mock providers and distinguish them from real
sandbox integrations. Never reproduce secret values. Keep each section suitable for
retrieval, preserving exact API/event/configuration identifiers and source citations.
