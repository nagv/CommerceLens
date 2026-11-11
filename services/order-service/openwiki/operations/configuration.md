---
type: Configuration and Observability
title: Configuration and Observability
description: Environment variables, Spring Boot properties, safe configuration names, multi-stage Docker packaging, RabbitMQ publisher confirms, and the database-backed health check for the CommerceLens Order Service.
tags: [configuration, spring-boot, docker, observability, health-check, environment-variables]
sources:
  - id: openwiki-source-bb1ebe868e35e9e500714501
    resource: repo://Dockerfile
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-16a5a13276943dc522d2add4
    resource: repo://src/main/java/com/commercelens/orders/OrderController.java
  - id: openwiki-source-108cb54cf02515bb6eae368e
    resource: repo://src/main/java/com/commercelens/orders/OrderStore.java
  - id: openwiki-source-ece093ad10b91f3da0b7e34f
    resource: repo://src/main/resources/application.properties
generated: { by: "openwiki/0.7.2", at: "2026-11-08T23:01:58.880Z" }
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T01:28:27.799Z
---

# Configuration and Observability

The CommerceLens Order Service exposes a single TCP port and is configured entirely through Spring Boot properties and environment variables. This page documents the safe names, defaults, deployment packaging, and runtime health check.

## Server settings

The service listens on **port 8080** and includes full error messages in HTTP responses during development.

```properties
server.port=8080
server.error.include-message=always
```

See [`src/main/resources/application.properties`](repo://src/main/resources/application.properties#L1-L2, L17-L17).

## Safe configuration names

All runtime values can be supplied as environment variables. The following names are safe to set in deployment configuration.

### Database

| Environment variable | Alias (also accepted) | Purpose |
|---|---|---|
| `SPRING_DATASOURCE_URL` | `ORDER_DATABASE_URL` | JDBC URL for the PostgreSQL orders database |
| `SPRING_DATASOURCE_USERNAME` | `ORDER_DATABASE_USER` | Database user |
| `SPRING_DATASOURCE_PASSWORD` | `ORDER_DATABASE_PASSWORD` | Database password |

Spring standard names take precedence when both are present. See [`src/main/resources/application.properties`](repo://src/main/resources/application.properties#L2-L4).

> **Default values** (`jdbc:postgresql://localhost:5432/orders`, `commerce`, `commerce-local-only`) are for **local demonstration only**.

### RabbitMQ

| Environment variable | Alias (also accepted) | Purpose |
|---|---|---|
| `SPRING_RABBITMQ_HOST` | `RABBITMQ_HOST` | AMQP broker host |
| `SPRING_RABBITMQ_PORT` | `RABBITMQ_PORT` | AMQP broker port |
| `SPRING_RABBITMQ_USERNAME` | `RABBITMQ_USER` | Broker login user |
| `SPRING_RABBITMQ_PASSWORD` | `RABBITMQ_PASSWORD` | Broker login password |

See [`src/main/resources/application.properties`](repo://src/main/resources/application.properties#L6-L9).

> **Default values** (`localhost`, `5672`, `commerce`, `commerce-local-only`) are for **local demonstration only**.

### External service URLs

| Environment variable | Purpose |
|---|---|
| `INVENTORY_URL` | Base URL of the inventory service (no trailing slash) |
| `PAYMENT_URL` | Base URL of the payment service (no trailing slash) |
| `SHIPPING_URL` | Base URL of the shipping service (no trailing slash) |

See [`src/main/resources/application.properties`](repo://src/main/resources/application.properties#L14-L16).

> **Default values** (`http://localhost:8081`, `http://localhost:8082`, `http://localhost:8083`) are for **local demonstration only**.

## Spring AMQP publisher guarantees

The service enables correlated publisher confirms, returned-message handling, and a broker connection timeout:

```properties
spring.rabbitmq.publisher-confirm-type=correlated
spring.rabbitmq.publisher-returns=true
spring.rabbitmq.template.mandatory=true
spring.rabbitmq.connection-timeout=3000
```

See [`src/main/resources/application.properties`](repo://src/main/resources/application.properties#L10-L13).

These settings ensure that outbox messages published to the `order.confirmed` queue are either confirmed by the broker or returned to the application so the publisher can detect failures and retry later. See [Outbox Publishing](../architecture/outbox-publishing.md) for the full delivery flow.

## Health check

`GET /health` performs a lightweight database liveness probe by executing `SELECT 1` through `OrderStore.healthy()`.

```java
public boolean healthy() {
    return Integer.valueOf(1).equals(jdbc.queryForObject("SELECT 1", Integer.class));
}
```

* `200 OK` — the database is reachable.  
* `503 Service Unavailable` — the database is unreachable.

`OrderController.health()` maps the boolean result to the corresponding HTTP status.

See [`OrderStore.java`](repo://src/main/java/com/commercelens/orders/OrderStore.java#L29-L29) and [`OrderController.java`](repo://src/main/java/com/commercelens/orders/OrderController.java#L14-L14).

## Docker packaging

The [`Dockerfile`](repo://Dockerfile#L1-L13) uses a multi-stage build:

1. **Build stage** — `maven:3.9-eclipse-temurin-21`  
   - Dependencies are resolved offline first for layer caching.  
   - The project is compiled with `mvn verify`.
2. **Runtime stage** — `eclipse-temurin:21-jre-alpine`  
   - Runs as unprivileged user `app`.  
   - Exposes port `8080` and starts the fat JAR (`order-service-0.1.0.jar`) via `java -jar app.jar`.

## Local build and run

Build the image:

```bash
docker build -t commercelens-orders .
```

Local execution should be done through the central **CommerceLens** Compose project; the service expects the Compose-managed PostgreSQL and RabbitMQ instances. See [`README.md`](repo://README.md#L43-L46).

## Related pages

- [API Surface](../architecture/api-surface.md)
- [Outbox Publishing](../architecture/outbox-publishing.md)
- [External Services](../integrations/external-services.md)
- [Service Context](../service-context.md)
