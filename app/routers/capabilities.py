from __future__ import annotations

import secrets
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, cast, String
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Agent, Capability
from app.schemas import CapabilityCreate, CapabilityUpdate, CapabilityResponse, CapabilityPublic
from app.auth import require_agent

router_private = APIRouter(prefix="/v1/agents", tags=["capabilities"])
router_public = APIRouter(prefix="/v1", tags=["capabilities-public"])


@router_private.post("/{agent_id}/capabilities", response_model=CapabilityResponse)
async def create_capability(
    agent_id: str,
    body: CapabilityCreate,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    if agent.id != agent_id:
        from fastapi import HTTPException
        raise HTTPException(403, "Cannot create capability for another agent")
    cap_id = f"cap_{secrets.token_hex(12)}"
    cap = Capability(
        id=cap_id,
        agent_id=agent_id,
        type=body.type,
        input_schema=body.input_schema,
        price=body.price,
        domains=body.domains,
    )
    db.add(cap)
    await db.flush()
    await db.refresh(cap)
    return CapabilityResponse(
        id=cap.id,
        agent_id=cap.agent_id,
        type=cap.type,
        input_schema=cap.input_schema,
        price=cap.price,
        domains=cap.domains,
        created_at=cap.created_at,
    )


@router_private.get("/{agent_id}/capabilities", response_model=list[CapabilityResponse])
async def list_my_capabilities(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    if agent.id != agent_id:
        from fastapi import HTTPException
        raise HTTPException(403, "Forbidden")
    r = await db.execute(select(Capability).where(Capability.agent_id == agent_id))
    caps = r.scalars().all()
    return [
        CapabilityResponse(
            id=c.id,
            agent_id=c.agent_id,
            type=c.type,
            input_schema=c.input_schema,
            price=c.price,
            domains=c.domains,
            created_at=c.created_at,
        )
        for c in caps
    ]


@router_private.patch("/{agent_id}/capabilities/{cap_id}", response_model=CapabilityResponse)
async def update_capability(
    agent_id: str,
    cap_id: str,
    body: CapabilityUpdate,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    if agent.id != agent_id:
        from fastapi import HTTPException
        raise HTTPException(403, "Forbidden")
    r = await db.execute(
        select(Capability).where(Capability.id == cap_id, Capability.agent_id == agent_id)
    )
    cap = r.scalar_one_or_none()
    if not cap:
        from fastapi import HTTPException
        raise HTTPException(404, "Capability not found")
    if body.input_schema is not None:
        cap.input_schema = body.input_schema
    if body.price is not None:
        cap.price = body.price
    if body.domains is not None:
        cap.domains = body.domains
    await db.flush()
    await db.refresh(cap)
    return CapabilityResponse(
        id=cap.id,
        agent_id=cap.agent_id,
        type=cap.type,
        input_schema=cap.input_schema,
        price=cap.price,
        domains=cap.domains,
        created_at=cap.created_at,
    )


@router_private.delete("/{agent_id}/capabilities/{cap_id}")
async def delete_capability(
    agent_id: str,
    cap_id: str,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    if agent.id != agent_id:
        from fastapi import HTTPException
        raise HTTPException(403, "Forbidden")
    r = await db.execute(
        select(Capability).where(Capability.id == cap_id, Capability.agent_id == agent_id)
    )
    cap = r.scalar_one_or_none()
    if not cap:
        from fastapi import HTTPException
        raise HTTPException(404, "Capability not found")
    await db.delete(cap)
    return {"ok": True}


# 公开能力目录（无需鉴权，便于发现）
@router_public.get("/capabilities", response_model=list[CapabilityPublic])
async def list_capabilities_public(
    type: Optional[str] = Query(None, description="能力类型，如 ip_evaluation"),
    domain: Optional[str] = Query(None, description="领域关键词，如 悬疑"),
    db: AsyncSession = Depends(get_db),
):
    q = select(Capability)
    if type:
        q = q.where(Capability.type == type)
    if domain:
        # 按 domains JSON 文本包含关键词过滤
        q = q.where(cast(Capability.domains, String).contains(domain))
    r = await db.execute(q)
    caps = r.scalars().all()
    return [
        CapabilityPublic(
            agent_id=c.agent_id,
            type=c.type,
            input_schema=c.input_schema,
            price=c.price,
            domains=c.domains,
        )
        for c in caps
    ]
