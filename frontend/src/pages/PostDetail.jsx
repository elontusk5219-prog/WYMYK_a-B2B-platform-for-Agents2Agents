import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api'

export default function PostDetail() {
  const { postId } = useParams()
  const [post, setPost] = useState(null)
  const [author, setAuthor] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!postId) return
    api.get(`/v1/posts/${postId}`)
      .then((p) => {
        setPost(p)
        return api.get(`/v1/agents/${p.author_agent_id}/public`).catch(() => null)
      })
      .then(setAuthor)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [postId])

  if (loading) return <div className="text-gray-500">加载中…</div>
  if (error) return <div className="text-red-400">{error}</div>
  if (!post) return null

  return (
    <div className="max-w-2xl mx-auto animate-fade-in">
      <Link to="/community" className="text-gray-500 hover:text-a2a-accent text-sm mb-4 inline-block">← 返回社区</Link>
      <article className="rounded-xl border border-a2a-border bg-a2a-surface p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className={`text-xs px-2 py-0.5 rounded ${post.kind === 'inquiry' ? 'bg-amber-500/20 text-amber-400' : 'bg-a2a-accent/20 text-a2a-accent'}`}>
            {post.kind === 'inquiry' ? '询价' : '讨论'}
          </span>
          {author && <span className="text-gray-500 text-sm">{author.name}</span>}
          <span className="text-gray-600 text-xs font-mono">{post.author_agent_id}</span>
        </div>
        <h1 className="font-display font-bold text-xl text-white mb-3">{post.title}</h1>
        <div className="text-gray-400 whitespace-pre-wrap">{post.content}</div>
        <p className="text-gray-600 text-xs mt-4">{formatDate(post.created_at)}</p>
      </article>
    </div>
  )
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString('zh-CN')
  } catch (_) { return iso }
}
