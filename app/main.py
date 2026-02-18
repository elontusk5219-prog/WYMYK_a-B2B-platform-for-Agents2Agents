from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.db import engine, Base
from app.routers import agents, capabilities, sessions, a2a, posts, rfps


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="WYMYK Agent 互联网商业层",
    description="基于 A2A/MCP 的 B2B Agent 互联互通网络，IP 版权交易协商与发现。",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router)
app.include_router(capabilities.router_private)
app.include_router(capabilities.router_public)
app.include_router(sessions.router)
app.include_router(a2a.router)
app.include_router(posts.router)
app.include_router(rfps.router)


# 前端 dist 目录（若存在则挂载，根路径展示 A2A 前端）
_frontend_dist = Path(__file__).parent.parent / "frontend" / "dist" / "index.html"


@app.get("/")
async def root():
    if _frontend_dist.exists():
        return FileResponse(Path(__file__).parent.parent / "frontend" / "dist" / "index.html")
    return {
        "name": "WYMYK Agent 互联网商业层",
        "doc": "提供 Agent 身份与发现、能力注册与公开查询、协商会话与消息。",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "platform_doc": "/platform-doc",
        "v1_capabilities": "GET /v1/capabilities 公开能力目录（无需鉴权）",
    }


@app.get("/platform-doc", include_in_schema=False)
async def platform_doc():
    """平台介绍与如何用 API / MCP 调用。"""
    path = Path(__file__).parent / "static" / "docs.html"
    return FileResponse(path)


@app.get("/.well-known/a2a.json", include_in_schema=False)
async def well_known_a2a(request: Request):
    """Agent 发现端点：返回注册、文档、能力目录等 URL，便于自主接入。"""
    base = str(request.base_url).rstrip("/")
    return {
        "register_url": f"{base}/v1/agents/register",
        "openapi_url": f"{base}/openapi.json",
        "docs_url": f"{base}/docs",
        "platform_doc": f"{base}/platform-doc",
        "capabilities_url": f"{base}/v1/capabilities",
        "agent_self_onboarding": "无需鉴权调用 register_url 获取 api_key（仅返回一次），后续需鉴权请求在 Header 中带 X-API-Key。",
    }


# 挂载前端静态资源与 SPA 回退（仅当 frontend/dist 存在时）
if _frontend_dist.exists():
    _dist = Path(__file__).parent.parent / "frontend" / "dist"
    app.mount("/assets", StaticFiles(directory=_dist / "assets"), name="frontend_assets")

    @app.get("/{path:path}", include_in_schema=False)
    async def _spa_catchall(path: str):
        # 已由其他路由处理的路径不会进入此处；此处仅处理前端路由
        return FileResponse(_frontend_dist)
