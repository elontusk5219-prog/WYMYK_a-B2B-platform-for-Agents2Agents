#!/bin/bash
# A2A 平台部署脚本（在本地执行，将代码同步到服务器并执行远程安装）
# 用法: ./scripts/deploy.sh [ssh_user] [server_ip]
# 示例: ./scripts/deploy.sh ubuntu 124.156.137.176
# 需在项目根目录执行，且本机已配置 SSH 密钥（如 -i /path/to/A2A.pem）

set -e
SSH_USER="${1:-ubuntu}"
SERVER="${2:-124.156.137.176}"
SSH_KEY="${SSH_KEY:-$HOME/Downloads/A2A.pem}"
REMOTE_DIR="${REMOTE_DIR:-~/A2A}"

echo ">>> 同步代码到 ${SSH_USER}@${SERVER}:${REMOTE_DIR}"
rsync -avz --progress \
  -e "ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no" \
  --exclude '.env' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude 'frontend/node_modules' \
  --exclude 'frontend/dist' \
  --exclude '.git' \
  --exclude '.cursor' \
  ./ "${SSH_USER}@${SERVER}:${REMOTE_DIR}/"

echo ">>> 远程安装依赖并检查"
ssh -i "${SSH_KEY}" -o StrictHostKeyChecking=no "${SSH_USER}@${SERVER}" "cd ${REMOTE_DIR} && \
  (command -v python3 >/dev/null || (sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv)) && \
  python3 -m venv .venv 2>/dev/null || true && \
  . .venv/bin/activate && \
  pip install -r requirements.txt -q && \
  echo 'Python deps OK'"

echo ">>> 若尚未配置 .env，请 SSH 登录后创建: nano ${REMOTE_DIR}/.env"
echo ">>> 填写 DATABASE_URL=postgresql+asyncpg://用户:密码@数据库地址:5432/库名"
echo ">>> 启动命令: cd ${REMOTE_DIR} && . .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ">>> 建议使用 systemd 常驻，见 docs/05-部署指南.md"
