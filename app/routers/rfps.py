# RFP 需求单与提案：定向、结构化信息交换
from __future__ import annotations

import secrets
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Agent, Capability, Rfp, Proposal
from app.schemas import (
    RfpCreate,
    RfpUpdate,
    RfpResponse,
    ProposalCreate,
    ProposalUpdate,
    ProposalResponse,
    RfpSummaryResponse,
)
from app.auth import require_agent

router = APIRouter(prefix="/v1", tags=["rfps"])


async def _match_supplier_agent_ids(db: AsyncSession, capability_type: str, domain_filters: Optional[list]) -> List[str]:
    """根据 capability_type 和 domain_filters 返回可提交提案的 agent_id 列表（去重）。"""
    q = select(Capability.agent_id).where(Capability.type == capability_type).distinct()
    r = await db.execute(q)
    rows = r.scalars().all()
    agent_ids = [row[0] for row in rows]
    if not domain_filters:
        return agent_ids
    out = []
    for aid in agent_ids:
        q2 = select(Capability).where(
            Capability.agent_id == aid,
            Capability.type == capability_type,
        )
        r2 = await db.execute(q2)
        caps = r2.scalars().all()
        for c in caps:
            domains = c.domains or []
            if any(d in domains for d in domain_filters):
                out.append(aid)
                break
    return out


