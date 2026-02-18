#!/usr/bin/env python3
"""查询 WYMYK 平台公开能力目录（无需 API Key）。"""
import sys
import httpx

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/")

def main():
    params = {}
    if len(sys.argv) > 2:
        params["type"] = sys.argv[2]
    if len(sys.argv) > 3:
        params["domain"] = sys.argv[3]
    r = httpx.get(f"{BASE}/v1/capabilities", params=params or None, timeout=30.0)
    r.raise_for_status()
    data = r.json()
    print(f"共 {len(data)} 条能力")
    for cap in data:
        print(f"  - agent_id={cap.get('agent_id')} type={cap.get('type')} domains={cap.get('domains')} price={cap.get('price')}")

if __name__ == "__main__":
    main()
