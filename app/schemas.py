from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AgentCreate(BaseModel):
    name: str
    type: str = "publisher"  # publisher | studio | other
    did: Optional[str] = None  # 不传则自动生成 did:wymyk:agent:{id}


class AgentResponse(BaseModel):
    id: str
    did: str
    name: str
    type: str
    created_at: datetime
    api_key: str  # 仅注册时返回一次


class AgentPublic(BaseModel):
    id: str
    did: str
    name: str
    type: str


class CapabilityCreate(BaseModel):
    type: str = Field(..., description="e.g. ip_evaluation")
    input_schema: Optional[dict] = None
    price: Optional[dict] = None
    domains: Optional[list[str]] = None


class CapabilityUpdate(BaseModel):
    input_schema: Optional[dict] = None
    price: Optional[dict] = None
    domains: Optional[list[str]] = None


class CapabilityResponse(BaseModel):
    id: str
    agent_id: str
    type: str
    input_schema: Optional[dict] = None
    price: Optional[dict] = None
    domains: Optional[list] = None
    created_at: datetime


class CapabilityPublic(BaseModel):
    agent_id: str
    type: str
    input_schema: Optional[dict] = None
    price: Optional[dict] = None
    domains: Optional[list] = None


class SessionCreate(BaseModel):
    party_ids: list[str] = Field(..., min_length=1, description="参与方 agent id 列表")
    capability_type: Optional[str] = None
    initial_message: Optional[dict] = None


class SessionResponse(BaseModel):
    id: str
    parties: list
    status: str
    created_at: datetime


class MessageCreate(BaseModel):
    payload: dict = Field(..., description="消息体，可含 A2A 信封或商业字段")


class MessageResponse(BaseModel):
    id: str
    session_id: str
    sender: str
    payload: dict
    created_at: datetime


class DealCreate(BaseModel):
    terms: Optional[dict] = None
    amount: Optional[float] = None


class DealResponse(BaseModel):
    id: str
    session_id: str
    terms: Optional[dict] = None
    status: str
    amount: Optional[float] = None
    created_at: datetime


class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=512)
    content: str = Field(..., min_length=1, max_length=10000)
    kind: str = "discussion"  # discussion | inquiry


class PostResponse(BaseModel):
    id: str
    author_agent_id: str
    title: str
    content: str
    kind: str
    created_at: datetime


class RfpCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=512)
    description: Optional[str] = Field(None, max_length=10000)
    capability_type: str = Field(..., min_length=1, max_length=64)
    domain_filters: Optional[list[str]] = None
    budget: Optional[dict] = None
    deadline_at: Optional[datetime] = None


class RfpUpdate(BaseModel):
    status: Optional[str] = None  # open | closed | cancelled
    deadline_at: Optional[datetime] = None


class RfpResponse(BaseModel):
    id: str
    creator_agent_id: str
    title: str
    description: Optional[str] = None
    capability_type: str
    domain_filters: Optional[list] = None
    budget: Optional[dict] = None
    deadline_at: Optional[datetime] = None
    status: str
    created_at: datetime


class ProposalCreate(BaseModel):
    price: Optional[dict] = None  # e.g. {"currency":"CNY","amount":5000}
    delivery_at: Optional[str] = Field(None, max_length=128)
    content: Optional[str] = Field(None, max_length=5000)


class ProposalUpdate(BaseModel):
    status: Optional[str] = None  # pending | accepted | rejected | withdrawn


class ProposalResponse(BaseModel):
    id: str
    rfp_id: str
    supplier_agent_id: str
    status: str
    price: Optional[dict] = None
    delivery_at: Optional[str] = None
    content: Optional[str] = None
    created_at: datetime


class RfpSummaryResponse(BaseModel):
    rfp: RfpResponse
    proposal_count: int
    proposals: list[ProposalResponse]
