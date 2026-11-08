import importlib.util
import tempfile
import unittest
import io
from pathlib import Path

spec = importlib.util.spec_from_file_location('provider', Path(__file__).parents[1] / 'mock-providers' / 'server.py')
provider = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provider)


class ProviderTests(unittest.TestCase):
    def test_chunked_request_from_dotnet_client(self):
        handler = object.__new__(provider.Handler)
        handler.headers = {'Transfer-Encoding': 'chunked'}
        handler.rfile = io.BytesIO(b'7\r\n{"a":1}\r\n0\r\n\r\n')
        self.assertEqual(b'{"a":1}', handler.read_body())
        handler.rfile = io.BytesIO(b'10001\r\n')
        with self.assertRaises(ValueError):
            handler.read_body()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = provider.Store(str(Path(self.tmp.name) / 'provider.db'))

    def tearDown(self):
        self.tmp.cleanup()

    def test_payment_replay_has_same_id_and_one_operation(self):
        body = dict(orderId='one', amountCents=3400, currency='USD', scenario='success')
        first = self.store.process('/payments', body)
        self.assertEqual(first, self.store.process('/payments', body))
        self.assertEqual('authorized', first[1]['status'])
        self.assertEqual(1, self.store.count())

    def test_conflicting_payment_rejected(self):
        body = dict(orderId='one', amountCents=3400, currency='USD')
        self.store.process('/payments', body)
        self.assertEqual(409, self.store.process('/payments', {**body, 'amountCents': 1})[0])

    def test_decline_does_not_authorize(self):
        result = self.store.process('/payments', dict(orderId='one', amountCents=3400, currency='USD', scenario='decline'))
        self.assertEqual(402, result[0])

    def test_shipping_failure_and_email_failure(self):
        self.assertEqual(422, self.store.process('/shipments', dict(orderId='one', postalCode='10001', scenario='failure'))[0])
        self.assertEqual(503, self.store.process('/email', dict(eventId='e1', customerEmail='fail-email@example.com'))[0])

    def test_invalid_amount_and_missing_id_rejected(self):
        self.assertEqual(400, self.store.process('/payments', dict(orderId='one', amountCents=-1, currency='USD'))[0])
        self.assertEqual(400, self.store.process('/shipments', dict(postalCode='10001'))[0])

    def test_refund_is_idempotent(self):
        paid = self.store.process('/payments', dict(orderId='one', amountCents=3400, currency='USD'))[1]
        body = dict(orderId='one', paymentId=paid['paymentId'])
        self.assertEqual(self.store.process('/refunds', body), self.store.process('/refunds', body))


if __name__ == '__main__':
    unittest.main()
