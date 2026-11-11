# Graph Report - payment-service  (2026-11-11)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 29 nodes · 38 edges · 4 communities (2 shown, 2 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 2 edges (avg confidence: 0.85)
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

## God Nodes (most connected - your core abstractions)
1. `PaymentsTest` - 6 edges
2. `authorize()` - 4 edges
3. `provider_client()` - 4 edges
4. `Payment` - 3 edges
5. `Refund` - 3 edges
6. `forward()` - 3 edges
7. `refund()` - 3 edges
8. `health()` - 2 edges
9. `client()` - 2 edges
10. `handle()` - 2 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (4 total, 2 thin omitted)

### Community 1 - "Community 1"
Cohesion: 0.29
Nodes (3): PaymentsTest, client(), handle()

### Community 2 - "Community 2"
Cohesion: 0.33
Nodes (5): authorize(), forward(), Payment, refund(), Refund

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PaymentsTest` connect `Community 1` to `Community 3`?**
  _High betweenness centrality (0.437) - this node is a cross-community bridge._
- **Why does `authorize()` connect `Community 2` to `Community 0`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._