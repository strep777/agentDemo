import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api'
import { getBackendURL, config } from '@/config'
import axios from 'axios'
import type { 
  Conversation, 
  Message, 
  PaginationParams,
  PaginatedResponse,
  ApiResponse 
} from '@/types'

// 创建axios实例
const instance = axios.create({
  baseURL: getBackendURL(),  // 使用后端地址
  timeout: config.api.timeout,  // 使用统一配置
  headers: config.api.headers
})

// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    let token = localStorage.getItem('token')
    if (!token && import.meta.env.DEV) {
      token = 'dev-token-12345'
      localStorage.setItem('token', token)
    }
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 添加API路径前缀
    if (!config.url?.startsWith('/api')) {
      config.url = `/api${config.url}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

export const useChatStore = defineStore('chat', () => {
  // 状态
  const conversations = ref<Conversation[]>([])
  const currentConversation = ref<Conversation | null>(null)
  const messages = ref<Message[]>([])
  const loading = ref(false)
  const streaming = ref(false)
  const pagination = ref({
    page: 1,
    page_size: 20,
    total: 0,
    pages: 0
  })

  // 获取当前用户ID
  const getCurrentUserId = (): string => {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        const user = JSON.parse(userStr)
        return user.id || ''
      } catch {
        return ''
      }
    }
    return ''
  }

  // 计算属性
  const activeConversations = computed(() => 
    conversations.value.filter(conv => conv.status === 'active')
  )

  const archivedConversations = computed(() => 
    conversations.value.filter(conv => conv.status === 'archived')
  )

  // 获取对话列表
  const getConversations = async (params: PaginationParams = {}) => {
    try {
      loading.value = true
      console.log('🔍 开始获取对话列表...')
      const response = await api.chat.conversations.list()
      
      if (response.data.success) {
        // 修复：正确处理嵌套的data字段
        conversations.value = response.data.data.data || response.data.data
        pagination.value = {
          page: response.data.data.page || 1,
          page_size: response.data.data.page_size || 20,
          total: response.data.data.total || conversations.value.length,
          pages: response.data.data.pages || 1
        }
        console.log('✅ 获取对话列表成功:', conversations.value.length, '个对话')
      } else {
        console.error('❌ 获取对话列表失败:', response.data.message)
        conversations.value = []
      }
    } catch (error: any) {
      console.error('❌ 获取对话列表异常:', error)
      
      // 根据错误类型显示不同的错误信息
      if (error.code === 'ECONNABORTED') {
        console.error('请求超时，请检查后端服务是否正常运行')
      } else if (error.code === 'ERR_NETWORK') {
        console.error('网络连接失败，请检查网络连接')
      } else if (error.response?.status === 500) {
        console.error('服务器内部错误，请稍后重试')
      } else if (error.response?.status === 404) {
        console.error('API端点不存在，请检查后端配置')
      } else if (error.response?.status === 401) {
        console.error('认证失败，请重新登录')
      } else if (error.response?.status === 403) {
        console.error('权限不足，请检查用户权限')
      } else {
        console.error(`获取对话列表失败: ${error.message || '未知错误'}`)
      }
      
      conversations.value = []
    } finally {
      loading.value = false
    }
  }

  // 创建对话
  const createConversation = async (data: { 
    type: 'agent' | 'model'
    agent_id?: string
    title?: string 
  }): Promise<Conversation | null> => {
    try {
      console.log('🔍 创建对话，发送数据:', data)
      const response = await api.chat.conversations.create(data)
      console.log('📊 创建对话响应:', response)
      
      if (response.data.success) {
        console.log('✅ 对话创建成功')
        const conversation = response.data.data
        conversations.value.unshift(conversation)
        return conversation
      } else {
        console.error('❌ 创建对话失败:', response.data.message)
        return null
      }
    } catch (error: any) {
      console.error('❌ 创建对话异常:', error)
      
      // 根据错误类型显示不同的错误信息
      if (error.code === 'ECONNABORTED') {
        console.error('请求超时，请检查后端服务是否正常运行')
      } else if (error.code === 'ERR_NETWORK') {
        console.error('网络连接失败，请检查网络连接')
      } else if (error.response?.status === 500) {
        console.error('服务器内部错误，请稍后重试')
      } else if (error.response?.status === 404) {
        console.error('API端点不存在，请检查后端配置')
      } else if (error.response?.status === 401) {
        console.error('认证失败，请重新登录')
      } else if (error.response?.status === 403) {
        console.error('权限不足，请检查用户权限')
      } else if (error.response?.status === 422) {
        console.error('请求参数错误，请检查输入数据')
      } else {
        console.error(`创建对话失败: ${error.message || '未知错误'}`)
      }
      
      throw error // 重新抛出错误以便上层处理
    }
  }

  // 获取对话详情
  const getConversation = async (conversationId: string): Promise<Conversation | null> => {
    try {
      loading.value = true
      console.log('🔍 获取对话详情:', conversationId)
      
      const response = await api.chat.conversations.get(conversationId)
      
      if (response.data.success) {
        console.log('✅ 获取对话详情成功')
        currentConversation.value = response.data.data
        return response.data.data
      } else {
        console.error('❌ 获取对话详情失败:', response.data.message)
        return null
      }
    } catch (error: any) {
      console.error('❌ 获取对话详情异常:', error)
      
      // 根据错误类型显示不同的错误信息
      if (error.code === 'ECONNABORTED') {
        console.error('请求超时，请检查后端服务是否正常运行')
      } else if (error.code === 'ERR_NETWORK') {
        console.error('网络连接失败，请检查网络连接')
      } else if (error.response?.status === 500) {
        console.error('服务器内部错误，请稍后重试')
      } else if (error.response?.status === 404) {
        console.error('API端点不存在，请检查后端配置')
      } else if (error.response?.status === 401) {
        console.error('认证失败，请重新登录')
      } else if (error.response?.status === 403) {
        console.error('权限不足，请检查用户权限')
      } else {
        console.error(`获取对话详情失败: ${error.message || '未知错误'}`)
      }
      
      return null
    } finally {
      loading.value = false
    }
  }

  // 更新对话
  const updateConversation = async (conversationId: string, data: Partial<Conversation>): Promise<Conversation | null> => {
    try {
      loading.value = true
      console.log('🔍 更新对话:', conversationId, data)
      
      const response = await api.chat.conversations.update(conversationId, data)
      
      if (response.data.success) {
        // 更新本地数据
        const conversationIndex = conversations.value.findIndex(c => c.id === conversationId)
        if (conversationIndex !== -1) {
          conversations.value[conversationIndex] = {
            ...conversations.value[conversationIndex],
            ...response.data.data
          }
        }
        console.log('✅ 对话更新成功')
        return response.data.data
      } else {
        console.error('❌ 对话更新失败:', response.data.message)
        return null
      }
    } catch (error: any) {
      console.error('更新对话失败:', error)
      return null
    } finally {
      loading.value = false
    }
  }

  // 删除对话
  const deleteConversation = async (conversationId: string): Promise<boolean> => {
    try {
      loading.value = true
      console.log('🗑️ 开始删除对话:', conversationId)
      
      const response = await api.chat.conversations.delete(conversationId)
      
      if (response.data.success) {
        console.log('✅ 对话删除成功')
        await getConversations() // 刷新列表
        return true
      } else {
        console.error('❌ 删除对话失败:', response.data.message)
        return false
      }
    } catch (error: any) {
      console.error('❌ 删除对话异常:', error)
      
      // 根据错误类型显示不同的错误信息
      if (error.code === 'ECONNABORTED') {
        console.error('请求超时，请检查后端服务是否正常运行')
      } else if (error.code === 'ERR_NETWORK') {
        console.error('网络连接失败，请检查网络连接')
      } else if (error.response?.status === 500) {
        console.error('服务器内部错误，请稍后重试')
      } else if (error.response?.status === 404) {
        console.error('API端点不存在，请检查后端配置')
      } else if (error.response?.status === 401) {
        console.error('认证失败，请重新登录')
      } else if (error.response?.status === 403) {
        console.error('权限不足，请检查用户权限')
      } else {
        console.error(`删除对话失败: ${error.message || '未知错误'}`)
      }
      
      return false
    } finally {
      loading.value = false
    }
  }

  // 发送消息
  const sendMessage = async (conversationId: string, content: string, attachments: any[] = []): Promise<Message | null> => {
    try {
      loading.value = true
      console.log('📤 开始发送消息:', conversationId, content)
      
      const response = await api.chat.send({
        conversation_id: conversationId,
        content,
        attachments,
        metadata: {}
      })
      
      if (response.data.success) {
        console.log('✅ 消息发送成功')
        
        // 添加用户消息到列表
        const userMessage: Message = {
          id: response.data.data.user_message_id,
          conversation_id: conversationId,
          content,
          type: 'user',
          attachments,
          metadata: {},
          user_id: getCurrentUserId(),
          created_at: new Date().toISOString()
        }
        messages.value.push(userMessage)
        
        // 添加AI消息到列表
        const aiMessage: Message = {
          id: response.data.data.ai_message_id,
          conversation_id: conversationId,
          content: response.data.data.response,
          type: 'assistant',
          attachments: [],
          metadata: {},
          user_id: 'ai',
          created_at: new Date().toISOString()
        }
        messages.value.push(aiMessage)
        return aiMessage
      } else {
        console.error('❌ 发送消息失败:', response.data.message)
        return null
      }
    } catch (error: any) {
      console.error('❌ 发送消息异常:', error)
      
      // 根据错误类型显示不同的错误信息
      if (error.code === 'ECONNABORTED') {
        console.error('请求超时，请检查后端服务是否正常运行')
      } else if (error.code === 'ERR_NETWORK') {
        console.error('网络连接失败，请检查网络连接')
      } else if (error.response?.status === 500) {
        console.error('服务器内部错误，请稍后重试')
      } else if (error.response?.status === 404) {
        console.error('API端点不存在，请检查后端配置')
      } else if (error.response?.status === 401) {
        console.error('认证失败，请重新登录')
      } else if (error.response?.status === 403) {
        console.error('权限不足，请检查用户权限')
      } else if (error.response?.status === 422) {
        console.error('请求参数错误，请检查输入数据')
      } else {
        console.error(`发送消息失败: ${error.message || '未知错误'}`)
      }
      
      return null
    } finally {
      loading.value = false
    }
  }

  // 流式发送消息 - 修复版本
  const streamMessage = async (conversationId: string, content: string, 
                             onChunk?: (chunk: string) => void,
                             onComplete?: (message: Message) => void,
                             onError?: (error: string) => void,
                             options?: {
                               files?: File[]
                               showThinking?: boolean
                               modelId?: string
                             }) => {
    try {
      streaming.value = true
      console.log('🔄 开始流式发送消息:', conversationId, content)
      console.log('🔧 选项:', options)
      
      // 处理文件附件
      const attachments = options?.files?.map(file => ({
        name: file.name,
        size: file.size,
        type: file.type,
        data: file
      })) || []
      
      // 注意：用户消息已经在前端添加，这里只处理AI回复
      console.log('✅ 准备发送流式请求')
      
      // 流式获取AI回复
      const baseURL = getBackendURL()  // 使用后端地址
      const token = localStorage.getItem('token') || 'dev-token-12345'
      
      // 构建请求数据
      const requestData: any = {
        conversation_id: conversationId,
        content
      }
      
      // 添加深度思考设置
      if (options?.showThinking) {
        requestData.show_thinking = true
      }
      
      // 添加模型选择
      if (options?.modelId) {
        requestData.model_id = options.modelId
      }
      
      // 添加文件附件
      if (options?.files && options.files.length > 0) {
        requestData.attachments = attachments
      }
      
      console.log('🔍 发送流式请求到:', `${baseURL}/api/chat/stream`)
      console.log('🔍 请求数据:', requestData)
      
      const response = await fetch(`${baseURL}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestData)
      })
      
      console.log('🔍 响应状态:', response.status, response.statusText)
      console.log('🔍 响应头:', Object.fromEntries(response.headers.entries()))
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('❌ 流式请求失败:', response.status, errorText)
        const errorMessage = `流式请求失败: ${response.status} - ${errorText}`
        onError?.(errorMessage)
        return
      }
      
      const reader = response.body?.getReader()
      if (!reader) {
        console.error('❌ 无法读取响应流')
        onError?.('无法读取响应流')
        return
      }
      
      let fullResponse = ""
      const decoder = new TextDecoder()
      
      console.log('🔄 开始读取流式响应...')
      
      try {
        while (true) {
          const { done, value } = await reader.read()
          
          if (done) {
            console.log('✅ 流式响应读取完成')
            break
          }
          
          const chunk = decoder.decode(value)
          console.log('📦 收到数据块:', chunk)
          
          const lines = chunk.split('\n')
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))
                
                if (data.chunk) {
                  fullResponse += data.chunk
                  onChunk?.(data.chunk)
                }
                
                if (data.done) {
                  console.log('✅ 流式传输完成')
                  
                  // 检查是否有错误
                  if (data.error) {
                    console.error('❌ 流式传输错误:', data.error)
                    onError?.(data.error)
                    return
                  }
                  
                  // 创建AI消息对象
                  const aiMessage: Message = {
                    id: data.message_id || `ai_${Date.now()}`,
                    conversation_id: conversationId,
                    content: fullResponse,
                    type: 'assistant',
                    attachments: [],
                    metadata: {},
                    user_id: 'ai',
                    created_at: new Date().toISOString()
                  }
                  
                  // 添加到消息列表
                  messages.value.push(aiMessage)
                  
                  onComplete?.(aiMessage)
                  break
                }
              } catch (parseError) {
                console.warn('⚠️ 解析流式数据失败:', parseError, line)
              }
            } else if (line.trim() !== '') {
              // 处理非空行但不是data格式的情况
              console.log('📝 收到非data格式行:', line)
            }
          }
        }
      } catch (streamError) {
        console.error('❌ 读取流式响应失败:', streamError)
        onError?.(`读取流式响应失败: ${streamError}`)
      } finally {
        reader.releaseLock()
      }
      
    } catch (error: any) {
      console.error('❌ 流式发送消息失败:', error)
      
      // 根据错误类型提供不同的错误信息
      let errorMessage = '发送消息失败'
      
      if (error.code === 'ECONNABORTED') {
        errorMessage = '请求超时，请检查后端服务是否正常运行'
      } else if (error.code === 'ERR_NETWORK') {
        errorMessage = '网络连接失败，请检查网络连接'
      } else if (error.response?.status === 500) {
        errorMessage = '服务器内部错误，请稍后重试'
      } else if (error.response?.status === 404) {
        errorMessage = 'API端点不存在，请检查后端配置'
      } else if (error.response?.status === 401) {
        errorMessage = '认证失败，请重新登录'
      } else if (error.response?.status === 403) {
        errorMessage = '权限不足，请检查用户权限'
      } else if (error.response?.status === 422) {
        errorMessage = '请求参数错误，请检查输入数据'
      } else {
        errorMessage = error.response?.data?.message || error.message || '发送消息失败'
      }
      
      onError?.(errorMessage)
    } finally {
      streaming.value = false
    }
  }

  // 获取消息列表
  const getMessages = async (conversationId: string, params: PaginationParams = {}) => {
    try {
      loading.value = true
      console.log('🔍 获取消息列表:', conversationId, params)
      
      const response = await api.chat.conversations.messages(conversationId)
      
      console.log('🔍 消息列表响应:', response.data)
      
      if (response.data.success) {
        console.log('✅ 获取消息列表成功，消息数量:', response.data.data.length)
        messages.value = response.data.data
      } else {
        console.error('❌ 获取消息列表失败:', response.data.message)
        messages.value = []
      }
    } catch (error: any) {
      console.error('❌ 获取消息列表异常:', error)
      
      // 根据错误类型显示不同的错误信息
      if (error.code === 'ECONNABORTED') {
        console.error('请求超时，请检查后端服务是否正常运行')
      } else if (error.code === 'ERR_NETWORK') {
        console.error('网络连接失败，请检查网络连接')
      } else if (error.response?.status === 500) {
        console.error('服务器内部错误，请稍后重试')
      } else if (error.response?.status === 404) {
        console.error('API端点不存在，请检查后端配置')
      } else if (error.response?.status === 401) {
        console.error('认证失败，请重新登录')
      } else if (error.response?.status === 403) {
        console.error('权限不足，请检查用户权限')
      } else {
        console.error(`获取消息列表失败: ${error.message || '未知错误'}`)
      }
      
      messages.value = []
    } finally {
      loading.value = false
    }
  }

  // 清空当前对话
  const clearCurrentConversation = () => {
    currentConversation.value = null
    messages.value = []
  }

  // 重置状态
  const reset = () => {
    conversations.value = []
    currentConversation.value = null
    messages.value = []
    loading.value = false
    streaming.value = false
    pagination.value = {
      page: 1,
      page_size: 20,
      total: 0,
      pages: 0
    }
  }

  return {
    // 状态
    conversations,
    currentConversation,
    messages,
    loading,
    streaming,
    pagination,
    
    // 计算属性
    activeConversations,
    archivedConversations,
    
    // 方法
    getConversations,
    createConversation,
    getConversation,
    updateConversation,
    deleteConversation,
    sendMessage,
    streamMessage,
    getMessages,
    clearCurrentConversation,
    reset
  }
}) 