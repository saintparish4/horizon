"""Memory CRUD and semantic search."""

import uuid

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import delete, select

from horizon.api.deps import CurrentOrg, DbSession
from horizon.models import Memory
from horizon.schemas.memory import (
    MemoryCreate,
    MemoryCreated,
    MemoryOut,
    MemoryUpdate,
    SearchHit,
    SearchRequest,
    SearchResponse,
)
from horizon.services import memory_service
from horizon.services.embeddings import get_embeddings

router = APIRouter(prefix="/v1/memories", tags=["memories"])


@router.post("", response_model=MemoryCreated, status_code=status.HTTP_201_CREATED)
async def create_memory(payload: MemoryCreate, org: CurrentOrg, db: DbSession) -> MemoryCreated:
    memory, created = await memory_service.store_memory(
        db,
        org.id,
        payload.content,
        collection=payload.collection,
        context_type=payload.context_type,
        user_id=payload.user_id,
        session_id=payload.session_id,
        meta=payload.metadata,
        tags=payload.tags,
        dedupe=payload.dedupe,
    )
    return MemoryCreated(memory=MemoryOut.model_validate(memory), created=created)


@router.post("/search", response_model=SearchResponse)
async def search(payload: SearchRequest, org: CurrentOrg, db: DbSession) -> SearchResponse:
    results = await memory_service.search_memories(
        db,
        org.id,
        payload.query,
        collection=payload.collection,
        user_id=payload.user_id,
        session_id=payload.session_id,
        tags=payload.tags or None,
        limit=payload.limit,
        min_similarity=payload.min_similarity,
    )
    return SearchResponse(
        query=payload.query,
        hits=[SearchHit(memory=MemoryOut.model_validate(m), similarity=s) for m, s in results],
    )


@router.get("", response_model=list[MemoryOut])
async def list_memories(
    org: CurrentOrg,
    db: DbSession,
    collection: str | None = None,
    user_id: str | None = None,
    session_id: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[MemoryOut]:
    stmt = select(Memory).where(Memory.org_id == org.id)
    if collection is not None:
        stmt = stmt.where(Memory.collection == collection)
    if user_id is not None:
        stmt = stmt.where(Memory.user_id == user_id)
    if session_id is not None:
        stmt = stmt.where(Memory.session_id == session_id)

    stmt = stmt.order_by(Memory.created_at.desc()).limit(limit).offset(offset)
    rows = (await db.execute(stmt)).scalars().all()
    return [MemoryOut.model_validate(m) for m in rows]


@router.get("/{memory_id}", response_model=MemoryOut)
async def get_memory(memory_id: uuid.UUID, org: CurrentOrg, db: DbSession) -> MemoryOut:
    return MemoryOut.model_validate(await _owned_memory(db, org.id, memory_id))


@router.patch("/{memory_id}", response_model=MemoryOut)
async def update_memory(
    memory_id: uuid.UUID, payload: MemoryUpdate, org: CurrentOrg, db: DbSession
) -> MemoryOut:
    memory = await _owned_memory(db, org.id, memory_id)

    if payload.content is not None and payload.content != memory.content:
        memory.content = payload.content
        # Content changed, so the old vector is stale — re-embed.
        memory.embedding = await get_embeddings().embed_one(payload.content)
    if payload.metadata is not None:
        memory.meta = payload.metadata
    if payload.tags is not None:
        memory.tags = payload.tags

    await db.flush()
    # `updated_at` is computed server-side via onupdate, so SQLAlchemy expires
    # it after the UPDATE. Refresh to read it back while the session is open —
    # FastAPI validates the response only after dependency teardown, and a
    # detached lazy load there fails with MissingGreenlet.
    await db.refresh(memory)
    return MemoryOut.model_validate(memory)


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(memory_id: uuid.UUID, org: CurrentOrg, db: DbSession) -> None:
    await _owned_memory(db, org.id, memory_id)
    await db.execute(delete(Memory).where(Memory.id == memory_id, Memory.org_id == org.id))


async def _owned_memory(db: DbSession, org_id: uuid.UUID, memory_id: uuid.UUID) -> Memory:
    """Fetch scoped to the caller's org — never leak another tenant's row."""
    stmt = select(Memory).where(Memory.id == memory_id, Memory.org_id == org_id)
    memory = (await db.execute(stmt)).scalar_one_or_none()
    if memory is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Memory not found")
    return memory
