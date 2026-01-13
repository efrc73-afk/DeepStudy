/**
 * API 服务封装
 * 处理所有与后端的 HTTP 通信，包括 JWT token 管理
 */
import axios, { AxiosInstance, AxiosError } from 'axios'
import {
  UserCreate,
  UserLogin,
  AuthResponse,
  ChatRequest,
  AgentResponse,
  MindMapGraph,
  DialogueNodeBase,
  ErrorResponse,
} from '../types/api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

/**
 * 创建 axios 实例
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * 请求拦截器：添加 JWT token
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器：处理 token 过期
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ErrorResponse>) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

/**
 * 认证 API
 */
export const authAPI = {
  /**
   * 用户注册
   */
  register: async (data: UserCreate): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/register', data)
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token)
    }
    return response.data
  },

  /**
   * 用户登录
   */
  login: async (data: UserLogin): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/login', data)
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token)
    }
    return response.data
  },

  /**
   * 用户登出
   */
  logout: (): void => {
    localStorage.removeItem('access_token')
  },
}

/**
 * 聊天 API
 */
export const chatAPI = {
  /**
   * 发送聊天消息（支持普通提问和划词追问）
   */
  sendMessage: async (data: ChatRequest): Promise<AgentResponse> => {
    const response = await apiClient.post<AgentResponse>('/chat', data)
    return response.data
  },

  /**
   * 获取对话树
   */
  getConversationTree: async (conversationId: string): Promise<DialogueNodeBase> => {
    const response = await apiClient.get<DialogueNodeBase>(
      `/chat/conversation/${conversationId}`
    )
    return response.data
  },
}

/**
 * 知识图谱 API
 */
export const mindMapAPI = {
  /**
   * 获取思维导图数据
   */
  getMindMap: async (conversationId: string): Promise<MindMapGraph> => {
    const response = await apiClient.get<MindMapGraph>(
      `/mindmap/${conversationId}`
    )
    return response.data
  },
}
