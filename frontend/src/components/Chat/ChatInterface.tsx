import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { authAPI, chatAPI, mindMapAPI } from '../../services/api'
import { AgentResponse, ConversationNode, MindMapGraph } from '../../types/api'
import TextFragment from '../Markdown/TextFragment'
import KnowledgeGraph from '../MindMap/KnowledgeGraph'

/**
 * 聊天界面主组件
 * 包含对话展示、输入框、思维导图侧边栏
 */
const ChatInterface = () => {
  const navigate = useNavigate()
  const [messages, setMessages] = useState<AgentResponse[]>([])
  const [input, setInput] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)
  const [mindMapData, setMindMapData] = useState<MindMapGraph>({ nodes: [], edges: [] })
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null)
  const [sessionId] = useState<string>(() => `session_${Date.now()}`) // 会话 ID

  /**
   * 发送消息（支持普通提问和划词追问）
   */
  const handleSend = async (refFragmentId?: string) => {
    if (!input.trim() || loading) return

    const query = input.trim()
    setInput('')
    setLoading(true)

    try {
      const parentId = messages.length > 0 ? messages[messages.length - 1].conversation_id : null
      const response = await chatAPI.sendMessage({
        query,
        parent_id: parentId,
        ref_fragment_id: refFragmentId || null,
        session_id: sessionId,
      })

      setMessages((prev) => [...prev, response])
      setCurrentConversationId(response.conversation_id)

      // 更新思维导图
      if (response.conversation_id) {
        const graphData = await mindMapAPI.getMindMap(response.conversation_id)
        setMindMapData(graphData)
      }
    } catch (error: any) {
      console.error('发送消息失败:', error)
      if (error.response?.status === 401) {
        authAPI.logout()
        navigate('/login')
      }
    } finally {
      setLoading(false)
    }
  }

  /**
   * 处理片段选择（划词追问）
   */
  const handleFragmentSelect = (fragmentId: string) => {
    const query = prompt('请输入你的问题:')
    if (query && messages.length > 0) {
      const lastMessage = messages[messages.length - 1]
      // 使用统一的 sendMessage，传入 ref_fragment_id
      setInput(query)
      setTimeout(() => {
        handleSend(fragmentId)
      }, 0)
    }
  }

  /**
   * 登出
   */
  const handleLogout = () => {
    authAPI.logout()
    navigate('/login')
  }

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* 主聊天区域 */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* 头部 */}
        <div style={{
          padding: '1rem',
          borderBottom: '1px solid #ddd',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h1>DeepStudy</h1>
          <button onClick={handleLogout}>登出</button>
        </div>

        {/* 消息列表 */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '1rem',
        }}>
          {messages.map((msg, index) => (
            <div key={index} style={{ marginBottom: '2rem' }}>
              <div>
                <TextFragment
                  content={msg.answer}
                  fragments={msg.fragments}
                  onFragmentSelect={handleFragmentSelect}
                />
              </div>
            </div>
          ))}
          {loading && <div>思考中...</div>}
        </div>

        {/* 输入框 */}
        <div style={{
          padding: '1rem',
          borderTop: '1px solid #ddd',
          display: 'flex',
          gap: '0.5rem'
        }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="输入你的问题..."
            style={{
              flex: 1,
              padding: '0.5rem',
              border: '1px solid #ddd',
              borderRadius: '4px'
            }}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading || !input.trim() ? 'not-allowed' : 'pointer'
            }}
          >
            发送
          </button>
        </div>
      </div>

      {/* 思维导图侧边栏 */}
      <div style={{
        width: '400px',
        borderLeft: '1px solid #ddd',
        padding: '1rem'
      }}>
        <h3 style={{ marginBottom: '1rem' }}>知识图谱</h3>
        <div style={{ height: 'calc(100vh - 100px)' }}>
          <KnowledgeGraph data={mindMapData} />
        </div>
      </div>
    </div>
  )
}

export default ChatInterface
