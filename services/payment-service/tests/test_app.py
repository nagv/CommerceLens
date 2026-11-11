import unittest
import httpx
from fastapi.testclient import TestClient
from app import app, provider_client


class PaymentsTest(unittest.TestCase):
    def setUp(self):
        self.requests = []
        self.mode = 'ok'
        async def handle(request):
            self.requests.append(request)
            if self.mode == 'timeout':
                raise httpx.ReadTimeout('slow')
            if self.mode == 'decline':
                return httpx.Response(402, json={'message': 'declined'})
            return httpx.Response(200, json={'paymentId': 'pay-1', 'status': 'authorized'} if request.url.path == '/payments' else {'status': 'refunded'})
        async def client():
            async with httpx.AsyncClient(transport=httpx.MockTransport(handle), base_url='http://provider') as c:
                yield c
        app.dependency_overrides[provider_client] = client
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_authorization_passes_idempotency_and_validates_amount(self):
        body = {'orderId': 'o1', 'amountCents': 3400, 'currency': 'USD'}
        self.assertEqual(self.client.post('/api/payments', json=body).json()['paymentId'], 'pay-1')
        self.assertEqual(self.requests[0].headers['Idempotency-Key'], 'o1')
        self.assertEqual(self.client.post('/api/payments', json={**body, 'amountCents': 0}).status_code, 422)

    def test_timeout_is_uncertain_and_decline_is_distinct(self):
        body = {'orderId': 'o1', 'amountCents': 3400}
        self.mode = 'timeout'
        response = self.client.post('/api/payments', json=body)
        self.assertEqual(response.status_code, 504)
        self.assertEqual(response.json()['status'], 'unknown')
        self.mode = 'decline'
        self.assertEqual(self.client.post('/api/payments', json=body).status_code, 402)

    def test_refund_key_is_distinct(self):
        self.assertEqual(self.client.post('/api/payments/pay-1/refund', json={'orderId': 'o1'}).status_code, 200)
        self.assertEqual(self.requests[0].headers['Idempotency-Key'], 'refund:o1:pay-1')
