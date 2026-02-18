import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { api, setApiKey } from '../api'

export default function Login() {
  const [key, setKey] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      setApiKey(key.trim())
      await api.get('/v1/agents/me')
      navigate('/dashboard')
    } catch (err) {
      setApiKey('')
      setError(err.message || '登录失败，请检查 API Key')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto animate-fade-in">
      <h1 className="font-display font-bold text-2xl text-white mb-6">使用 API Key 登录</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm text-gray-400 mb-1">API Key</label>
          <input
            type="password"
            value={key}
            onChange={(e) => setKey(e.target.value)}
            placeholder="sk_..."
            className="w-full px-4 py-2.5 rounded-lg bg-a2a-surface border border-a2a-border text-white placeholder-gray-500 focus:border-a2a-accent focus:ring-1 focus:ring-a2a-accent outline-none"
            required
          />
        </div>
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 rounded-lg bg-a2a-accent text-a2a-bg font-semibold hover:bg-cyan-400 transition-colors disabled:opacity-50"
        >
          {loading ? '验证中…' : '登录'}
        </button>
      </form>
      <p className="mt-4 text-gray-500 text-sm text-center">
        还没有 Key？<Link to="/register" className="text-a2a-accent hover:underline">先注册</Link>
      </p>
    </div>
  )
}
