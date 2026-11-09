"""Explicit configuration loading. Never searches neighboring projects for secrets."""
from dataclasses import dataclass, field
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    chat_api_key: str = field(repr=False)
    chat_base_url: str
    chat_model: str
    embedding_api_key: str = field(repr=False)
    embedding_base_url: str
    embedding_model: str
    pinecone_api_key: str = field(repr=False)
    pinecone_host: str
    pinecone_index: str
    pinecone_namespace: str
    langsmith_api_key: str = field(repr=False)
    langsmith_project: str

    @classmethod
    def from_env(cls, root: Path, env_file: Path | None = None):
        selected = Path(env_file) if env_file is not None else Path(root) / '.env'
        values = {}
        if selected.exists():
            for line in selected.read_text(encoding='utf-8-sig').splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('export '):
                    line = line[7:].lstrip()
                if '=' not in line:
                    continue
                name, value = line.split('=', 1)
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                    value = value[1:-1]
                else:
                    value = value.split(' #', 1)[0].rstrip()
                values[name.strip()] = value
        elif env_file is not None:
            raise FileNotFoundError('The explicitly selected environment file does not exist.')
        # Alias resolution also prioritizes process environment over file aliases.
        def get(*keys, default=''):
            for source in (os.environ, values):
                for key in keys:
                    if source.get(key):
                        return source[key]
            return default

        # Choose one provider family as a unit. An environment provider key
        # selects its own URL/model defaults, never another family's file values.
        family = next((name for source in (os.environ, values)
                       for name in ('NEBIUS', 'OPENAI') if source.get(name + '_API_KEY')), 'NEBIUS')
        openai = family == 'OPENAI'
        default_base = 'https://api.openai.com/v1' if openai else 'https://api.tokenfactory.nebius.com/v1'

        def channel(prefix, default_model):
            explicit_key = get(prefix + '_API_KEY')
            explicit_base = get(prefix + '_BASE_URL')
            if explicit_key and not explicit_base:
                raise ValueError(f'{prefix}_BASE_URL must be supplied with {prefix}_API_KEY to identify the intended provider.')
            return (
                explicit_key or get(family + '_API_KEY'),
                explicit_base or get(family + '_BASE_URL', default=default_base),
                get(prefix + '_MODEL', family + ('_CHAT_MODEL' if prefix == 'CHAT' else '_EMBEDDING_MODEL'), default=default_model))

        chat_key, chat_base, chat_model = channel('CHAT', 'gpt-4.1-mini' if openai else 'Qwen/Qwen3-235B-A22B-Instruct-2507')
        embedding_key, embedding_base, embedding_model = channel('EMBEDDING', 'text-embedding-3-small' if openai else 'Qwen/Qwen3-Embedding-8B')
        return cls(
            chat_api_key=chat_key, chat_base_url=chat_base, chat_model=chat_model,
            embedding_api_key=embedding_key, embedding_base_url=embedding_base, embedding_model=embedding_model,
            pinecone_api_key=get('PINECONE_API_KEY'), pinecone_host=get('PINECONE_HOST'),
            pinecone_index=get('PINECONE_INDEX', default='commercelens-docs'),
            pinecone_namespace=get('PINECONE_NAMESPACE', default='commercelens-docs-v1'),
            langsmith_api_key=get('LANGSMITH_API_KEY', 'LANGCHAIN_API_KEY'),
            langsmith_project=get('LANGSMITH_PROJECT', 'LANGCHAIN_PROJECT', default='commercelens-documentation-assistant'))
