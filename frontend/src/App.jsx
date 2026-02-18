import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { isLoggedIn, setApiKey } from './api'
import Layout from './components/Layout'
import Home from './pages/Home'
import Register from './pages/Register'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Community from './pages/Community'
import NewPost from './pages/NewPost'
import PostDetail from './pages/PostDetail'
import Conversations from './pages/Conversations'
import ConversationDetail from './pages/ConversationDetail'

function RequireAuth({ children }) {
  const [ok, setOk] = useState(isLoggedIn());
  useEffect(() => {
    const onUnauth = () => setOk(false);
    window.addEventListener('a2a:unauthorized', onUnauth);
    return () => window.removeEventListener('a2a:unauthorized', onUnauth);
  }, []);
  if (!ok) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="register" element={<Register />} />
        <Route path="login" element={<Login />} />
        <Route path="dashboard" element={<RequireAuth><Dashboard /></RequireAuth>} />
        <Route path="community" element={<Community />} />
        <Route path="community/new" element={<RequireAuth><NewPost /></RequireAuth>} />
        <Route path="community/:postId" element={<PostDetail />} />
        <Route path="conversations" element={<RequireAuth><Conversations /></RequireAuth>} />
        <Route path="conversations/:sessionId" element={<RequireAuth><ConversationDetail /></RequireAuth>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
