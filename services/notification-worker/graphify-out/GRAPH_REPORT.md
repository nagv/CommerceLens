# Graph Report - notification-worker  (2026-11-11)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 54 nodes · 75 edges · 11 communities (6 shown, 5 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
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

## God Nodes (most connected - your core abstractions)
1. `compilerOptions` - 9 edges
2. `connect()` - 6 edges
3. `deliver()` - 4 edges
4. `parseEvent()` - 4 edges
5. `watchSession()` - 4 edges
6. `scripts` - 4 edges
7. `main()` - 3 edges
8. `sleep()` - 3 edges
9. `amqplib` - 3 edges
10. `pg` - 3 edges

## Surprising Connections (you probably didn't know these)
- `connect()` --calls--> `watchSession()`  [EXTRACTED]
  src/main.ts → src/lifecycle.ts
- `connect()` --calls--> `deliver()`  [EXTRACTED]
  src/main.ts → src/delivery.ts
- `connect()` --calls--> `parseEvent()`  [EXTRACTED]
  src/main.ts → src/delivery.ts

## Import Cycles
- None detected.

## Communities (11 total, 5 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.30
Nodes (8): deliver(), Event, parseEvent(), connect(), main(), pool, server, sleep()

### Community 1 - "Community 1"
Cohesion: 0.18
Nodes (10): compilerOptions, esModuleInterop, module, moduleResolution, outDir, rootDir, skipLibCheck, strict (+2 more)

### Community 3 - "Community 3"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 4 - "Community 4"
Cohesion: 0.40
Nodes (5): dependencies, amqplib@0.10.5, pg@8.13.3, amqplib, pg

### Community 5 - "Community 5"
Cohesion: 0.50
Nodes (4): scripts, build, start, test

### Community 6 - "Community 6"
Cohesion: 0.67
Nodes (3): devDependencies, tsx@4.19.4, tsx

## Knowledge Gaps
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `amqplib` connect `Community 4` to `Community 0`, `Community 3`?**
  _High betweenness centrality (0.158) - this node is a cross-community bridge._
- **Why does `pg` connect `Community 4` to `Community 0`, `Community 3`?**
  _High betweenness centrality (0.158) - this node is a cross-community bridge._
- **Why does `scripts` connect `Community 5` to `Community 3`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._