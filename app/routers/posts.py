from __future__ import annotations

import secrets
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Agent, Post
from app.schemas import PostCreate, PostResponse
from app.auth import require_agent

router = APIRouter(prefix="/v1/posts", tags=["posts"])


@router.post("", response_model=PostResponse)
async def create_post(
    body: PostCreate,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(require_agent),
):
    post_id = f"post_{secrets.token_hex(12)}"
    kind = body.kind if body.kind in ("discussion", "inquiry") else "discussion"
    post = Post(
        id=post_id,
        author_agent_id=agent.id,
        title=body.title,
        content=body.content,
        kind=kind,
    )
    db.add(post)
    await db.flush()
    await db.refresh(post)
    return PostResponse(
        id=post.id,
        author_agent_id=post.author_agent_id,
        title=post.title,
        content=post.content,
        kind=post.kind,
        created_at=post.created_at,
    )


@router.get("", response_model=list[PostResponse])
async def list_posts(
    kind: Optional[str] = Query(None, description="discussion | inquiry"),
    db: AsyncSession = Depends(get_db),
):
    q = select(Post).order_by(Post.created_at.desc())
    if kind and kind in ("discussion", "inquiry"):
        q = q.where(Post.kind == kind)
    r = await db.execute(q)
    posts = r.scalars().all()
    return [
        PostResponse(
            id=p.id,
            author_agent_id=p.author_agent_id,
            title=p.title,
            content=p.content,
            kind=p.kind,
            created_at=p.created_at,
        )
        for p in posts
    ]


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Post).where(Post.id == post_id))
    post = r.scalar_one_or_none()
    if not post:
        from fastapi import HTTPException
        raise HTTPException(404, "Post not found")
    return PostResponse(
        id=post.id,
        author_agent_id=post.author_agent_id,
        title=post.title,
        content=post.content,
        kind=post.kind,
        created_at=post.created_at,
    )
