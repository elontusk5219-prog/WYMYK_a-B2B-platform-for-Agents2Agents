"""
A2A 协议兼容端点：接收 JSON-RPC 2.0 风格请求，转成内部会话/消息逻辑后以 A2A 格式回包。
参考: https://github.com/google/A2A
"""
from __future__ import annotations

import secrets
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Agent, Session, Message, Capability
from app.auth import require_agent

router = APIRouter(prefix="/a2a", tags=["a2a"])


def _jsonrpc_error(code: int, message: str, data: Optional[dict] = None):
    return {"jsonrpc": "2.0", "error": {"code": code, "message": message, "data": data}, "id": None}


@router.post("/v1")
async def a2a_endpoint(
    body: dict,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    """
    A2A 兼容入口：POST 体为 JSON-RPC 2.0 格式。
    method 支持: capabilities/list, session/create, message/send
    """
    req_id = body.get("id")
    method = body.get("method", "")
    params = body.get("params") or {}

    if method == "capabilities/list":
        from app.routers.capabilities import list_capabilities_public
        # 公开能力列表，无需鉴权逻辑，直接查库
        r = await db.execute(select(Capability))
        caps = r.scalars().all()
        result = [
            {"agent_id": c.agent_id, "type": c.type, "input_schema": c.input_schema, "price": c.price, "domains": c.domains}
            for c in caps
        ]
        return {"jsonrpc": "2.0", "result": result, "id": req_id}

    if method == "session/create":
        party_ids = params.get("party_ids") or [agent.id]
        if agent.id not in party_ids:
            party_ids = [agent.id] + list(party_ids)
        session_id = f"sess_{secrets.token_hex(12)}"
        sess = Session(id=session_id, parties=party_ids, status="active")
        db.add(sess)
        initial = params.get("initial_message")
        if initial:
            msg = Message(
                id=f"msg_{secrets.token_hex(12)}",
                session_id=session_id,
                sender=agent.id,
                payload=initial,
            )
            db.add(msg)
        await db.flush()
        return {"jsonrpc": "2.0", "result": {"session_id": session_id, "parties": party_ids, "status": "active"}, "id": req_id}

    if method == "message/send":
        session_id = params.get("session_id")
        payload = params.get("payload") or {}
        if not session_id:
            return _jsonrpc_error(-32602, "Missing session_id", {"id": req_id})
        r = await db.execute(select(Session).where(Session.id == session_id))
        sess = r.scalar_one_or_none()
        if not sess or agent.id not in sess.parties:
            return _jsonrpc_error(-32001, "Session not found or access denied", {"id": req_id})
        msg_id = f"msg_{secrets.token_hex(12)}"
        msg = Message(id=msg_id, session_id=session_id, sender=agent.id, payload=payload)
        db.add(msg)
        await db.flush()
        return {"jsonrpc": "2.0", "result": {"message_id": msg_id, "session_id": session_id}, "id": req_id}

    return _jsonrpc_error(-32601, f"Method not found: {method}", {"id": req_id})
