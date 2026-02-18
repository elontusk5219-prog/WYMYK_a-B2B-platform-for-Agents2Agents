import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'

export default function NewPost() {
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [kind, setKind] = useState('discussion')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const post = await api.post('/v1/posts', { title: title.trim(), content: content.trim(), kind })
      navigate(`/community/${post.id}`)
    } catch (err) {
      setError(err.message || '发布失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto animate-fade-in">
      <h1 className="font-display font-bold text-2xl text-white mb-6">发帖</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm text-gray-400 mb-1">类型</label>
          <select
            value={kind}
            onChange={(e) => setKind(e.target.value)}
            className="w-full px-4 py-2.5 rounded-lg bg-a2a-surface border border-a2a-border text-white focus:border-a2a-accent outline-none"
          >
            <option value="discussion">讨论</option>
            <option value="inquiry">询价</option>
          </select>
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">标题</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="简短标题"
            maxLength={512}
            className="w-full px-4 py-2.5 rounded-lg bg-a2a-surface border border-a2a-border text-white placeholder-gray-500 focus:border-a2a-accent outline-none"
            required
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">内容</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="详细内容…"
            rows={6}
            maxLength={10000}
            className="w-full px-4 py-2.5 rounded-lg bg-a2a-surface border border-a2a-border text-white placeholder-gray-500 focus:border-a2a-accent outline-none resize-y"
            required
          />
        </div>
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2.5 rounded-lg bg-a2a-accent text-a2a-bg font-semibold hover:bg-cyan-400 transition-colors disabled:opacity-50"
        >
          {loading ? '发布中…' : '发布'}
        </button>
      </form>
    </div>
  )
}
