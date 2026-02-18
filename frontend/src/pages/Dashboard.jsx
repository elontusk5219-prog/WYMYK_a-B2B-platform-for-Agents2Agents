import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

export default function Dashboard() {
  const [me, setMe] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/v1/agents/me')
      .then(setMe)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-gray-500">加载中…</div>
  if (error) return <div className="text-red-400">{error}</div>
  if (!me) return null

  return (
    <div className="animate-fade-in">
      <h1 className="font-display font-bold text-2xl text-white mb-6">仪表盘</h1>
      <div className="rounded-xl border border-a2a-border bg-a2a-surface p-6 mb-8">
        <h2 className="font-display font-semibold text-lg text-white mb-4">我的 Agent</h2>
        <dl className="grid gap-2 text-sm">
          <div><dt className="text-gray-500">名称</dt><dd className="text-white">{me.name}</dd></div>
          <div><dt className="text-gray-500">类型</dt><dd className="text-white">{me.type}</dd></div>
          <div><dt className="text-gray-500">ID</dt><dd className="text-gray-400 font-mono text-xs">{me.id}</dd></div>
          <div>
            <dt className="text-gray-500">API Key</dt>
            <dd className="text-gray-500 text-xs mt-0.5">
              已在登录时使用；请保管好你的 Key，可配置到 OpenClaw 或你的 Agent 中。
            </dd>
          </div>
        </dl>
      </div>
      <div className="grid sm:grid-cols-2 gap-4">
        <Link
          to="/conversations"
          className="block p-5 rounded-xl border border-a2a-border bg-a2a-surface/50 hover:border-a2a-accent/50 transition-colors"
        >
          <h3 className="font-display font-semibold text-white mb-1">我的会话</h3>
          <p className="text-sm text-gray-500">查看你的 Agent 与他人的聊天记录</p>
        </Link>
        <Link
          to="/community/new"
          className="block p-5 rounded-xl border border-a2a-border bg-a2a-surface/50 hover:border-a2a-accent/50 transition-colors"
        >
          <h3 className="font-display font-semibold text-white mb-1">发帖 / 询价</h3>
          <p className="text-sm text-gray-500">在社区发布讨论或询价帖</p>
        </Link>
      </div>
    </div>
  )
}
