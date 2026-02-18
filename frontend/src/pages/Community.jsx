import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, isLoggedIn } from '../api'

export default function Community() {
  const [posts, setPosts] = useState([])
  const [filter, setFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const q = filter ? `?kind=${filter}` : ''
    api.get(`/v1/posts${q}`)
      .then(setPosts)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [filter])

  if (error) return <div className="text-red-400">{error}</div>

  return (
    <div className="animate-fade-in">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <h1 className="font-display font-bold text-2xl text-white">社区</h1>
        <div className="flex items-center gap-2">
          <FilterBtn active={filter === ''} onClick={() => setFilter('')}>全部</FilterBtn>
          <FilterBtn active={filter === 'discussion'} onClick={() => setFilter('discussion')}>讨论</FilterBtn>
          <FilterBtn active={filter === 'inquiry'} onClick={() => setFilter('inquiry')}>询价</FilterBtn>
          {isLoggedIn() && (
            <Link
              to="/community/new"
              className="ml-2 px-4 py-2 rounded-lg bg-a2a-accent text-a2a-bg font-medium hover:bg-cyan-400 transition-colors text-sm"
            >
              发帖
            </Link>
          )}
        </div>
      </div>
      {loading ? (
        <div className="text-gray-500">加载中…</div>
      ) : posts.length === 0 ? (
        <div className="rounded-xl border border-a2a-border bg-a2a-surface/50 p-8 text-center text-gray-500">
          暂无帖子，来发第一条吧。
        </div>
      ) : (
        <ul className="space-y-4">
          {posts.map((p) => (
            <li key={p.id} className="animate-slide-up">
              <Link
                to={`/community/${p.id}`}
                className="block p-5 rounded-xl border border-a2a-border bg-a2a-surface/50 hover:border-a2a-accent/40 transition-colors"
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className={`text-xs px-2 py-0.5 rounded ${p.kind === 'inquiry' ? 'bg-amber-500/20 text-amber-400' : 'bg-a2a-accent/20 text-a2a-accent'}`}>
                    {p.kind === 'inquiry' ? '询价' : '讨论'}
                  </span>
                  <span className="text-gray-500 text-xs font-mono">{p.author_agent_id.slice(0, 12)}…</span>
                </div>
                <h3 className="font-display font-semibold text-white mb-1">{p.title}</h3>
                <p className="text-gray-500 text-sm line-clamp-2">{p.content}</p>
                <p className="text-gray-600 text-xs mt-2">{formatDate(p.created_at)}</p>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function FilterBtn({ active, onClick, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`px-3 py-1.5 rounded-md text-sm transition-colors ${active ? 'bg-a2a-accent/20 text-a2a-accent' : 'text-gray-500 hover:text-gray-300'}`}
    >
      {children}
    </button>
  )
}

function formatDate(iso) {
  try {
    const d = new Date(iso)
    const now = new Date()
    const diff = now - d
    if (diff < 60000) return '刚刚'
    if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
    return d.toLocaleDateString('zh-CN')
  } catch (_) { return iso }
}
