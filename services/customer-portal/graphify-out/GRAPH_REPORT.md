# Graph Report - customer-portal  (2026-11-11)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 65 nodes · 98 edges · 12 communities (8 shown, 4 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.85)
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
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11

## God Nodes (most connected - your core abstractions)
1. `App()` - 13 edges
2. `compilerOptions` - 10 edges
3. `checkoutAttempt()` - 5 edges
4. `validateCheckout()` - 5 edges
5. `request()` - 5 edges
6. `ApiError` - 4 edges
7. `submit()` - 4 edges
8. `cartSummary()` - 4 edges
9. `scripts` - 4 edges
10. `refresh()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `App()` --calls--> `request()`  [EXTRACTED]
  src/main.tsx → src/api.ts
- `App()` --calls--> `cartSummary()`  [EXTRACTED]
  src/main.tsx → src/domain.ts
- `App()` --calls--> `money()`  [EXTRACTED]
  src/main.tsx → src/domain.ts
- `refresh()` --calls--> `request()`  [EXTRACTED]
  src/main.tsx → src/api.ts
- `App()` --calls--> `checkoutAttempt()`  [EXTRACTED]
  src/main.tsx → src/domain.ts

## Import Cycles
- None detected.

## Communities (12 total, 4 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.17
Nodes (11): compilerOptions, allowImportingTsExtensions, jsx, lib, module, moduleResolution, noEmit, skipLibCheck (+3 more)

### Community 1 - "Community 1"
Cohesion: 0.27
Nodes (7): checkoutAttempt(), validateCheckout(), App(), refresh(), submit(), savedAttempt(), Status()

### Community 2 - "Community 2"
Cohesion: 0.39
Nodes (6): Attempt, Checkout, money(), Notification, Order, Product

### Community 3 - "Community 3"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 4 - "Community 4"
Cohesion: 0.40
Nodes (5): dependencies, react@^19.0.0, react-dom@^19.0.0, react, react-dom

### Community 5 - "Community 5"
Cohesion: 0.40
Nodes (5): devDependencies, @types/react@^19.0.0, @types/react-dom@^19.0.0, @types/react, @types/react-dom

### Community 6 - "Community 6"
Cohesion: 0.50
Nodes (4): scripts, build, dev, test

### Community 8 - "Community 8"
Cohesion: 0.50
Nodes (3): cartSummary(), body, products

## Knowledge Gaps
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `react` connect `Community 4` to `Community 2`, `Community 3`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Why does `react-dom` connect `Community 4` to `Community 2`, `Community 3`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Why does `App()` connect `Community 1` to `Community 8`, `Community 2`, `Community 7`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._