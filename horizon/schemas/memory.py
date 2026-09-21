"""Request/response models for the memory API."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class MemoryCreate(BaseModel):
    content: str = Field(min_length=1, max_length=100_000)
    collection: str = Field(default="default", max_length=128)
    context_type: str | None = Field(default=None, max_length=50)
    user_id: str | None = Field(default=None, max_length=255)
    session_id: str | None = Field(default=None, max_length=255)
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    dedupe: bool = True


class MemoryUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1, max_length=100_000)
    metadata: dict[str, Any] | None = None
    tags: list[str] | None = None


class MemoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    content: str
    collection: str
    context_type: str | None
    user_id: str | None
    session_id: str | None
    metadata: dict[str, Any] = Field(validation_alias="meta")
    tags: list[str]
    created_at: datetime
    updated_at: datetime
    access_count: int


class MemoryCreated(BaseModel):
    memory: MemoryOut
    created: bool = Field(description="False when an existing near-duplicate was returned.")


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    collection: str | None = None
    user_id: str | None = None
    session_id: str | None = None
    tags: list[str] = Field(default_factory=list)
    limit: int = Field(default=10, ge=1, le=100)
    min_similarity: float = Field(default=0.7, ge=0.0, le=1.0)


class SearchHit(BaseModel):
    memory: MemoryOut
    similarity: float


class SearchResponse(BaseModel):
    query: str
    hits: list[SearchHit]
