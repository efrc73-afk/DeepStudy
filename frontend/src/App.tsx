import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './components/Auth/Login'
import Register from './components/Auth/Register'
import ChatInterface from './components/Chat/ChatInterface'
import { useAuth } from './hooks/useAuth'
import './App.css'

/**
 * 应用主组件
 * 处理路由和认证状态
 */
function App() {
  const { isAuthenticated } = useAuth()

  return (
    <div className="app-background">
      <div className="app-content">
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
    </div>
   </div>
  )
}

export default App
