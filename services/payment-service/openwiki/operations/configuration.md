---
type: service operations
title: Deployment, Configuration, and Observability
description: Environment variables, Dockerfile targets, health checks, and runtime constraints for the payment service.
tags: [deployment, docker, configuration, health-checks, fastapi]
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T01:29:41.531Z
sources:
  - id: openwiki-source-17dded95897e01ee430228e3
    resource: repo://app.py
  - id: openwiki-source-bb1ebe868e35e9e500714501
    resource: repo://Dockerfile
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
generated: { by: "openwiki/0.7.2", at: "2026-11-08T23:01:22.698Z" }
---

# Deployment, Configuration, and Observability

This page covers how to build, configure, and operate the CommerceLens payment service. It documents the multi-stage Dockerfile, required and optional environment variables, runtime constraints, and how to verify that the service is healthy.

## Docker build stages

The Dockerfile uses a multi-stage build with three targets:

<!-- openwiki: mermaid parse failed and this diagram was converted to a text fence so it does not break rendering. Fix the diagram source and restore the mermaid fence. Parser error: Heuristic: an unescaped angle bracket inside a label breaks rendering; rephrase the label. -->
```text
flowchart TD
    base["Stage: base<br>python:3.12-slim<br>Install dependencies, copy app.py"]
    test["Stage: test<br>Copy tests, run unittest"]
    runtime["Stage: runtime<br>Create unprivileged user, expose 8080, start uvicorn"]
    base --> test
    base --> runtime
```

- **base** installs Python dependencies from `requirements.txt` and copies `app.py` into the image.
- **test**, from `base`, copies the `tests/` directory and runs the provider contract tests with `python -m unittest discover -s tests -v`.
- **runtime**, from `base`, creates an unprivileged user with UID 10001, exposes port 8080, and starts the FastAPI application via `uvicorn` on host `0.0.0.0`.

You can build the production image with:

```bash
docker build -t commercelens-payment .
```

Or run the provider contract tests by targeting the `test` stage:

```bash
docker build --target test -t commercelens-payment-test .
```

## Environment variables

The application reads two runtime environment variables via `os.getenv` in [app.py](repo://app.py#L24-L26):

| Variable | Default | Description |
|----------|---------|-------------|
| `PAYMENT_PROVIDER_URL` | `http://mock-provider:8080` | Base URL of the external payment provider. |
| `PROVIDER_TIMEOUT_SECONDS` | `3` | HTTP request timeout for provider calls. |

Both are injected into the `httpx.AsyncClient` that forwards payment and refund requests. Never set secrets in plain environment variables inside the image; pass them at runtime through your orchestrator or secret manager.

## Runtime constraints

- The runtime stage runs as an unprivileged user (`app`, UID 10001).
- The service listens on port **8080**.
- The default timeout for provider HTTP calls is **3 seconds**. Timeouts are treated as ambiguous: a 504 response is returned and the caller must reconcile because the provider may still have created the charge.

## Health checks and observability

The service exposes a readiness/health endpoint:

- **GET `/health`** returns `{"status": "ok"}` with an HTTP 200. No provider dependency is exercised, so it is safe to use as a Kubernetes liveness or readiness probe.

FastAPI generates interactive OpenAPI documentation at **`/docs`**. You can use it to explore the payment and refund endpoints while the service is running.

## Security notice

The local demo configuration has **no end-user authentication**. Do not expose the service on public networks. Restrict access to private networks or localhost/loopback interfaces only.
