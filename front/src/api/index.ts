import axios from 'axios'
import { config } from '@/config'

// 创建axios实例
const instance = axios.create({
  baseURL: config.api.baseURL,  // 使用统一配置
  timeout: config.api.timeout,  // 使用统一配置
  headers: config.api.headers
})

// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等认证信息
    let token = localStorage.getItem('token')
    console.log('🔧 从localStorage获取token:', token)
    console.log('🔧 开发环境:', import.meta.env.DEV)
    
    // 开发环境如果没有token，使用默认token
    if (!token && import.meta.env.DEV) {
      token = 'dev-token-12345'
      localStorage.setItem('token', token)
      console.log('🔧 开发环境：设置默认token:', token)
    }
    
    // 开发环境：检查是否有skip_login_token标记
    if (import.meta.env.DEV && localStorage.getItem('skip_login_token')) {
      token = 'dev-token-12345'
      localStorage.setItem('token', token)
      console.log('🔧 开发环境：使用跳过登录token:', token)
    }
    
    // 开发环境：如果token是skip_login_token，替换为正确的开发token
    if (import.meta.env.DEV && token === 'skip_login_token') {
      token = 'dev-token-12345'
      localStorage.setItem('token', token)
      console.log('🔧 开发环境：替换skip_login_token为dev-token-12345')
    }
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('🔑 设置认证头:', `Bearer ${token}`)
    } else {
      console.log('⚠️ 没有找到token')
    }
    
    // 调试信息
    console.log('API Request:', config.method?.toUpperCase(), config.url)
    console.log('Authorization Header:', config.headers.Authorization)
    console.log('所有请求头:', config.headers)
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error)
    // 直接返回错误，不使用模拟数据
    return Promise.reject(error)
  }
)

