# Graph Report - CommerceLens  (2026-11-08)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 160 nodes · 191 edges · 15 communities (10 shown, 5 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `28aa43c8`
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
- Community 12

## God Nodes (most connected - your core abstractions)
1. `services` - 12 edges
2. `environment` - 11 edges
3. `ProviderTests` - 10 edges
4. `Handler` - 6 edges
5. `main()` - 6 edges
6. `depends_on` - 6 edges
7. `rabbitmq` - 6 edges
8. `volumes` - 6 edges
9. `request()` - 5 edges
10. `inventory-db` - 5 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (15 total, 5 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.16
Nodes (5): checkout(), main(), request(), wait_notification(), wait_ready()

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (18): inventory-service, mock-providers, notifications-db, orders-db, payment-service, rabbitmq, shipping-service, condition (+10 more)

### Community 2 - "Community 2"
Cohesion: 0.12
Nodes (15): build, depends_on, ports, build, volumes, name, services, customer-portal (+7 more)

### Community 4 - "Community 4"
Cohesion: 0.17
Nodes (15): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, environment, image, volumes, environment, image (+7 more)

### Community 5 - "Community 5"
Cohesion: 0.15
Nodes (13): inventory-db, DATABASE_URL, EMAIL_PROVIDER_URL, PROVIDER_TIMEOUT_MS, RABBITMQ_URL, condition, build, depends_on (+5 more)

### Community 6 - "Community 6"
Cohesion: 0.15
Nodes (12): application, id, name, pipeline, graphify_command, openwiki_command, per_repository_order, services (+4 more)

### Community 7 - "Community 7"
Cohesion: 0.18
Nodes (11): INVENTORY_URL, PAYMENT_URL, SHIPPING_URL, SPRING_DATASOURCE_PASSWORD, SPRING_DATASOURCE_URL, SPRING_DATASOURCE_USERNAME, SPRING_RABBITMQ_HOST, SPRING_RABBITMQ_PASSWORD (+3 more)

### Community 8 - "Community 8"
Cohesion: 0.18
Nodes (11): PAYMENT_PROVIDER_URL, PROVIDER_TIMEOUT_SECONDS, SHIPPING_PROVIDER_URL, build, depends_on, environment, payment-service, shipping-service (+3 more)

### Community 9 - "Community 9"
Cohesion: 0.57
Nodes (8): interval, retries, test, timeout, healthcheck, healthcheck, healthcheck, healthcheck

### Community 10 - "Community 10"
Cohesion: 0.29
Nodes (7): RABBITMQ_DEFAULT_PASS, RABBITMQ_DEFAULT_USER, environment, image, ports, volumes, rabbitmq

## Knowledge Gaps
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `services` connect `Community 2` to `Community 1`, `Community 4`, `Community 5`, `Community 8`, `Community 10`?**
  _High betweenness centrality (0.309) - this node is a cross-community bridge._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._
- **Why does `order-service` connect `Community 1` to `Community 2`, `Community 7`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._
- **Why does `environment` connect `Community 7` to `Community 1`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._