# Graph Report - order-service  (2026-11-11)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 136 nodes · 275 edges · 11 communities (3 shown, 8 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 24 edges (avg confidence: 0.85)
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
- Community 7
- Community 8
- Community 9
- Community 10

## God Nodes (most connected - your core abstractions)
1. `OrderStore` - 19 edges
2. `RemoteServices` - 18 edges
3. `FakePorts` - 15 edges
4. `OrderController` - 14 edges
5. `Order` - 13 edges
6. `CheckoutTest` - 11 edges
7. `Checkout` - 11 edges
8. `Request` - 11 edges
9. `Ports` - 10 edges
10. `OutboxPublisher` - 9 edges

## Surprising Connections (you probably didn't know these)
- `OrderController` --references--> `RemoteServices`  [EXTRACTED]
  src/main/java/com/commercelens/orders/OrderController.java → src/main/java/com/commercelens/orders/RemoteServices.java
- `RemoteServices` --references--> `OrderStore`  [EXTRACTED]
  src/main/java/com/commercelens/orders/RemoteServices.java → src/main/java/com/commercelens/orders/OrderStore.java
- `RemoteServices` --implements--> `Ports`  [EXTRACTED]
  src/main/java/com/commercelens/orders/RemoteServices.java → src/main/java/com/commercelens/orders/Checkout.java
- `FakePorts` --references--> `RemoteFailure`  [EXTRACTED]
  src/test/java/com/commercelens/orders/CheckoutTest.java → src/main/java/com/commercelens/orders/Checkout.java
- `Existing` --references--> `Order`  [EXTRACTED]
  src/main/java/com/commercelens/orders/OrderStore.java → src/main/java/com/commercelens/orders/Checkout.java

## Import Cycles
- None detected.

## Communities (11 total, 8 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.14
Nodes (4): Order, OrderController, Existing, OrderStore

### Community 1 - "Community 1"
Cohesion: 0.18
Nodes (3): Ports, CheckoutTest, FakePorts

### Community 7 - "Community 7"
Cohesion: 0.36
Nodes (4): Checkout, Item, Request, Reservation

## Knowledge Gaps
- **1 isolated node(s):** `com.commercelens:order-service`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 37 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RemoteServices` connect `Community 3` to `Community 0`, `Community 1`, `Community 2`, `Community 6`?**
  _High betweenness centrality (0.246) - this node is a cross-community bridge._
- **What connects `com.commercelens:order-service` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.13793103448275862 - nodes in this community are weakly interconnected._
- **Why does `OrderController` connect `Community 0` to `Community 3`, `Community 4`, `Community 7`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **Why does `Ports` connect `Community 1` to `Community 3`, `Community 7`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._