"""Memory storage and semantic retrieval."""

import uuid
from typing import Any

import structlog
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from horizon.models import Memory
from horizon.services.embeddings import get_embeddings

log = structlog.get_logger(__name__)

# Below this cosine similarity a "match" is noise, not context.
DEFAULT_MIN_SIMILARITY = 0.7
# Two memories this close are treated as the same fact.
DEDUPE_SIMILARITY = 0.95


async def store_memory(
    db: AsyncSession,
    org_id: uuid.UUID,
    content: str,
    *,
    collection: str = "default",
    context_type: str | None = None,
    user_id: str | None = None,
    session_id: str | None = None,
    meta: dict[str, Any] | None = None,
    tags: list[str] | None = None,
    dedupe: bool = True,
) -> tuple[Memory, bool]:
    """
    Store a memory, embedding its content.

    Returns (memory, created). When `dedupe` is on and a near-identical memory
    already exists in the same collection, the existing row is returned with
    created=False instead of writing a duplicate.
    """
    embedding = await get_embeddings().embed_one(content)

    if dedupe:
        existing = await _find_duplicate(db, org_id, collection, embedding)
        if existing is not None:
            log.info("memory.deduped", org_id=str(org_id), memory_id=str(existing.id))
            return existing, False

    memory = Memory(
        org_id=org_id,
        content=content,
        embedding=embedding,
        collection=collection,
        context_type=context_type,
        user_id=user_id,
        session_id=session_id,
        meta=meta or {},
        tags=tags or [],
    )
    db.add(memory)
    await db.flush()
    return memory, True


async def _find_duplicate(
    db: AsyncSession,
    org_id: uuid.UUID,
    collection: str,
    embedding: list[float],
) -> Memory | None:
    distance = Memory.embedding.cosine_distance(embedding)
    stmt = (
        select(Memory)
        .where(
            Memory.org_id == org_id,
            Memory.collection == collection,
            distance < (1 - DEDUPE_SIMILARITY),
        )
        .order_by(distance)
        .limit(1)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def search_memories(
    db: AsyncSession,
    org_id: uuid.UUID,
    query: str,
    *,
    collection: str | None = None,
    user_id: str | None = None,
    session_id: str | None = None,
    tags: list[str] | None = None,
    limit: int = 10,
    min_similarity: float = DEFAULT_MIN_SIMILARITY,
) -> list[tuple[Memory, float]]:
    """Semantic search. Returns (memory, similarity) ordered most-similar first."""
    embedding = await get_embeddings().embed_one(query)
    distance = Memory.embedding.cosine_distance(embedding)
    similarity = (1 - distance).label("similarity")

    stmt = select(Memory, similarity).where(
        Memory.org_id == org_id,
        Memory.embedding.is_not(None),
        distance < (1 - min_similarity),
    )
    if collection is not None:
        stmt = stmt.where(Memory.collection == collection)
    if user_id is not None:
        stmt = stmt.where(Memory.user_id == user_id)
    if session_id is not None:
        stmt = stmt.where(Memory.session_id == session_id)
    if tags:
        stmt = stmt.where(Memory.tags.overlap(tags))

    stmt = stmt.order_by(distance).limit(limit)
    rows = (await db.execute(stmt)).all()

    if rows:
        await _touch(db, [m.id for m, _ in rows])

    return [(m, float(s)) for m, s in rows]


async def _touch(db: AsyncSession, ids: list[uuid.UUID]) -> None:
    """
    Record retrieval, so decay/pruning can act on real access patterns.

    synchronize_session=False matters: the default would expire the Memory
    instances we just loaded, and serializing them afterwards would trigger a
    lazy refresh outside the async context (MissingGreenlet). This counter is
    fire-and-forget, so the in-session copies going slightly stale is fine.
    """
    await db.execute(
        update(Memory)
        .where(Memory.id.in_(ids))
        .values(accessed_at=func.now(), access_count=Memory.access_count + 1)
        .execution_options(synchronize_session=False)
    )
