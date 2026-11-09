import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from commercelens_ai.config import Settings
from commercelens_ai.providers import OpenAICompatibleModel, OpenAICompatibleEmbeddings, ProviderError


class Response:
    def __init__(self, value): self.value = value
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self, *args): return json.dumps(self.value).encode()


class SettingsTests(unittest.TestCase):
    def test_explicit_file_and_environment_precedence(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / '.env').write_text('NEBIUS_API_KEY=default\n')
            selected = root / 'chosen.env'
            selected.write_text('NEBIUS_API_KEY="selected"\nNEBIUS_BASE_URL=https://example.test/v1\nNEBIUS_EMBEDDING_MODEL=embed-choice\n')
            with patch.dict('os.environ', {'CHAT_MODEL': 'override'}, clear=True):
                settings = Settings.from_env(root, selected)
            self.assertEqual(settings.chat_api_key, 'selected')
            self.assertEqual(settings.chat_model, 'override')
            self.assertEqual(settings.embedding_model, 'embed-choice')
            self.assertNotIn('selected', repr(settings))

    def test_missing_explicit_file_is_error(self):
        with self.assertRaises(FileNotFoundError):
            Settings.from_env(Path('.'), Path('missing-explicit-config.env'))

    def test_environment_provider_family_does_not_borrow_other_file_family(self):
        with patch('pathlib.Path.exists', return_value=True), patch('pathlib.Path.read_text', return_value='NEBIUS_API_KEY=file-key\nNEBIUS_BASE_URL=https://nebius.example/v1\nNEBIUS_CHAT_MODEL=nebius-model\n'), patch.dict('os.environ', {'OPENAI_API_KEY': 'env-key'}, clear=True):
            settings = Settings.from_env(Path('.'))
        self.assertEqual(settings.chat_api_key, 'env-key')
        self.assertEqual(settings.chat_base_url, 'https://api.openai.com/v1')
        self.assertEqual(settings.chat_model, 'gpt-4.1-mini')
        self.assertEqual(settings.embedding_base_url, 'https://api.openai.com/v1')

    def test_explicit_channel_key_requires_matching_explicit_base(self):
        with patch('pathlib.Path.exists', return_value=False), patch.dict('os.environ', {'CHAT_API_KEY': 'unknown-provider'}, clear=True):
            with self.assertRaises(ValueError):
                Settings.from_env(Path('.'))

    def test_explicit_channel_pair_can_override_provider_family(self):
        with patch('pathlib.Path.exists', return_value=False), patch.dict('os.environ', {'NEBIUS_API_KEY': 'nebius', 'CHAT_API_KEY': 'custom', 'CHAT_BASE_URL': 'https://custom.example/v1', 'CHAT_MODEL': 'custom-model'}, clear=True):
            settings = Settings.from_env(Path('.'))
        self.assertEqual(settings.chat_api_key, 'custom')
        self.assertEqual(settings.chat_base_url, 'https://custom.example/v1')
        self.assertEqual(settings.embedding_api_key, 'nebius')


class ProviderTests(unittest.TestCase):
    def test_chat_returns_content_and_usage(self):
        response = {'choices': [{'message': {'content': 'Hello'}, 'finish_reason': 'stop'}], 'usage': {'total_tokens': 7}}
        with patch('urllib.request.OpenerDirector.open', return_value=Response(response)) as request:
            model = OpenAICompatibleModel('secret', 'https://example.test/v1', 'chat')
            self.assertEqual(model.complete([{'role': 'user', 'content': 'Hi'}]), 'Hello')
            self.assertEqual(model.usage['total_tokens'], 7)
            self.assertEqual(model.call_count, 1)
            sent = json.loads(request.call_args.args[0].data)
            self.assertEqual(sent['model'], 'chat')

    def test_truncation_is_failure(self):
        response = {'choices': [{'message': {'content': 'partial'}, 'finish_reason': 'length'}]}
        with patch('urllib.request.OpenerDirector.open', return_value=Response(response)):
            with self.assertRaises(ProviderError):
                OpenAICompatibleModel('secret', 'https://example.test/v1', 'chat').complete([])

    def test_transport_errors_are_sanitized(self):
        with patch('urllib.request.OpenerDirector.open', side_effect=OSError('secret-credential')):
            with self.assertRaises(ProviderError) as caught:
                OpenAICompatibleModel('secret', 'https://example.test/v1', 'chat').complete([])
        self.assertNotIn('secret', str(caught.exception))

    def test_embedding_order_and_actual_dimensions(self):
        response = {'data': [{'index': 1, 'embedding': [3, 4]}, {'index': 0, 'embedding': [1, 2]}]}
        with patch('urllib.request.OpenerDirector.open', return_value=Response(response)):
            model = OpenAICompatibleEmbeddings('key', 'https://example.test/v1', 'embed')
            self.assertIsNone(model.dimensions)
            self.assertEqual(model.embed(['first', 'second']), [[1, 2], [3, 4]])
            self.assertEqual(model.dimensions, 2)

    def test_malformed_embeddings_fail(self):
        for data in ([{'index': 0, 'embedding': [float('nan')]}],
                     [{'index': 0, 'embedding': [True]}],
                     [{'index': 1, 'embedding': [2]}], []):
            with self.subTest(data=data), patch('urllib.request.OpenerDirector.open', return_value=Response({'data': data})):
                with self.assertRaises(ProviderError):
                    OpenAICompatibleEmbeddings('key', 'https://example.test/v1', 'embed').embed(['x'])

    def test_insecure_remote_transport_rejected(self):
        with self.assertRaises(ValueError):
            OpenAICompatibleModel('key', 'http://example.test/v1', 'chat')


if __name__ == '__main__': unittest.main()
