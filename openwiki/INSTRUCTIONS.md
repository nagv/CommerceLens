# Application-wide documentation

Maintain the master catalog for the six CommerceLens services. Read compose.yaml, catalog/source-evidence.json and the linked service wikis. Prefer source code over wiki assertions. Cite original commit-pinned source links from the snapshot. Never infer runtime calls from Compose depends_on or workspace membership.

Document responsibilities, API callers/callees, database ownership, queue producers/consumers, logical external providers, idempotency, failure states and end-to-end checkout. Distinguish local mocks from real integrations and implemented capabilities from planned RAG/chat/evaluation work. Surface conflicts or missing evidence explicitly.

Preserve the six entry pages and their navigation. A service wiki update does not automatically refresh this catalog. Refresh and review the source snapshot before revising facts; use the lifecycle APIs or openwiki --update --print to finalize reviewed changes. Do not claim that lifecycle completion alone proves factual correctness.
