import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api'
import axios from 'axios'
import type { 
  Conversation, 
  Message, 
  PaginationParams,
  PaginatedResponse,
  ApiResponse 
} from '@/types'
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
    let token = localStorage.getItem('token')
    if (!token && import.meta.env.DEV) {
      token = 'dev-token-12345'
      localStorage.setItem('token', token)
    }
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
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
        console.error('❌ 获取对话列表失败:', response.data)
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
        const conversation = response.data.data
        conversations.value.unshift(conversation)
        return conversation
      } else {
        console.error('❌ 创建对话失败:', response.data)
        return null
      }
    } catch (error: any) {
      console.error('❌ 创建对话异常:', error)
      console.error('❌ 错误详情:', error.response?.data)
      throw error // 重新抛出错误以便上层处理
    }
  }

  // 获取对话详情
  const getConversation = async (conversationId: string): Promise<Conversation | null> => {
    try {
      loading.value = true
      const response = await api.chat.conversations.get(conversationId)
      
      if (response.data.success) {
        currentConversation.value = response.data.data
        return response.data.data
      } else {
        return null
      }
    } catch (error: any) {
      console.error('获取对话详情失败:', error)
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
      
      // 由于后端没有专门的更新对话接口，我们直接更新本地数据
      const conversationIndex = conversations.value.findIndex(c => c.id === conversationId)
      if (conversationIndex !== -1) {
        conversations.value[conversationIndex] = {
          ...conversations.value[conversationIndex],
          ...data,
          updated_at: new Date().toISOString()
        }
        console.log('✅ 对话更新成功')
        return conversations.value[conversationIndex]
      } else {
        console.error('❌ 未找到要更新的对话')
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
      const response = await api.chat.conversations.delete(conversationId)
      
      if (response.data.success) {
        await getConversations() // 刷新列表
        return true
      } else {
        return false
      }
    } catch (error: any) {
      console.error('删除对话失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 发送消息
  const sendMessage = async (conversationId: string, content: string, attachments: any[] = []): Promise<Message | null> => {
    try {
      loading.value = true
      const response = await instance.post<ApiResponse<Message>>(`/conversations/${conversationId}/messages`, {
        content,
        type: 'user',
        attachments,
        metadata: {}
      })
      
      if (response.data.success) {
        // 添加用户消息到列表
        messages.value.push(response.data.data)
        
        // 获取AI回复
        const aiResponse = await instance.post<ApiResponse<{
          user_message_id: string
          ai_message_id: string
          ai_response: string
        }>>('/chat/send', {
          conversation_id: conversationId,
          content
        })
        
        if (aiResponse.data.success) {
          // 添加AI消息到列表
          const aiMessage: Message = {
            id: aiResponse.data.data.ai_message_id,
            conversation_id: conversationId,
            content: aiResponse.data.data.ai_response,
            type: 'assistant',
            attachments: [],
            metadata: {},
            user_id: getCurrentUserId(),
            created_at: new Date().toISOString()
          }
          messages.value.push(aiMessage)
          return aiMessage
        } else {
          return null
        }
      } else {
        return null
      }
    } catch (error: any) {
      console.error('发送消息失败:', error)
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
      const baseURL = '/api'  // 使用代理路径（通过Vite代理）
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
      
      console.log('🔍 发送流式请求到:', `${baseURL}/chat/stream`)
      console.log('🔍 请求数据:', requestData)
      
      const response = await fetch(`${baseURL}/chat/stream`, {
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
      let thinking = ""
      let reply = ""
      let currentSection = "reply" // 默认在回复部分
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
                console.log('📊 解析的数据:', data)
                
                if (data.error) {
                  console.error('❌ 流式生成错误:', data.error)
                  onError?.(data.error)
                  return
                }
                
                if (data.chunk) {
                  fullResponse += data.chunk
                  
                  // 解析思考过程和回复
                  const chunkText = data.chunk
                  
                  // 检查是否包含 <think> 标签
                  if (chunkText.includes('<think>')) {
                    currentSection = "thinking"
                    const parts = chunkText.split('<think>')
                    if (parts.length > 1) {
                      thinking += parts[1]
                    }
                  } else if (chunkText.includes('</think>')) {
                    currentSection = "reply"
                    const parts = chunkText.split('</think>')
                    if (parts.length > 1) {
                      reply += parts[1]
                    }
                  } else {
                    // 根据当前部分添加内容
                    if (currentSection === "thinking") {
                      thinking += chunkText
                    } else {
                      reply += chunkText
                    }
                  }
                  
                  onChunk?.(data.chunk)
                }
                
                if (data.done) {
                  console.log('✅ 流式生成完成，总长度:', fullResponse.length)
                  
                  // 添加AI消息到列表
                  const aiMessage: Message = {
                    id: data.message_id || `ai_${Date.now()}`,
                    conversation_id: conversationId,
                    content: fullResponse,
                    type: 'assistant',
                    attachments: [],
                    metadata: {},
                    user_id: getCurrentUserId(),
                    created_at: new Date().toISOString()
                  }
                  messages.value.push(aiMessage)
                  console.log('✅ AI消息已添加到列表')
                  onComplete?.(aiMessage)
                  break
                }
              } catch (e) {
                console.error('❌ 解析流式数据失败:', e, line)
              }
            }
          }
        }
      } catch (error: any) {
        console.error('❌ 读取流式响应失败:', error)
        onError?.(error.message || '读取响应流失败')
      } finally {
        streaming.value = false
      }
    } catch (error: any) {
      console.error('❌ 流式消息发送失败:', error)
      onError?.(error.message || '流式消息发送失败')
      streaming.value = false
    }
  }

  // 获取消息列表
  const getMessages = async (conversationId: string, params: PaginationParams = {}) => {
    try {
      loading.value = true
      console.log('🔍 获取消息列表:', conversationId, params)
      
      const response = await instance.get<ApiResponse<Message[]>>(`/chat/conversations/${conversationId}/messages`, { 
        params: {
          page: params.page || 1,
          page_size: params.page_size || 50
        }
      })
      
      console.log('🔍 消息列表响应:', response.data)
      
      if (response.data.success) {
        messages.value = response.data.data
        console.log('✅ 获取消息列表成功，消息数量:', messages.value.length)
      } else {
        console.error('❌ 获取消息列表失败:', response.data.message)
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
      } else {
        console.error(`获取消息列表失败: ${error.message || '未知错误'}`)
      }
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