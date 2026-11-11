"""Small loopback chat server; no repository execution or index mutations."""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


def create_server(assistant, host='127.0.0.1', port=8090):
    static = Path(__file__).parent / 'static'
    gate = threading.BoundedSemaphore(2)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass  # Never log questions, provider responses, or credentials.

        def send(self, status, data, content_type='application/json; charset=utf-8'):
            body = data if isinstance(data, bytes) else json.dumps(data).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def trusted_host(self):
            expected = {host, 'localhost', '127.0.0.1', '::1'}
            try:
                parsed = urlsplit('http://' + self.headers.get('Host', ''))
                return parsed.hostname in expected and parsed.port == self.server.server_port
            except ValueError:
                return False

        def do_GET(self):
            if not self.trusted_host():
                return self.send(403, {'error': 'Untrusted host.'})
            path = urlsplit(self.path).path
            if path == '/health':
                return self.send(200, {'status': 'ok'})
            assets = {'/': ('index.html', 'text/html; charset=utf-8'),
                      '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                      '/style.css': ('style.css', 'text/css; charset=utf-8')}
            if path not in assets:
                return self.send(404, {'error': 'Not found.'})
            filename, mime = assets[path]
            self.send(200, (static / filename).read_bytes(), mime)

        def do_POST(self):
            if not self.trusted_host():
                return self.send(403, {'error': 'Untrusted host.'})
            origin = self.headers.get('Origin')
            if origin and origin != 'http://' + self.headers.get('Host', ''):
                return self.send(403, {'error': 'Cross-origin requests are not accepted.'})
            if self.path not in ('/api/chat','/api/replan'):
                return self.send(404, {'error': 'Not found.'})
            try:
                size = int(self.headers.get('Content-Length', '0'))
            except ValueError:
                return self.send(400, {'error': 'Invalid request length.'})
            limit=262144 if self.path=='/api/replan' else 32768
            if size < 1 or size > limit:
                return self.send(413, {'error': 'Request exceeds the allowed size.'})
            self.connection.settimeout(15)
            try:
                payload = json.loads(self.rfile.read(size))
                if not isinstance(payload, dict):
                    raise ValueError()
                if self.path=='/api/replan':
                    from .engine import Assistant
                    context=Assistant.validate_replan(payload.get('original_request'),payload.get('previous_plan'),payload.get('selected_alternative'),payload.get('instruction',''))
                else:
                    question, mode = payload.get('question'), payload.get('mode', 'ask')
                    if not isinstance(question, str) or not question.strip() or len(question) > 8000 or mode not in ('ask', 'plan'):
                        raise ValueError()
            except (ValueError, OSError):
                return self.send(400, {'error': 'Provide a question of 1 to 8000 characters and mode ask or plan.'})
            if not gate.acquire(blocking=False):
                return self.send(429, {'error': 'Assistant is busy. Try again shortly.'})
            try:
                result = assistant.replan(**context) if self.path=='/api/replan' else assistant.run(question, mode=mode)
                self.send(200, result)
            except Exception:
                self.send(500, {'error': 'The assistant could not complete the request.'})
            finally:
                gate.release()

    return ThreadingHTTPServer((host, port), Handler)


def serve(assistant, host='127.0.0.1', port=8090):
    server = create_server(assistant, host, port)
    print(f'CommerceLens documentation assistant: http://{host}:{server.server_port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
