# Graph Report - inventory-service  (2026-11-11)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 47 nodes · 73 edges · 9 communities (1 shown, 8 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 7 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0a506696`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 1
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8

## God Nodes (most connected - your core abstractions)
1. `Store` - 6 edges
2. `ReserveRequest` - 5 edges
3. `fingerprint()` - 4 edges
4. `validate()` - 4 edges
5. `fail()` - 4 edges
6. `write()` - 4 edges
7. `TestPostgresReservationsNeverOversellAndReleaseIsIdempotent()` - 4 edges
8. `Reservation` - 3 edges
9. `TestFingerprintIndependentOfItemOrder()` - 3 edges
10. `TestValidateRejectsInvalidAndDuplicateItems()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `TestFingerprintIndependentOfItemOrder()` --calls--> `fingerprint()`  [INFERRED]
  main_test.go → main.go
- `TestValidateRejectsInvalidAndDuplicateItems()` --calls--> `validate()`  [INFERRED]
  main_test.go → main.go

## Import Cycles
- None detected.

## Communities (9 total, 8 thin omitted)

### Community 1 - "Community 1"
Cohesion: 0.28
Nodes (6): Item, ReserveRequest, fingerprint(), TestFingerprintIndependentOfItemOrder(), TestValidateRejectsInvalidAndDuplicateItems(), validate()

## Knowledge Gaps
- **1 isolated node(s):** `github.com/nagv/commercelens-inventory-service`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 17 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Store` connect `Community 5` to `Community 0`, `Community 3`, `Community 4`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **What connects `github.com/nagv/commercelens-inventory-service` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Why does `fingerprint()` connect `Community 1` to `Community 0`, `Community 4`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `validate()` connect `Community 1` to `Community 0`, `Community 4`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._