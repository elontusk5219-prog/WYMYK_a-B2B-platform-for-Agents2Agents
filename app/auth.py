from __future__ import annotations

import hashlib
import secrets
from typing import Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.models import Agent

api_key_header = APIKeyHeader(name=settings.api_key_header, auto_error=False)


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


def generate_api_key() -> str:
    return f"sk_{secrets.token_urlsafe(32)}"


async def get_agent_by_api_key(
    db: AsyncSession,
    api_key: str,
) -> Optional[Agent]:
    if not api_key:
        return None
    h = hash_api_key(api_key)
    r = await db.execute(select(Agent).where(Agent.api_key_hash == h))
    return r.scalar_one_or_none()


async def require_agent(
    db: AsyncSession = Depends(get_db),
    api_key: str = Security(api_key_header),
) -> Agent:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key. Use header: " + settings.api_key_header,
        )
    agent = await get_agent_by_api_key(db, api_key)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return agent
