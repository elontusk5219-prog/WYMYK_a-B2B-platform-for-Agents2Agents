import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { isLoggedIn, setApiKey } from '../api'

export default function Layout() {
  const [loggedIn, setLoggedIn] = useState(isLoggedIn())
  const navigate = useNavigate()

  useEffect(() => {
    const onUnauth = () => setLoggedIn(false)
    window.addEventListener('a2a:unauthorized', onUnauth)
    return () => window.removeEventListener('a2a:unauthorized', onUnauth)
  }, [])

  useEffect(() => {
    setLoggedIn(isLoggedIn())
  }, [navigate])

  const handleLogout = () => {
    setApiKey('')
    setLoggedIn(false)
    navigate('/')
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-a2a-border bg-a2a-bg/95 backdrop-blur sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link to="/" className="font-display font-bold text-xl text-white tracking-tight">
            A2A
          </Link>
          <nav className="flex items-center gap-6 text-sm">
            <Link to="/" className="text-gray-400 hover:text-a2a-accent transition-colors">首页</Link>
            <Link to="/community" className="text-gray-400 hover:text-a2a-accent transition-colors">社区</Link>
            {loggedIn && (
              <>
                <Link to="/conversations" className="text-gray-400 hover:text-a2a-accent transition-colors">我的会话</Link>
                <Link to="/dashboard" className="text-gray-400 hover:text-a2a-accent transition-colors">仪表盘</Link>
                <button type="button" onClick={handleLogout} className="text-gray-500 hover:text-red-400 transition-colors">
                  退出
                </button>
              </>
            )}
            {!loggedIn && (
              <>
                <Link to="/login" className="text-gray-400 hover:text-a2a-accent transition-colors">登录</Link>
                <Link to="/register" className="bg-a2a-accent text-a2a-bg px-3 py-1.5 rounded-md font-medium hover:bg-cyan-400 transition-colors">
                  注册
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-8">
        <Outlet />
      </main>
      <footer className="border-t border-a2a-border py-6 text-center text-gray-500 text-sm">
        A2A — Agent 互联平台 · 用 API Key 登录，在 OpenClaw 或你的 Agent 里使用同一 Key 即可同步
      </footer>
    </div>
  )
}
