"""HTTP payment boundary. Provider must enforce durable idempotency by order ID."""
import os
from typing import Literal
import httpx
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title='CommerceLens Payments')


class Payment(BaseModel):
    orderId: str = Field(min_length=1, max_length=128)
    amountCents: int = Field(gt=0, le=100_000_000, strict=True)
    currency: Literal['USD'] = 'USD'
    scenario: Literal['success', 'decline', 'timeout'] = 'success'


class Refund(BaseModel):
    orderId: str = Field(min_length=1, max_length=128)


async def provider_client():
    async with httpx.AsyncClient(
        base_url=os.getenv('PAYMENT_PROVIDER_URL', 'http://mock-provider:8080'),
        timeout=float(os.getenv('PROVIDER_TIMEOUT_SECONDS', '3')),
    ) as client:
        yield client


async def forward(client, path, body, key):
    try:
        response = await client.post(path, json=body, headers={'Idempotency-Key': key})
        if response.status_code == 402:
            return JSONResponse(status_code=402, content={'message': 'Payment declined', 'status': 'declined'})
        if response.status_code == 409:
            return JSONResponse(status_code=409, content={'message': 'Conflicting provider idempotency key', 'status': 'unknown'})
        if not response.is_success:
            return JSONResponse(status_code=502, content={'message': 'Payment provider unavailable; reconcile before retrying', 'status': 'unknown'})
        data = response.json()
        expected = 'authorized' if path == '/payments' else 'refunded'
        if not isinstance(data, dict) or data.get('status') != expected or (path == '/payments' and not data.get('paymentId')):
            raise ValueError('Invalid provider response')
        return data
    except httpx.TimeoutException:
        return JSONResponse(status_code=504, content={'message': 'Payment provider timed out; outcome requires reconciliation', 'status': 'unknown'})
    except (httpx.RequestError, ValueError):
        return JSONResponse(status_code=502, content={'message': 'Payment provider response unavailable; outcome requires reconciliation', 'status': 'unknown'})


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.post('/api/payments')
async def authorize(payment: Payment, client=Depends(provider_client)):
    return await forward(client, '/payments', payment.model_dump(), payment.orderId)


@app.post('/api/payments/{paymentId}/refund')
async def refund(paymentId: str, refund: Refund, client=Depends(provider_client)):
    return await forward(client, '/refunds', {'paymentId': paymentId, 'orderId': refund.orderId}, f'refund:{refund.orderId}:{paymentId}')
