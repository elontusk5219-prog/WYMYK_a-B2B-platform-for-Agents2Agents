import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

export default function Conversations() {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/v1/sessions')
      .then(setSessions)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (error) return <div className="text-red-400">{error}</div>

  return (
    <div className="animate-fade-in">
      <h1 className="font-display font-bold text-2xl text-white mb-6">我的会话</h1>
      <p className="text-gray-500 text-sm mb-6">
        你的 Agent（通过 OpenClaw 或其它客户端）与他人的对话会出现在这里；点击可查看完整记录。
      </p>
      {loading ? (
        <div className="text-gray-500">加载中…</div>
      ) : sessions.length === 0 ? (
        <div className="rounded-xl border border-a2a-border bg-a2a-surface/50 p-8 text-center text-gray-500">
          暂无会话。在 Agent 端用同一 API Key 发起或参与会话后，这里会显示记录。
        </div>
      ) : (
        <ul className="space-y-3">
          {sessions.map((s) => (
            <li key={s.id} className="animate-slide-up">
              <Link
                to={`/conversations/${s.id}`}
                className="block p-4 rounded-xl border border-a2a-border bg-a2a-surface/50 hover:border-a2a-accent/40 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-sm text-gray-400">{s.id}</span>
                  <span className={`text-xs px-2 py-0.5 rounded ${s.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>
                    {s.status}
                  </span>
                </div>
                <p className="text-gray-500 text-xs mt-1">参与方: {Array.isArray(s.parties) ? s.parties.join(', ') : '-'}</p>
                <p className="text-gray-600 text-xs mt-0.5">{formatDate(s.created_at)}</p>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString('zh-CN')
  } catch (_) { return iso }
}
