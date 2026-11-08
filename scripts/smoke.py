"""Exercise actual checkout via the portal proxy. Requires the Compose stack."""
import concurrent.futures
import json
import os
import time
import urllib.error
import urllib.request
import uuid

BASE = os.getenv('COMMERCE_URL', 'http://localhost:3000')


def request(path, body=None, key=None):
    headers = {'Content-Type': 'application/json'}
    if key:
        headers['Idempotency-Key'] = key
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode() if body is not None else None, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=40) as res:
            return res.status, json.loads(res.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def checkout(**overrides):
    return dict(customerEmail='demo@example.com', postalCode='10001', items=[{'sku': 'BOOK-001', 'quantity': 1}], paymentScenario='success', shippingScenario='success') | overrides


def wait_ready():
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        try:
            code, products = request('/api/products')
            if code == 200 and len(products) >= 3:
                return products
        except (OSError, ValueError):
            pass
        time.sleep(2)
    raise AssertionError('Portal/order/inventory did not become ready in 180 seconds')


def wait_notification(order_id, expected):
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        code, rows = request('/api/notifications')
        if code == 200:
            for row in rows:
                if row['orderId'] == order_id and row['status'] in expected:
                    return row
        time.sleep(1)
    raise AssertionError(f'No expected notification for {order_id}')


def main():
    products = wait_ready()
    initial = next(p['available'] for p in products if p['sku'] == 'BOOK-001')
    key = str(uuid.uuid4())
    body = checkout()
    code, order = request('/api/orders', body, key)
    assert code == 201 and order['status'] == 'confirmed', (code, order)
    assert order['totalCents'] == 3400 and order['trackingNumber'], order
    code, replay = request('/api/orders', body, key)
    assert code in (200, 201) and replay['id'] == order['id'], replay
    changed = {**body, 'postalCode': '90210'}
    assert request('/api/orders', changed, key)[0] == 409
    stock = next(p['available'] for p in request('/api/products')[1] if p['sku'] == 'BOOK-001')
    assert stock == initial - 1, (initial, stock)
    print('PASS checkout, totals, replay, conflicting key, stock decrement', flush=True)
    wait_notification(order['id'], {'sent', 'delivered'})
    print('PASS asynchronous notification delivery', flush=True)

    for field, scenario in [('paymentScenario', 'decline'), ('shippingScenario', 'failure')]:
        before = next(p['available'] for p in request('/api/products')[1] if p['sku'] == 'BOOK-001')
        code, failure = request('/api/orders', {**body, field: scenario}, str(uuid.uuid4()))
        assert code >= 400, (code, failure)
        after = next(p['available'] for p in request('/api/products')[1] if p['sku'] == 'BOOK-001')
        assert before == after, (scenario, before, after)
        print(f'PASS {scenario}: stock compensated', flush=True)

    code, _ = request('/api/orders', {**body, 'items': [{'sku': 'BOOK-001', 'quantity': 0}]}, str(uuid.uuid4()))
    assert code == 400, code
    code, failure = request('/api/orders', {**body, 'paymentScenario': 'timeout'}, str(uuid.uuid4()))
    assert code >= 400, (code, failure)
    assert failure['status'] == 'payment_unknown', failure
    assert request('/api/orders/' + failure['id'])[1]['status'] == 'payment_unknown'
    print('PASS invalid quantity rejected; timeout remains explicitly uncertain', flush=True)

    code, mail_order = request('/api/orders', {**body, 'customerEmail': 'fail-email@example.com'}, str(uuid.uuid4()))
    assert code == 201 and mail_order['status'] == 'confirmed', (code, mail_order)
    notification = wait_notification(mail_order['id'], {'failed', 'dead', 'dead_letter', 'dead-lettered'})
    assert notification['attempts'] == 3, notification
    assert request('/api/orders/' + mail_order['id'])[1]['status'] == 'confirmed'
    print('PASS email retries exhausted without undoing confirmed checkout', flush=True)

    concurrent_key = str(uuid.uuid4())
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: request('/api/orders', body, concurrent_key), range(2)))
    successes = [o for status, o in outcomes if status in (200, 201)]
    assert successes and len({o['id'] for o in successes}) == 1, outcomes
    assert all(status in (200, 201, 409) for status, _ in outcomes), outcomes
    print('PASS concurrent checkout idempotency', flush=True)
    print('All integration smoke checks passed.', flush=True)


if __name__ == '__main__':
    main()