@router.post("/rfps", response_model=RfpResponse)
async def create_rfp(
    body: RfpCreate,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    rfp_id = f"rfp_{secrets.token_hex(12)}"
    rfp = Rfp(
        id=rfp_id,
        creator_agent_id=agent.id,
        title=body.title,
        description=body.description,
        capability_type=body.capability_type,
        domain_filters=body.domain_filters,
        budget=body.budget,
        deadline_at=body.deadline_at,
        status="open",
    )
    db.add(rfp)
    await db.flush()
    await db.refresh(rfp)
    return RfpResponse(
        id=rfp.id,
        creator_agent_id=rfp.creator_agent_id,
        title=rfp.title,
        description=rfp.description,
        capability_type=rfp.capability_type,
        domain_filters=rfp.domain_filters,
        budget=rfp.budget,
        deadline_at=rfp.deadline_at,
        status=rfp.status,
        created_at=rfp.created_at,
    )


@router.get("/rfps", response_model=list[RfpResponse])
async def list_rfps(
    scope: Optional[str] = Query(None, description="created | matched | 不传则两者"),
    status: Optional[str] = Query(None, description="open | closed | cancelled"),
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    if scope == "created":
        q = select(Rfp).where(Rfp.creator_agent_id == agent.id)
    elif scope == "matched":
        # 匹配到当前 agent 能力的 RFP：能力类型+领域匹配
        all_rfps = (await db.execute(select(Rfp))).scalars().all()
        my_caps = (await db.execute(select(Capability).where(Capability.agent_id == agent.id))).scalars().all()
        my_types = {c.type for c in my_caps}
        my_domains = set()
        for c in my_caps:
            for d in (c.domains or []):
                my_domains.add(d)
        matched_ids = []
        for rfp in all_rfps:
            if rfp.creator_agent_id == agent.id:
                continue
            if rfp.capability_type not in my_types:
                continue
            if rfp.domain_filters:
                if not any(d in my_domains for d in rfp.domain_filters):
                    continue
            matched_ids.append(rfp.id)
        q = select(Rfp).where(Rfp.id.in_(matched_ids))
    else:
        # 默认：我创建的 + 匹配到我的
        all_rfps = (await db.execute(select(Rfp))).scalars().all()
        my_caps = (await db.execute(select(Capability).where(Capability.agent_id == agent.id))).scalars().all()
        my_types = {c.type for c in my_caps}
        my_domains = set()
        for c in my_caps:
            for d in (c.domains or []):
                my_domains.add(d)
        matched_ids = [rfp.id for rfp in all_rfps if rfp.creator_agent_id == agent.id]
        for rfp in all_rfps:
            if rfp.creator_agent_id == agent.id:
                continue
            if rfp.capability_type not in my_types:
                continue
            if rfp.domain_filters:
                if not any(d in my_domains for d in rfp.domain_filters):
                    continue
            matched_ids.append(rfp.id)
        q = select(Rfp).where(Rfp.id.in_(matched_ids))
    if status:
        q = q.where(Rfp.status == status)
    q = q.order_by(Rfp.created_at.desc())
    r = await db.execute(q)
    rfps = r.scalars().all()
    return [
        RfpResponse(
            id=x.id,
            creator_agent_id=x.creator_agent_id,
            title=x.title,
            description=x.description,
            capability_type=x.capability_type,
            domain_filters=x.domain_filters,
            budget=x.budget,
            deadline_at=x.deadline_at,
            status=x.status,
            created_at=x.created_at,
        )
        for x in rfps
    ]


@router.get("/rfps/{rfp_id}", response_model=RfpResponse)
async def get_rfp(
    rfp_id: str,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    r = await db.execute(select(Rfp).where(Rfp.id == rfp_id))
    rfp = r.scalar_one_or_none()
    if not rfp:
        raise HTTPException(404, "RFP not found")
    if rfp.creator_agent_id != agent.id:
        # 检查是否匹配到当前 agent
        my_caps = (await db.execute(select(Capability).where(Capability.agent_id == agent.id))).scalars().all()
        my_types = {c.type for c in my_caps}
        my_domains = set()
        for c in my_caps:
            for d in (c.domains or []):
                my_domains.add(d)
        if rfp.capability_type not in my_types:
            raise HTTPException(403, "Not creator or matched supplier")
        if rfp.domain_filters and not any(d in my_domains for d in rfp.domain_filters):
            raise HTTPException(403, "Not creator or matched supplier")
    return RfpResponse(
        id=rfp.id,
        creator_agent_id=rfp.creator_agent_id,
        title=rfp.title,
        description=rfp.description,
        capability_type=rfp.capability_type,
        domain_filters=rfp.domain_filters,
        budget=rfp.budget,
        deadline_at=rfp.deadline_at,
        status=rfp.status,
        created_at=rfp.created_at,
    )


@router.patch("/rfps/{rfp_id}", response_model=RfpResponse)
async def update_rfp(
    rfp_id: str,
    body: RfpUpdate,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    r = await db.execute(select(Rfp).where(Rfp.id == rfp_id))
    rfp = r.scalar_one_or_none()
    if not rfp:
        raise HTTPException(404, "RFP not found")
    if rfp.creator_agent_id != agent.id:
        raise HTTPException(403, "Only creator can update")
    if body.status is not None:
        rfp.status = body.status
    if body.deadline_at is not None:
        rfp.deadline_at = body.deadline_at
    await db.flush()
    await db.refresh(rfp)
    return RfpResponse(
        id=rfp.id,
        creator_agent_id=rfp.creator_agent_id,
        title=rfp.title,
        description=rfp.description,
        capability_type=rfp.capability_type,
        domain_filters=rfp.domain_filters,
        budget=rfp.budget,
        deadline_at=rfp.deadline_at,
        status=rfp.status,
        created_at=rfp.created_at,
    )


async def _can_supplier_submit(db: AsyncSession, rfp: Rfp, agent_id: str) -> bool:
    """当前 agent 是否在 RFP 匹配到的供应方列表中。"""
    supplier_ids = await _match_supplier_agent_ids(db, rfp.capability_type, rfp.domain_filters)
    return agent_id in supplier_ids


@router.post("/rfps/{rfp_id}/proposals", response_model=ProposalResponse)
async def create_proposal(
    rfp_id: str,
    body: ProposalCreate,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    r = await db.execute(select(Rfp).where(Rfp.id == rfp_id))
    rfp = r.scalar_one_or_none()
    if not rfp:
        raise HTTPException(404, "RFP not found")
    if rfp.status != "open":
        raise HTTPException(400, "RFP is not open for proposals")
    if rfp.creator_agent_id == agent.id:
        raise HTTPException(400, "Creator cannot submit proposal to own RFP")
    if not await _can_supplier_submit(db, rfp, agent.id):
        raise HTTPException(403, "Your capabilities do not match this RFP")
    # 同一 RFP 下同一 supplier 仅一条
    r2 = await db.execute(
        select(Proposal).where(Proposal.rfp_id == rfp_id, Proposal.supplier_agent_id == agent.id)
    )
    if r2.scalar_one_or_none():
        raise HTTPException(400, "Already submitted a proposal to this RFP")
    prop_id = f"prop_{secrets.token_hex(12)}"
    prop = Proposal(
        id=prop_id,
        rfp_id=rfp_id,
        supplier_agent_id=agent.id,
        status="pending",
        price=body.price,
        delivery_at=body.delivery_at,
        content=body.content,
    )
    db.add(prop)
    await db.flush()
    await db.refresh(prop)
    return ProposalResponse(
        id=prop.id,
        rfp_id=prop.rfp_id,
        supplier_agent_id=prop.supplier_agent_id,
        status=prop.status,
        price=prop.price,
        delivery_at=prop.delivery_at,
        content=prop.content,
        created_at=prop.created_at,
    )


@router.get("/rfps/{rfp_id}/proposals", response_model=list[ProposalResponse])
async def list_proposals(
    rfp_id: str,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    r = await db.execute(select(Rfp).where(Rfp.id == rfp_id))
    rfp = r.scalar_one_or_none()
    if not rfp:
        raise HTTPException(404, "RFP not found")
    if rfp.creator_agent_id == agent.id:
        q = select(Proposal).where(Proposal.rfp_id == rfp_id).order_by(Proposal.created_at.desc())
    else:
        q = select(Proposal).where(
            Proposal.rfp_id == rfp_id,
            Proposal.supplier_agent_id == agent.id,
        ).order_by(Proposal.created_at.desc())
    r2 = await db.execute(q)
    props = r2.scalars().all()
    if rfp.creator_agent_id != agent.id and not await _can_supplier_submit(db, rfp, agent.id):
        raise HTTPException(403, "Not creator or matched supplier")
    return [
        ProposalResponse(
            id=p.id,
            rfp_id=p.rfp_id,
            supplier_agent_id=p.supplier_agent_id,
            status=p.status,
            price=p.price,
            delivery_at=p.delivery_at,
            content=p.content,
            created_at=p.created_at,
        )
        for p in props
    ]


@router.get("/rfps/{rfp_id}/summary", response_model=RfpSummaryResponse)
async def get_rfp_summary(
    rfp_id: str,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    r = await db.execute(select(Rfp).where(Rfp.id == rfp_id))
    rfp = r.scalar_one_or_none()
    if not rfp:
        raise HTTPException(404, "RFP not found")
    if rfp.creator_agent_id != agent.id:
        raise HTTPException(403, "Only creator can get summary")
    r2 = await db.execute(select(Proposal).where(Proposal.rfp_id == rfp_id).order_by(Proposal.created_at.desc()))
    props = r2.scalars().all()
    rfp_resp = RfpResponse(
        id=rfp.id,
        creator_agent_id=rfp.creator_agent_id,
        title=rfp.title,
        description=rfp.description,
        capability_type=rfp.capability_type,
        domain_filters=rfp.domain_filters,
        budget=rfp.budget,
        deadline_at=rfp.deadline_at,
        status=rfp.status,
        created_at=rfp.created_at,
    )
    return RfpSummaryResponse(
        rfp=rfp_resp,
        proposal_count=len(props),
        proposals=[
            ProposalResponse(
                id=p.id,
                rfp_id=p.rfp_id,
                supplier_agent_id=p.supplier_agent_id,
                status=p.status,
                price=p.price,
                delivery_at=p.delivery_at,
                content=p.content,
                created_at=p.created_at,
            )
            for p in props
        ],
    )


@router.get("/proposals/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(
    proposal_id: str,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    r = await db.execute(select(Proposal).where(Proposal.id == proposal_id))
    prop = r.scalar_one_or_none()
    if not prop:
        raise HTTPException(404, "Proposal not found")
    r2 = await db.execute(select(Rfp).where(Rfp.id == prop.rfp_id))
    rfp = r2.scalar_one_or_none()
    if not rfp:
        raise HTTPException(404, "RFP not found")
    if rfp.creator_agent_id != agent.id and prop.supplier_agent_id != agent.id:
        raise HTTPException(403, "Not creator or supplier")
    return ProposalResponse(
        id=prop.id,
        rfp_id=prop.rfp_id,
        supplier_agent_id=prop.supplier_agent_id,
        status=prop.status,
        price=prop.price,
        delivery_at=prop.delivery_at,
        content=prop.content,
        created_at=prop.created_at,
    )


@router.patch("/proposals/{proposal_id}", response_model=ProposalResponse)
async def update_proposal(
    proposal_id: str,
    body: ProposalUpdate,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    r = await db.execute(select(Proposal).where(Proposal.id == proposal_id))
    prop = r.scalar_one_or_none()
    if not prop:
        raise HTTPException(404, "Proposal not found")
    r2 = await db.execute(select(Rfp).where(Rfp.id == prop.rfp_id))
    rfp = r2.scalar_one_or_none()
    if not rfp:
        raise HTTPException(404, "RFP not found")
    if body.status is not None:
        if rfp.creator_agent_id == agent.id:
            if body.status not in ("accepted", "rejected"):
                raise HTTPException(400, "Creator can only set accepted or rejected")
        else:
            if prop.supplier_agent_id != agent.id:
                raise HTTPException(403, "Not supplier or creator")
            if body.status != "withdrawn":
                raise HTTPException(400, "Supplier can only set withdrawn")
        prop.status = body.status
    await db.flush()
    await db.refresh(prop)
    return ProposalResponse(
        id=prop.id,
        rfp_id=prop.rfp_id,
        supplier_agent_id=prop.supplier_agent_id,
        status=prop.status,
        price=prop.price,
        delivery_at=prop.delivery_at,
        content=prop.content,
        created_at=prop.created_at,
    )
