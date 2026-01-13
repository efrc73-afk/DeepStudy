import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './components/Auth/Login'
import Register from './components/Auth/Register'
import ChatInterface from './components/Chat/ChatInterface'
import { useAuth } from './hooks/useAuth'

/**
 * 应用主组件
 * 处理路由和认证状态
 */
function App() {
  const { isAuthenticated } = useAuth()

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/"
        element={
          isAuthenticated() ? <ChatInterface /> : <Navigate to="/login" replace />
        }
      />
    </Routes>
  )
}

export default App
