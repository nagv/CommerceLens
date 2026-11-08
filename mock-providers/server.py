"""Local-only external provider simulator. No real charges, shipments, or email."""
import hashlib
import json
import os
import sqlite3
import time
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class Store:
    def __init__(self, path):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(path)) as db:
            db.execute('CREATE TABLE IF NOT EXISTS operations (key TEXT PRIMARY KEY, fingerprint TEXT, code INTEGER, response TEXT)')
            db.commit()

    def count(self):
        with closing(sqlite3.connect(self.path)) as db:
            return db.execute('SELECT count(*) FROM operations').fetchone()[0]

    def process(self, route, body):
        if not isinstance(body, dict):
            return 400, {'message': 'JSON object required'}
        identifier = body.get('eventId' if route == '/email' else 'orderId')
        if not isinstance(identifier, str) or not identifier.strip():
            return 400, {'message': 'A non-empty operation ID is required'}
        if route == '/payments':
            amount = body.get('amountCents')
            if type(amount) is not int or amount <= 0 or body.get('currency') != 'USD':
                return 400, {'message': 'Positive integer amountCents and USD currency required'}
        if route == '/shipments' and not body.get('postalCode'):
            return 400, {'message': 'postalCode is required'}
        if route == '/refunds' and not body.get('paymentId'):
            return 400, {'message': 'paymentId is required'}
        if route == '/email' and not body.get('customerEmail'):
            return 400, {'message': 'customerEmail is required'}
        if route not in ('/payments', '/refunds', '/shipments', '/email'):
            return 404, {'message': 'Unknown provider operation'}
        fingerprint = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        key = route + ':' + identifier
        suffix = hashlib.sha256(identifier.encode()).hexdigest()[:16]
        with closing(sqlite3.connect(self.path, timeout=10)) as db:
            db.execute('BEGIN IMMEDIATE')
            existing = db.execute('SELECT fingerprint, code, response FROM operations WHERE key=?', (key,)).fetchone()
            if existing:
                if existing[0] != fingerprint:
                    return 409, {'message': 'Idempotency key reused with different payload'}
                return existing[1], json.loads(existing[2])
            scenario = body.get('scenario', 'success')
            code = 200
            if route == '/payments':
                if scenario == 'decline':
                    code, response = 402, {'message': 'Simulated payment decline', 'status': 'declined'}
                else:
                    response = {'paymentId': 'pay_' + suffix, 'status': 'authorized'}
            elif route == '/refunds':
                paid = db.execute('SELECT response, code FROM operations WHERE key=?', ('/payments:' + identifier,)).fetchone()
                if not paid or paid[1] != 200 or json.loads(paid[0]).get('paymentId') != body['paymentId']:
                    return 404, {'message': 'Authorized payment not found'}
                response = {'status': 'refunded', 'paymentId': body['paymentId']}
            elif route == '/shipments':
                if scenario == 'failure':
                    return 422, {'message': 'Simulated shipping provider rejection', 'status': 'failed'}
                response = {'shipmentId': 'ship_' + suffix, 'status': 'created', 'trackingNumber': 'CL-' + suffix.upper(), 'shippingCents': 500}
            else:
                if 'fail-email' in str(body['customerEmail']).lower():
                    return 503, {'message': 'Simulated email provider outage'}
                response = {'messageId': 'mail_' + suffix, 'status': 'sent'}
            db.execute('INSERT INTO operations VALUES (?,?,?,?)', (key, fingerprint, code, json.dumps(response)))
            db.commit()
            return code, response


class Handler(BaseHTTPRequestHandler):
    def read_body(self):
        if self.headers.get('Transfer-Encoding', '').lower() == 'chunked':
            chunks = bytearray()
            while True:
                size = int(self.rfile.readline(128).split(b';', 1)[0].strip(), 16)
                if size < 0 or len(chunks) + size > 65536:
                    raise ValueError('Invalid body size')
                if size == 0:
                    if self.rfile.readline(128) != b'\r\n':
                        raise ValueError('Trailers unsupported')
                    return bytes(chunks)
                part = self.rfile.read(size)
                if len(part) != size or self.rfile.read(2) != b'\r\n':
                    raise ValueError('Invalid chunk')
                chunks.extend(part)
        length = int(self.headers.get('Content-Length', '0'))
        if length <= 0 or length > 65536:
            raise ValueError('Invalid body size')
        return self.rfile.read(length)

    def send_json(self, code, body):
        payload = json.dumps(body).encode()
        try:
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError):
            pass  # Expected when simulating an ambiguous payment timeout.

    def do_GET(self):
        self.send_json(200, {'status': 'ok', 'mode': 'mock'}) if self.path == '/health' else self.send_json(404, {'message': 'Not found'})

    def do_POST(self):
        try:
            self.connection.settimeout(10)
            body = json.loads(self.read_body())
            code, response = self.server.store.process(self.path, body)
            if self.path == '/payments' and isinstance(body, dict) and body.get('scenario') == 'timeout' and code == 200:
                time.sleep(5)  # Authorization persisted before the caller's timeout.
            self.send_json(code, response)
        except (ValueError, TypeError):
            self.send_json(400, {'message': 'Invalid JSON request'})
        except sqlite3.Error:
            self.send_json(503, {'message': 'Provider storage unavailable'})


if __name__ == '__main__':
    server = ThreadingHTTPServer(('0.0.0.0', 8080), Handler)
    server.store = Store(os.getenv('PROVIDER_DB', '/data/providers.db'))
    server.serve_forever()
