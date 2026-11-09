"""Small OpenAI-compatible HTTP clients with bounded, sanitized failures."""
import json
import math
import threading
import urllib.request
from urllib.parse import urlsplit


class ProviderError(RuntimeError):
    pass


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ProviderError('Provider redirects are not accepted.')


class _Client:
    def __init__(self, api_key, base_url, model, timeout=60):
        parsed = urlsplit(base_url)
        if parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in ('127.0.0.1', 'localhost', '::1')):
            raise ValueError('Provider URL must use HTTPS (HTTP is allowed only on loopback).')
        if not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('Provider URL must be a base URL without credentials, query, or fragment.')
        if not api_key or not model:
            raise ValueError('Provider API key and model must be configured.')
        self._api_key = api_key
        self.base_url, self.model = base_url.rstrip('/'), model
        self.timeout = min(120, max(1, timeout))
        self._stats = threading.local()

    @property
    def usage(self):
        return dict(getattr(self._stats, 'usage', {}))

    @property
    def call_count(self):
        return getattr(self._stats, 'call_count', 0)

    def _post(self, endpoint, payload):
        self._stats.call_count = self.call_count + 1
        request = urllib.request.Request(self.base_url + endpoint,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Authorization': 'Bearer ' + self._api_key, 'Content-Type': 'application/json'}, method='POST')
        try:
            with urllib.request.build_opener(_NoRedirect()).open(request, timeout=self.timeout) as response:
                raw = response.read(16 * 1024 * 1024 + 1)
            if len(raw) > 16 * 1024 * 1024:
                raise ValueError('response limit')
            result = json.loads(raw)
            if not isinstance(result, dict):
                raise ValueError('response shape')
            usage = result.get('usage', {})
            if isinstance(usage, dict):
                self._stats.usage = {k: v for k, v in usage.items() if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)}
            return result
        except Exception:
            raise ProviderError('Provider request failed. Check the endpoint, credentials, model, and service availability.') from None


class OpenAICompatibleModel(_Client):
    def __init__(self, api_key, base_url, model, max_tokens=5000, timeout=60):
        super().__init__(api_key, base_url, model, timeout)
        self.max_tokens = max(1, min(16000, max_tokens))

    def complete(self, messages):
        data = self._post('/chat/completions', {'model': self.model, 'messages': messages,
                          'max_tokens': self.max_tokens, 'temperature': 0})
        try:
            choice = data['choices'][0]
            content = choice['message']['content']
            if choice.get('finish_reason') == 'length':
                raise ValueError('truncated')
            if not isinstance(content, str) or not content.strip():
                raise ValueError('empty')
            return content
        except (KeyError, IndexError, TypeError, ValueError):
            raise ProviderError('Provider returned an empty, malformed, or truncated answer.') from None


class OpenAICompatibleEmbeddings(_Client):
    def __init__(self, api_key, base_url, model, timeout=60):
        super().__init__(api_key, base_url, model, timeout)
        self.dimensions = None

    def embed(self, texts):
        if not texts:
            return []
        if not isinstance(texts, list) or any(not isinstance(t, str) or not t.strip() for t in texts):
            raise ValueError('Embeddings require a list of nonempty text strings.')
        data = self._post('/embeddings', {'model': self.model, 'input': texts})
        try:
            rows = data['data']
            if len(rows) != len(texts) or {r['index'] for r in rows} != set(range(len(texts))):
                raise ValueError('count/index mismatch')
            vectors = [r['embedding'] for r in sorted(rows, key=lambda r: r['index'])]
            dims = len(vectors[0])
            if not dims or (self.dimensions is not None and dims != self.dimensions):
                raise ValueError('dimension mismatch')
            for vector in vectors:
                if not isinstance(vector, list) or len(vector) != dims or any(
                    isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in vector):
                    raise ValueError('invalid vector')
            self.dimensions = dims
            return vectors
        except (KeyError, IndexError, TypeError, ValueError):
            raise ProviderError('Embedding provider returned invalid counts, ordering, dimensions, or numeric values.') from None
