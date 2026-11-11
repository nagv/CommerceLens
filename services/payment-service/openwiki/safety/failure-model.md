---
type: safety-reference
title: "Payment Failure Model, Idempotency, and Reconciliation"
description: Safety rules governing idempotency keys, ambiguous provider timeouts, explicit declines, and required reconciliation before retries.
tags: [safety, idempotency, reconciliation, payments, failures]
sources:
  - id: openwiki-source-17dded95897e01ee430228e3
    resource: repo://app.py
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-aee60addf228e6c9bf133836
    resource: repo://tests/test_app.py
generated: { by: "openwiki/0.7.2", at: "2026-11-08T23:01:22.698Z" }
verified:
  - by: openwiki/0.7.2
    at: 2026-11-09T01:29:41.531Z
---

# Payment Failure Model, Idempotency, and Reconciliation

The payment service forwards write requests to an external provider. Because provider calls mutate money and can fail ambiguously, the service uses structured idempotency keys and strict HTTP status codes to separate safe failures from dangerous unknowns. This page documents the failure taxonomy, key schemes, and the reconciliation-invariant: **no blind retry of an ambiguous payment write**.

## Idempotency key schemes

The service sends an `Idempotency-Key` header on every provider POST so the provider can deduplicate or detect conflicting replays.

### Payments (`POST /api/payments`)

The key is the caller-supplied `orderId`.

```python
return await forward(client, '/payments', payment.model_dump(), payment.orderId)
```

### Refunds (`POST /api/payments/{paymentId}/refund`)

The key is `refund:{orderId}:{paymentId}`. This guarantees that a refund is scoped to both the original payment and the order, so retries of the same refund use the same key while refunds for different payments remain distinct.

```python
return await forward(client, '/refunds', {'paymentId': paymentId, 'orderId': refund.orderId},
                     f'refund:{refund.orderId}:{paymentId}')
```

### Provider contract

The README documents the requirement that the provider must durably enforce idempotency keys and reject conflicting payloads. A provider that silently ignores the header cannot satisfy the safety model of this service.

## Failure taxonomy

All payment and refund requests pass through the same `forward()` function, which classifies provider outcomes into four categories.

### 402 Payment Declined (explicit failure)

When the provider returns HTTP 402, the service translates it to a 402 response with `status: "declined"`.

```python
if response.status_code == 402:
    return JSONResponse(status_code=402, content={'message': 'Payment declined', 'status': 'declined'})
```

A 402 is an **explicit** failure. The caller can safely inform the end user that the charge was refused. No reconciliation is required before retrying with different parameters, because the provider has durably recorded the decline.

### 409 Conflict (idempotency key collision)

When the provider returns HTTP 409, the service returns a 409 response with `status: "unknown"`.

```python
if response.status_code == 409:
    return JSONResponse(status_code=409, content={'message': 'Conflicting provider idempotency key', 'status': 'unknown'})
```

A 409 means the provider already holds a different payload under the same idempotency key. This is a safety violation in the caller's domain: the caller attempted to change amount or other fields while reusing the same `orderId`. Reconciliation is required to determine whether the original write succeeded.

### 502 Bad Gateway (provider unreachable or invalid response)

Any non-success HTTP status other than 402 or 409, or any request error / malformed JSON / unexpected shape, becomes a 502 with `status: "unknown"`.

```python
if not response.is_success:
    return JSONResponse(status_code=502, content={'message': 'Payment provider unavailable; reconcile before retrying', 'status': 'unknown'})
```

```python
except (httpx.RequestError, ValueError):
    return JSONResponse(status_code=502, content={'message': 'Payment provider response unavailable; outcome requires reconciliation', 'status': 'unknown'})
```

A 502 signals that the provider could not be reached or returned an invalid / unexpected response. The charge **may or may not** have succeeded. The caller must reconcile with the provider before retrying.

### 504 Gateway Timeout (truly unknown outcome)

When the provider does not respond before the configured timeout, the service returns 504 with `status: "unknown"`.

```python
except httpx.TimeoutException:
    return JSONResponse(status_code=504, content={'message': 'Payment provider timed out; outcome requires reconciliation', 'status': 'unknown'})
```

A 504 means the request crossed the network but no response arrived. Because the provider may have partially or fully processed the charge before the timeout, the outcome is **genuinely unknown**. The caller must perform manual or automated reconciliation before any retry.

## Reconciliation invariant

The contract of the service follows a single invariant: **ambiguous provider outcomes must be reconciled before retry**.

| Status | Meaning | Safe to retry without reconciliation? |
|--------|---------|--------------------------------------|
| 200 OK | Success | Already complete |
| 402 | Declined | Yes (new request) |
| 409 | Conflicting idempotency key | No |
| 502 | Provider error or invalid response | No |
| 504 | Provider timeout | No |

Retries issued against 502 or 504 without reconciliation risk double-charging the customer or creating orphaned provider state.

## Verification by tests

`tests/test_app.py` validates the safety-critical distinctions above.

### Timeout vs decline

`test_timeout_is_uncertain_and_decline_is_distinct` confirms that a mocked provider timeout results in HTTP 504 with `status: "unknown"`, while a mocked provider decline results in HTTP 402 with no `unknown` status.

### Distinct refund idempotency key

`test_refund_key_is_distinct` confirms that refund requests carry the header `Idempotency-Key: refund:o1:pay-1`, distinct from the payment key `o1`.

### Idempotency propagation and validation

`test_authorization_passes_idempotency_and_validates_amount` confirms that the payment request carries `Idempotency-Key: o1` and that the service rejects invalid amounts via FastAPI/Pydantic validation before reaching the provider.
