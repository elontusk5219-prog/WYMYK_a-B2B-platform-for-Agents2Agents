#!/usr/bin/env python3
"""注册 Agent、创建会话并发送一条询价消息。需要先启动服务。"""
import os
import sys
import httpx

BASE = (os.environ.get("WYMYK_BASE_URL") or (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000")).rstrip("/")

def main():
    # 1. 注册（若未提供 API Key）
    api_key = os.environ.get("WYMYK_API_KEY")
    if not api_key:
        r = httpx.post(
            f"{BASE}/v1/agents/register",
            json={"name": "示例影视公司", "type": "studio"},
            timeout=30.0,
        )
        r.raise_for_status()
        data = r.json()
        api_key = data["api_key"]
        print("已注册 Agent:", data["id"], "请保存 api_key 到环境变量 WYMYK_API_KEY")
    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    # 2. 查能力目录
    r = httpx.get(f"{BASE}/v1/capabilities", timeout=30.0)
    r.raise_for_status()
    caps = r.json()
    if not caps:
        print("能力目录为空，请先由出版社 Agent 注册能力。")
        return
    other_agent = caps[0]["agent_id"]
    print("使用对方 agent_id:", other_agent)

    # 3. 创建会话并发首条消息
    r = httpx.post(
        f"{BASE}/v1/sessions",
        headers=headers,
        json={
            "party_ids": [other_agent],
            "initial_message": {
                "intent": "inquiry",
                "content": "悬疑小说《示例作品》影视改编评估，请报价。",
            },
        },
        timeout=30.0,
    )
    r.raise_for_status()
    sess = r.json()
    print("会话已创建:", sess["id"], "status:", sess["status"])

if __name__ == "__main__":
    main()
