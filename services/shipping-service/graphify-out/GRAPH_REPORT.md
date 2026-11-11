# Graph Report - shipping-service  (2026-11-11)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 40 nodes · 69 edges · 6 communities (2 shown, 4 thin omitted)
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 15 edges (avg confidence: 0.85)
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
- Community 5

## God Nodes (most connected - your core abstractions)
1. `ProviderException` - 8 edges
2. `ShippingProvider` - 7 edges
3. `Handler` - 7 edges
4. `ShipmentRequest` - 6 edges
5. `ShippingTests` - 5 edges
6. `Shipment` - 3 edges
7. `net8.0` - 2 edges
8. `Microsoft.NET.Test.Sdk (17.12.0)` - 1 edges
9. `xunit (2.9.3)` - 1 edges
10. `xunit.runner.visualstudio (3.0.2)` - 1 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (6 total, 4 thin omitted)

### Community 1 - "Community 1"
Cohesion: 0.29
Nodes (6): Microsoft.NET.Test.Sdk (17.12.0), xunit (2.9.3), xunit.runner.visualstudio (3.0.2), Microsoft.NET.Sdk, Microsoft.NET.Sdk.Web, net8.0

### Community 3 - "Community 3"
Cohesion: 0.40
Nodes (3): ProviderException, Code, Status

## Knowledge Gaps
- **7 isolated node(s):** `Microsoft.NET.Test.Sdk (17.12.0)`, `xunit (2.9.3)`, `xunit.runner.visualstudio (3.0.2)`, `Microsoft.NET.Sdk`, `Microsoft.NET.Sdk.Web` (+2 more)
  These have ≤1 connection - possible missing edges. (Counts symbols only; 18 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ProviderException` connect `Community 3` to `Community 0`, `Community 5`?**
  _High betweenness centrality (0.145) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `ShippingProvider` (e.g. with `ShippingTests.ExplicitRejectionIsSafeToCompensate()` and `ShippingTests.FailureDoesNotProduceShipment()`) actually correct?**
  _`ShippingProvider` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Microsoft.NET.Test.Sdk (17.12.0)`, `xunit (2.9.3)`, `xunit.runner.visualstudio (3.0.2)` to the rest of the system?**
  _7 weakly-connected nodes found - possible missing edges._
- **Why does `Handler` connect `Community 2` to `Community 0`, `Community 4`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `ShipmentRequest` (e.g. with `ShippingTests.ExplicitRejectionIsSafeToCompensate()` and `ShippingTests.FailureDoesNotProduceShipment()`) actually correct?**
  _`ShipmentRequest` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Why does `ShippingTests` connect `Community 2` to `Community 0`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._