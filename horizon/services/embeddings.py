"""Embedding generation. Provider-agnostic behind a small protocol."""

from typing import Protocol

import structlog
from openai import AsyncOpenAI

from horizon.config.settings import get_settings

log = structlog.get_logger(__name__)


class EmbeddingProvider(Protocol):
    """Swap-in point for Cohere/Voyage/local models without touching callers."""

    async def embed(self, texts: list[str]) -> list[list[float]]: ...

    async def embed_one(self, text: str) -> list[float]: ...


class OpenAIEmbeddings:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        settings = get_settings()
        key = api_key or settings.openai_api_key
        if not key:
            raise ValueError("OPENAI_API_KEY is not set")
        self._client = AsyncOpenAI(api_key=key)
        self._model = model or settings.embedding_model
        self._batch_size = settings.embedding_batch_size

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of texts, batching to stay under the provider limit."""
        cleaned = [t.strip() for t in texts]
        if any(not t for t in cleaned):
            raise ValueError("Cannot embed empty text")

        out: list[list[float]] = []
        for i in range(0, len(cleaned), self._batch_size):
            batch = cleaned[i : i + self._batch_size]
            resp = await self._client.embeddings.create(model=self._model, input=batch)
            # The API may return items out of order; sort by index before use.
            out.extend(item.embedding for item in sorted(resp.data, key=lambda d: d.index))

        log.debug("embedded", count=len(out), model=self._model)
        return out

    async def embed_one(self, text: str) -> list[float]:
        return (await self.embed([text]))[0]


class DeterministicEmbeddings:
    """
    Offline embeddings: a hashed bag-of-words, L2-normalized.

    Not a semantic model — it only captures lexical overlap. That is enough for
    tests and for the routing benchmark, where the point is to exercise the real
    pgvector/HNSW/SQL path without a network call or an API bill. Text sharing
    vocabulary lands close together, which is the property those callers need.

    Deterministic across processes: uses blake2b, not Python's randomized hash.
    """

    def __init__(self, dimensions: int | None = None) -> None:
        self._dim = dimensions or get_settings().embedding_dimensions

    def _vector(self, text: str) -> list[float]:
        import hashlib
        import re

        vec = [0.0] * self._dim
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        for token in tokens:
            digest = hashlib.blake2b(token.encode(), digest_size=8).digest()
            idx = int.from_bytes(digest[:4], "big") % self._dim
            sign = 1.0 if digest[4] & 1 else -1.0
            vec[idx] += sign

        norm = sum(v * v for v in vec) ** 0.5
        if norm == 0:
            # An empty/symbol-only string still needs a valid unit vector.
            vec[0] = 1.0
            return vec
        return [v / norm for v in vec]

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(t) for t in texts]

    async def embed_one(self, text: str) -> list[float]:
        return self._vector(text)


_provider: EmbeddingProvider | None = None


def get_embeddings() -> EmbeddingProvider:
    """Current provider. Defaults to OpenAI; overridden via set_embeddings()."""
    global _provider
    if _provider is None:
        _provider = OpenAIEmbeddings()
    return _provider


def set_embeddings(provider: EmbeddingProvider | None) -> None:
    """Inject a provider (tests, benchmarks). Pass None to reset to default."""
    global _provider
    _provider = provider
