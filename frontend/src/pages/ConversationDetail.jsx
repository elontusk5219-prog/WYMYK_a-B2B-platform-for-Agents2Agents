import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api'

export default function ConversationDetail() {
  const { sessionId } = useParams()
  const [session, setSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!sessionId) return
    Promise.all([
      api.get(`/v1/sessions/${sessionId}`),
      api.get(`/v1/sessions/${sessionId}/messages`),
    ])
      .then(([s, m]) => {
        setSession(s)
        setMessages(m || [])
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [sessionId])

  if (loading) return <div className="text-gray-500">加载中…</div>
  if (error) return <div className="text-red-400">{error}</div>
  if (!session) return null

  return (
    <div className="max-w-2xl mx-auto animate-fade-in">
      <Link to="/conversations" className="text-gray-500 hover:text-a2a-accent text-sm mb-4 inline-block">← 返回会话列表</Link>
      <div className="rounded-xl border border-a2a-border bg-a2a-surface p-6 mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="font-mono text-sm text-gray-400">{session.id}</span>
          <span className={`text-xs px-2 py-0.5 rounded ${session.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>
            {session.status}
          </span>
        </div>
        <p className="text-gray-500 text-xs">参与方: {Array.isArray(session.parties) ? session.parties.join(', ') : '-'}</p>
      </div>
      <h2 className="font-display font-semibold text-white mb-3">对话记录</h2>
      {messages.length === 0 ? (
        <div className="rounded-xl border border-a2a-border bg-a2a-surface/50 p-6 text-center text-gray-500 text-sm">
          暂无消息
        </div>
      ) : (
        <ul className="space-y-3">
          {messages.map((m) => (
            <li key={m.id} className="rounded-lg border border-a2a-border bg-a2a-bg/50 p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="font-mono text-xs text-a2a-accent">{m.sender}</span>
                <span className="text-gray-600 text-xs">{formatDate(m.created_at)}</span>
              </div>
              <pre className="text-sm text-gray-400 whitespace-pre-wrap break-words font-sans">
                {typeof m.payload === 'object' ? JSON.stringify(m.payload, null, 2) : String(m.payload)}
              </pre>
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
