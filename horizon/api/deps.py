"""Shared FastAPI dependencies: auth and request context."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from horizon.config.database import get_db
from horizon.config.settings import Settings, get_settings
from horizon.models import APIKey, Organization
from horizon.services.api_keys import hash_key

DbSession = Annotated[AsyncSession, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]


async def get_current_org(
    db: DbSession,
    settings: AppSettings,
    authorization: Annotated[str | None, Header()] = None,
    x_api_key: Annotated[str | None, Header()] = None,
) -> Organization:
    """
    Resolve the calling organization from its API key.

    Accepts `Authorization: Bearer <key>` or `X-API-Key: <key>`. The key is
    matched by hash — the plaintext is never stored, so lookup is a single
    indexed equality check.
    """
    raw = x_api_key
    if not raw and authorization and authorization.lower().startswith("bearer "):
        raw = authorization[7:].strip()

    if not raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Send 'Authorization: Bearer <key>' or 'X-API-Key: <key>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    stmt = (
        select(APIKey)
        .where(APIKey.key_hash == hash_key(raw, settings.api_key_pepper))
        .options(selectinload(APIKey.organization))
    )
    api_key = (await db.execute(stmt)).scalar_one_or_none()

    if api_key is None or not api_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    await db.execute(update(APIKey).where(APIKey.id == api_key.id).values(last_used_at=func.now()))
    return api_key.organization


CurrentOrg = Annotated[Organization, Depends(get_current_org)]
