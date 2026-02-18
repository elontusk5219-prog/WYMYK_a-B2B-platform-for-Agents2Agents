import secrets
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Agent
from app.schemas import AgentCreate, AgentResponse
from app.auth import require_agent, generate_api_key, hash_api_key

router = APIRouter(prefix="/v1/agents", tags=["agents"])


@router.post("/register", response_model=AgentResponse)
async def register_agent(
    body: AgentCreate,
    db: AsyncSession = Depends(get_db),
):
    """注册新 Agent，返回 api_key（仅此一次）。"""
    raw_key = generate_api_key()
    agent_id = f"agent_{secrets.token_hex(12)}"
    did = body.did or f"did:wymyk:agent:{agent_id}"
    agent = Agent(
        id=agent_id,
        did=did,
        name=body.name,
        type=body.type,
        api_key_hash=hash_api_key(raw_key),
    )
    db.add(agent)
    await db.flush()
    await db.refresh(agent)
    return AgentResponse(
        id=agent.id,
        did=agent.did,
        name=agent.name,
        type=agent.type,
        created_at=agent.created_at,
        api_key=raw_key,
    )


@router.get("/me")
async def me(
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    """当前认证 Agent 信息（不含 api_key）。"""
    return {
        "id": agent.id,
        "did": agent.did,
        "name": agent.name,
        "type": agent.type,
        "created_at": agent.created_at.isoformat(),
    }


@router.get("/{agent_id}/public")
async def get_agent_public(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
):
    """公开信息，用于社区帖子等展示作者名。"""
    from sqlalchemy import select
    r = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = r.scalar_one_or_none()
    if not agent:
        from fastapi import HTTPException
        raise HTTPException(404, "Agent not found")
    return {"id": agent.id, "name": agent.name, "type": agent.type}
