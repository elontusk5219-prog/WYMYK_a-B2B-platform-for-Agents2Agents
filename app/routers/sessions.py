import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Agent, Session, Message
from app.schemas import SessionCreate, SessionResponse, MessageCreate, MessageResponse
from app.auth import require_agent

router = APIRouter(prefix="/v1/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse)
async def create_session(
    body: SessionCreate,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    session_id = f"sess_{secrets.token_hex(12)}"
    parties = body.party_ids
    if agent.id not in parties:
        parties = [agent.id] + parties
    sess = Session(id=session_id, parties=parties, status="active")
    db.add(sess)
    await db.flush()
    if body.initial_message:
        msg_id = f"msg_{secrets.token_hex(12)}"
        msg = Message(
            id=msg_id,
            session_id=session_id,
            sender=agent.id,
            payload=body.initial_message,
        )
        db.add(msg)
    await db.refresh(sess)
    return SessionResponse(
        id=sess.id,
        parties=sess.parties,
        status=sess.status,
        created_at=sess.created_at,
    )


@router.get("", response_model=list[SessionResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    # 只返回当前 agent 参与的会话（parties 含 agent.id）
    r = await db.execute(
        select(Session).where(Session.parties.contains([agent.id]))
    )
    sessions = r.scalars().all()
    return [
        SessionResponse(
            id=s.id,
            parties=s.parties,
            status=s.status,
            created_at=s.created_at,
        )
        for s in sessions
    ]


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    r = await db.execute(select(Session).where(Session.id == session_id))
    sess = r.scalar_one_or_none()
    if not sess:
        raise HTTPException(404, "Session not found")
    if agent.id not in sess.parties:
        raise HTTPException(403, "Not a party of this session")
    return SessionResponse(
        id=sess.id,
        parties=sess.parties,
        status=sess.status,
        created_at=sess.created_at,
    )


@router.post("/{session_id}/messages", response_model=MessageResponse)
async def send_message(
    session_id: str,
    body: MessageCreate,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    r = await db.execute(select(Session).where(Session.id == session_id))
    sess = r.scalar_one_or_none()
    if not sess:
        raise HTTPException(404, "Session not found")
    if agent.id not in sess.parties:
        raise HTTPException(403, "Not a party of this session")
    msg_id = f"msg_{secrets.token_hex(12)}"
    msg = Message(
        id=msg_id,
        session_id=session_id,
        sender=agent.id,
        payload=body.payload,
    )
    db.add(msg)
    await db.flush()
    await db.refresh(msg)
    return MessageResponse(
        id=msg.id,
        session_id=msg.session_id,
        sender=msg.sender,
        payload=msg.payload,
        created_at=msg.created_at,
    )


@router.get("/{session_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    r = await db.execute(select(Session).where(Session.id == session_id))
    sess = r.scalar_one_or_none()
    if not sess:
        raise HTTPException(404, "Session not found")
    if agent.id not in sess.parties:
        raise HTTPException(403, "Not a party of this session")
    r = await db.execute(select(Message).where(Message.session_id == session_id).order_by(Message.created_at))
    msgs = r.scalars().all()
    return [
        MessageResponse(
            id=m.id,
            session_id=m.session_id,
            sender=m.sender,
            payload=m.payload,
            created_at=m.created_at,
        )
        for m in msgs
    ]
