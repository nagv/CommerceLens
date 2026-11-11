---
type: quickstart
title: Quickstart
description: Task-routing entry point for the commercelens-notification-worker repository. Orient yourself to the codebase and find the right wiki page for common changes.
tags: [quickstart, onboarding, rabbitmq, postgresql, nodejs]
sources:
  - id: openwiki-source-bb1ebe868e35e9e500714501
    resource: repo://Dockerfile
  - id: openwiki-source-5b54a58d1b51cd490b0e7162
    resource: repo://package.json
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-d4189bbeecb62806cb297b5a
    resource: repo://src/main.ts
generated: { by: "codex/openwiki-lifecycle-review", at: "2026-11-09T01:29:52.130Z" }
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T01:29:52.130Z
---

# Quickstart

**commercelens-notification-worker** is a Node.js/TypeScript service that consumes `order.confirmed` events from RabbitMQ, invokes an HTTP email provider, and persists delivery outcomes in PostgreSQL. It exposes a health endpoint and an unauthenticated status API, and runs as a Dockerized worker with automatic reconnection on broker or database failures.

## What to read first

The wiki pages below are ordered so a new reader can build understanding from identity and contracts through runtime mechanics to operations.

1. **[Service Context](./service-context.md)** — Comprehensive identity, interface contracts, dependencies, and business-flow guarantees for this worker.
2. **[Connection and Session Lifecycle](concepts/lifecycle.md)** — How the reconnect loop, session watcher, and channel/connection events manage readiness and teardown.
3. **[Message Consumption Flow](flows/message-consumption.md)** — End-to-end trace of a single event from queue consumption through validation, deduplication, delivery, persistence, and acknowledgment or dead-lettering.
4. **[Delivery and Retry Logic](concepts/delivery-retry.md)** — Attempt budgeting, backoff timing, idempotency, and terminal `dead` status semantics.
5. **[Configuration and Operations](operations/configuration.md)** — Environment variables, Docker build, health checks, and runtime operational notes.

## Common changes

| Task | Relevant wiki page |
|------|-------------------|
| Add or change an HTTP endpoint | [Service Context](./service-context.md) |
| Change retry/backoff behavior or attempt limits | [Delivery and Retry Logic](concepts/delivery-retry.md) |
| Change RabbitMQ queue or exchange topology | [Connection and Session Lifecycle](concepts/lifecycle.md) |
| Add a configuration variable | [Configuration and Operations](operations/configuration.md) |
| Change the database schema | [Message Consumption Flow](flows/message-consumption.md) |
