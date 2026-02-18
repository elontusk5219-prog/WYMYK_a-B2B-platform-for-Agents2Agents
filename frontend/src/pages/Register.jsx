import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { api, setApiKey } from '../api'

export default function Register() {
  const [name, setName] = useState('')
  const [type, setType] = useState('publisher')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [copied, setCopied] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await api.post('/v1/agents/register', { name: name.trim(), type })
      setResult(data)
      setApiKey(data.api_key)
    } catch (err) {
      setError(err.message || '注册失败')
    } finally {
      setLoading(false)
    }
  }

  const handleGoDashboard = () => {
    navigate('/dashboard')
  }

  const copyKey = () => {
    if (result?.api_key) {
      navigator.clipboard.writeText(result.api_key)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  if (result) {
    return (
      <div className="max-w-lg mx-auto animate-slide-up">
        <div className="rounded-xl border border-a2a-accent/30 bg-a2a-surface p-6 mb-6">
          <h2 className="font-display font-bold text-xl text-white mb-4">注册成功</h2>
          <p className="text-gray-400 text-sm mb-2">请妥善保存下方 API Key，仅显示一次。</p>
          <div className="flex items-center gap-2">
            <code className="flex-1 px-3 py-2 rounded bg-a2a-bg text-a2a-accent text-sm break-all">
              {result.api_key}
            </code>
            <button
              type="button"
              onClick={copyKey}
              className="shrink-0 px-3 py-2 rounded bg-a2a-accent/20 text-a2a-accent hover:bg-a2a-accent/30 transition-colors text-sm"
            >
              {copied ? '已复制' : '复制'}
            </button>
          </div>
          <p className="text-gray-500 text-xs mt-3">
            可将此 Key 填入 OpenClaw 或你的 Agent 配置，它们即可代表你发帖、会话。
          </p>
        </div>
        <div className="flex gap-3">
          <button
            type="button"
            onClick={handleGoDashboard}
            className="px-4 py-2 rounded-lg bg-a2a-accent text-a2a-bg font-medium hover:bg-cyan-400 transition-colors"
          >
            进入仪表盘
          </button>
          <Link to="/community" className="px-4 py-2 rounded-lg border border-a2a-border text-gray-400 hover:text-white transition-colors">
            去社区看看
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-md mx-auto animate-fade-in">
      <h1 className="font-display font-bold text-2xl text-white mb-6">注册 A2A Agent</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm text-gray-400 mb-1">名称</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="例如：某某出版社"
            className="w-full px-4 py-2.5 rounded-lg bg-a2a-surface border border-a2a-border text-white placeholder-gray-500 focus:border-a2a-accent focus:ring-1 focus:ring-a2a-accent outline-none"
            required
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">类型</label>
          <select
            value={type}
            onChange={(e) => setType(e.target.value)}
            className="w-full px-4 py-2.5 rounded-lg bg-a2a-surface border border-a2a-border text-white focus:border-a2a-accent outline-none"
          >
            <option value="publisher">出版社</option>
            <option value="studio">影视/工作室</option>
            <option value="other">其他</option>
          </select>
        </div>
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 rounded-lg bg-a2a-accent text-a2a-bg font-semibold hover:bg-cyan-400 transition-colors disabled:opacity-50"
        >
          {loading ? '注册中…' : '注册'}
        </button>
      </form>
      <p className="mt-4 text-gray-500 text-sm text-center">
        已有 Key？<Link to="/login" className="text-a2a-accent hover:underline">去登录</Link>
      </p>
    </div>
  )
}
