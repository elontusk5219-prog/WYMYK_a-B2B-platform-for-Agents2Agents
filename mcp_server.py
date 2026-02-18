"""
WYMYK 平台 MCP Server：暴露 list_capabilities、create_inquiry、send_message 工具，
供 OpenClaw、Claude Desktop 等 MCP 客户端调用。需先启动主服务 (uvicorn app.main:app)。
依赖: pip install fastmcp httpx
"""
from __future__ import annotations

import os
import httpx
from fastmcp import FastMCP

BASE_URL = os.environ.get("WYMYK_BASE_URL", "http://localhost:8000")
API_KEY = os.environ.get("WYMYK_API_KEY", "")

mcp = FastMCP(
    "WYMYK Agent 商业层",
    instructions="提供 WYMYK 平台能力发现与协商：查询能力目录、创建询价会话、发送消息。",
)


@mcp.tool(name="wymyk_list_capabilities", description="查询 WYMYK 平台公开能力目录，可按类型或领域过滤。")
def wymyk_list_capabilities(
    type: str | None = None,
    domain: str | None = None,
) -> list[dict]:
    """无需 API Key。返回能力列表（agent_id、type、price、domains 等）。"""
    params = {}
    if type:
        params["type"] = type
    if domain:
        params["domain"] = domain
    with httpx.Client(timeout=30.0) as client:
        r = client.get(f"{BASE_URL}/v1/capabilities", params=params or None)
        r.raise_for_status()
        return r.json()


@mcp.tool(
    name="wymyk_create_inquiry",
    description="在 WYMYK 平台创建协商会话并可选发送首条询价消息。",
)
def wymyk_create_inquiry(
    party_ids: list[str],
    initial_message: dict | None = None,
    capability_type: str | None = None,
) -> dict:
    """需要设置环境变量 WYMYK_API_KEY。party_ids 为参与方 agent id 列表。"""
    if not API_KEY:
        return {"error": "WYMYK_API_KEY not set"}
    with httpx.Client(timeout=30.0) as client:
        r = client.post(
            f"{BASE_URL}/v1/sessions",
            json={
                "party_ids": party_ids,
                "initial_message": initial_message,
                "capability_type": capability_type,
            },
            headers={ "X-API-Key": API_KEY },
        )
        r.raise_for_status()
        return r.json()


@mcp.tool(
    name="wymyk_send_message",
    description="向已有 WYMYK 会话发送一条消息（询价、报价、确认等）。",
)
def wymyk_send_message(
    session_id: str,
    payload: dict,
) -> dict:
    """需要设置环境变量 WYMYK_API_KEY。payload 为消息体（可含 A2A 或商业字段）。"""
    if not API_KEY:
        return {"error": "WYMYK_API_KEY not set"}
    with httpx.Client(timeout=30.0) as client:
        r = client.post(
            f"{BASE_URL}/v1/sessions/{session_id}/messages",
            json={"payload": payload},
            headers={ "X-API-Key": API_KEY },
        )
        r.raise_for_status()
        return r.json()


if __name__ == "__main__":
    mcp.run()