// API接口定义
export const api = {
  // 代理相关
  agents: {
    list: (params?: any) => instance.get('/agents', { params }),
    get: (id: string) => instance.get(`/agents/${id}`),
    create: (data: any) => instance.post('/agents', data),
    update: (id: string, data: any) => instance.put(`/agents/${id}`, data),
    delete: (id: string) => instance.delete(`/agents/${id}`),
    stats: (id: string) => instance.get(`/agents/${id}/stats`),
    conversations: (id: string) => instance.get(`/agents/${id}/conversations`)
  },

  // 聊天相关
  chat: {
    send: (data: any) => instance.post('/chat/send', data),
    stream: (data: any) => instance.post('/chat/stream', data),
    history: () => instance.get('/chat/history'),
    conversations: {
      list: () => instance.get('/chat/conversations'),
      get: (id: string) => instance.get(`/chat/conversations/${id}`),
      create: (data: any) => instance.post('/chat/conversations', data),
      update: (id: string, data: any) => instance.put(`/chat/conversations/${id}`, data),
      delete: (id: string) => instance.delete(`/chat/conversations/${id}`),
      messages: (id: string) => instance.get(`/chat/conversations/${id}/messages`)
    }
  },

  // 知识库相关
  knowledge: {
    list: () => instance.get('/knowledge'),
    get: (id: string) => instance.get(`/knowledge/${id}`),
    create: (data: any) => instance.post('/knowledge', data),
    update: (id: string, data: any) => instance.put(`/knowledge/${id}`, data),
    delete: (id: string) => instance.delete(`/knowledge/${id}`),
    upload: (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      return instance.post('/knowledge/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    },
    rebuildIndex: (id: string) => instance.post(`/knowledge/${id}/rebuild-index`),
    documents: {
      list: (id: string) => instance.get(`/knowledge/${id}/documents`),
      upload: (id: string, file: File) => {
        const formData = new FormData()
        formData.append('file', file)
        return instance.post(`/knowledge/${id}/documents`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
      },
      delete: (id: string, docId: string) => instance.delete(`/knowledge/${id}/documents/${docId}`)
    }
  },

  // 工作流相关
  workflows: {
    list: (params?: any) => instance.get('/workflows', { params }),
    get: (id: string) => instance.get(`/workflows/${id}`),
    create: (data: any) => instance.post('/workflows', data),
    update: (id: string, data: any) => instance.put(`/workflows/${id}`, data),
    delete: (id: string) => instance.delete(`/workflows/${id}`),
    execute: (id: string, data: any) => instance.post(`/workflows/${id}/execute`, data),
    publish: (id: string, data: any) => instance.post(`/workflows/${id}/publish`, data),
    getNodeTypes: () => instance.get('/workflows/node-types'),
    validate: (data: any) => instance.post('/workflows/validate', data),
    getExecutions: (id: string) => instance.get(`/workflows/${id}/executions`),
    getExecutionDetail: (executionId: string) => instance.get(`/workflows/executions/${executionId}`)
  },

  // 插件相关
  plugins: {
    list: (params?: any) => instance.get('/plugins', { params }),
    get: (id: string) => instance.get(`/plugins/${id}`),
    create: (data: any) => instance.post('/plugins', data),
    update: (id: string, data: any) => instance.put(`/plugins/${id}`, data),
    delete: (id: string) => instance.delete(`/plugins/${id}`),
    toggleStatus: (id: string) => instance.put(`/plugins/${id}/toggle`),
    test: (id: string, data: any) => instance.post(`/plugins/${id}/test`, data),
    execute: (id: string, data: any) => instance.post(`/plugins/${id}/execute`, data),
    upload: (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      return instance.post('/plugins/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    },
    download: (id: string) => instance.get(`/plugins/${id}/download`),
    getConfig: (id: string) => instance.get(`/plugins/${id}/config`),
    updateConfig: (id: string, config: any) => instance.put(`/plugins/${id}/config`, { config }),
    getAvailable: () => instance.get('/plugins/available'),
    batchDelete: (ids: string[]) => instance.post('/plugins/batch-delete', { plugin_ids: ids }),
    batchEnable: (ids: string[]) => instance.post('/plugins/batch-enable', { plugin_ids: ids }),
    batchDisable: (ids: string[]) => instance.post('/plugins/batch-disable', { plugin_ids: ids }),
    // 市场相关
    getMarket: () => instance.get('/plugins/market'),
    searchMarket: (query: string) => instance.get('/plugins/search', { params: { q: query } }),
    installFromMarket: (pluginId: string) => instance.post(`/plugins/market/${pluginId}/install`)
  },

  // 模型相关
  models: {
    list: () => instance.get('/models'),
    get: (id: string) => instance.get(`/models/${id}`),
    create: (data: any) => instance.post('/models', data),
    update: (id: string, data: any) => instance.put(`/models/${id}`, data),
    delete: (id: string) => instance.delete(`/models/${id}`),
    test: (id: string, data: any) => instance.post(`/models/${id}/test`, data),
    download: (id: string) => instance.get(`/models/${id}/download`),
    // Ollama相关
    checkOllamaHealth: (serverUrl?: string) => instance.get('/models/ollama/health', { 
      params: serverUrl ? { server_url: serverUrl } : {} 
    }),
    getOllamaModels: (serverUrl?: string) => instance.get('/models/ollama/models', { 
      params: serverUrl ? { server_url: serverUrl } : {} 
    }),
    pullOllamaModel: (modelName: string, serverUrl?: string) => instance.post('/models/ollama/pull', {
      model_name: modelName,
      server_url: serverUrl || 'http://localhost:11434'
    }),
    testOllamaModel: (modelName: string, prompt: string, serverUrl?: string) => instance.post('/models/ollama/test', {
      model_name: modelName,
      prompt: prompt,
      server_url: serverUrl || 'http://localhost:11434'
    }),
    // 模型管理
    batchDelete: (ids: string[]) => instance.post('/models/batch-delete', { model_ids: ids }),
    batchEnable: (ids: string[]) => instance.post('/models/batch-enable', { model_ids: ids }),
    batchDisable: (ids: string[]) => instance.post('/models/batch-disable', { model_ids: ids }),
    // 模型验证
    validate: (data: any) => instance.post('/models/validate', data),
    // 模型导入导出
    export: (id: string) => instance.get(`/models/${id}/export`),
    import: (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      return instance.post('/models/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    }
  },

  // 训练相关
  training: {
    list: () => instance.get('/training'),
    get: (id: string) => instance.get(`/training/${id}`),
    create: (data: any) => instance.post('/training', data),
    update: (id: string, data: any) => instance.put(`/training/${id}`, data),
    delete: (id: string) => instance.delete(`/training/${id}`),
    start: (id: string) => instance.post(`/training/${id}/start`),
    stop: (id: string) => instance.post(`/training/${id}/stop`)
  },

  // 仪表板相关
  dashboard: {
    stats: () => instance.get('/dashboard/stats'),
    analytics: () => instance.get('/dashboard/analytics'),
    recent: () => instance.get('/dashboard/recent')
  },

  // 设置相关
  settings: {
    get: () => instance.get('/settings'),
    update: (data: any) => instance.put('/settings', data),
    system: {
      get: () => instance.get('/settings/system'),
      update: (data: any) => instance.post('/settings/system', data)
    },
    notifications: {
      get: () => instance.get('/settings/notifications'),
      update: (data: any) => instance.post('/settings/notifications', data)
    },
    export: (type: string) => instance.get(`/settings/export/${type}`),
    clear: (type: string) => instance.delete(`/settings/clear/${type}`),
    clearAll: () => instance.delete('/settings/clear/all')
  },

  // 认证相关
  auth: {
    login: (credentials: any) => instance.post('/auth/login', credentials),
    register: (userData: any) => instance.post('/auth/register', userData),
    logout: () => instance.post('/auth/logout'),
    profile: () => instance.get('/auth/profile'),
    updateProfile: (data: any) => instance.put('/auth/profile', data),
    refresh: () => instance.post('/auth/refresh'),
    changePassword: (data: any) => instance.post('/auth/change-password', data)
  }
}

export default api 