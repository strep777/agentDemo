<template>
  <div class="chat-page">
    <!-- 聊天容器 -->
    <div class="chat-container">
      <!-- 左侧对话列表 -->
      <div class="conversation-sidebar">
        <div class="sidebar-header">
          <div class="header-content">
            <h3 class="sidebar-title">对话列表</h3>
            <n-button quaternary circle size="small" @click="showCreateDialog = true" class="new-chat-btn">
              <template #icon>
                <n-icon><Add /></n-icon>
              </template>
            </n-button>
          </div>
        </div>
        
        <div class="conversation-list">
          <div
            v-for="conversation in chatStore.conversations"
            :key="conversation.id"
            class="conversation-item"
            :class="{ active: conversation.id === currentConversationId }"
            @click="selectConversation(conversation)"
          >
            <div class="conversation-info">
              <div class="conversation-title">
                {{ conversation.title || '新对话' }}
              </div>
              <div class="conversation-meta">
                <n-tag size="small" :type="conversation.type === 'agent' ? 'primary' : 'success'" class="conversation-tag">
                  {{ conversation.type === 'agent' ? '智能体' : '模型' }}
                </n-tag>
                <span class="conversation-name">
                  {{ conversation.agent_name || conversation.model_name || '默认模型' }}
                </span>
              </div>
              <div class="conversation-time">
                {{ formatTime(conversation.created_at) }}
              </div>
            </div>
            <div class="conversation-actions">
              <n-button quaternary circle size="small" @click.stop="deleteConversation(conversation.id)" class="delete-btn">
                <template #icon>
                  <n-icon><Trash /></n-icon>
                </template>
              </n-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧聊天区域 -->
      <div class="chat-main">
        <div v-if="!currentConversationId" class="empty-state">
          <div class="empty-content">
            <div class="empty-icon">
              <n-icon size="80" color="var(--n-text-color-4)">
                <ChatbubblesOutline />
              </n-icon>
            </div>
            <h3 class="empty-title">选择一个对话开始聊天</h3>
            <p class="empty-description">或者创建一个新的对话</p>
            <n-button type="primary" size="large" @click="showCreateDialog = true" class="create-btn">
              <template #icon>
                <n-icon><Add /></n-icon>
              </template>
              新建对话
            </n-button>
          </div>
        </div>

        <div v-else class="chat-content">
          <!-- 聊天头部 -->
          <div class="chat-header">
            <div class="chat-info">
              <h3 class="chat-title">
                {{ currentConversation?.title || '新对话' }}
              </h3>
              <div class="chat-meta">
                <n-tag size="small" :type="currentConversation?.type === 'agent' ? 'primary' : 'success'" class="chat-tag">
                  {{ currentConversation?.type === 'agent' ? '智能体' : '模型' }}
                </n-tag>
                <span class="chat-name">
                  {{ currentConversation?.agent_name || currentConversation?.model_name || '默认模型' }}
                </span>
              </div>
            </div>
          </div>

          <!-- 聊天消息区域 -->
          <div class="chat-messages" ref="chatMessagesRef">
            <div
              v-for="message in chatStore.messages"
              :key="message.id"
              class="message-wrapper"
              :class="message.type"
            >
              <!-- 用户消息 -->
              <div v-if="message.type === 'user'" class="user-message">
                <div class="message-content">
                  <div class="message-text">{{ message.content }}</div>
                  
                  <!-- 用户上传的文件 -->
                  <div v-if="message.attachments && message.attachments.length > 0" class="message-attachments">
                    <div 
                      v-for="(attachment, index) in message.attachments" 
                      :key="index"
                      class="attachment-item"
                    >
                      <div class="attachment-info">
                        <n-icon size="16" class="attachment-icon">
                          <Document v-if="attachment.type.startsWith('text/')" />
                          <Image v-else-if="attachment.type.startsWith('image/')" />
                          <Document v-else />
                        </n-icon>
                        <span class="attachment-name">{{ attachment.name }}</span>
                        <span class="attachment-size">{{ formatFileSize(attachment.size) }}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div class="message-time">{{ formatTime(message.created_at) }}</div>
                </div>
                <div class="message-avatar">
                  <n-avatar round size="medium" color="var(--n-primary-color)">
                    <template #default>
                      <n-icon><Person /></n-icon>
                    </template>
                  </n-avatar>
                </div>
              </div>

              <!-- AI消息 -->
              <div v-else-if="message.type === 'assistant'" class="assistant-message">
                <div class="message-avatar">
                  <n-avatar round size="medium" color="var(--n-primary-color)">
                    <template #default>
                      <n-icon><HardwareChip /></n-icon>
                    </template>
                  </n-avatar>
                </div>
                <div class="message-content">
                  <!-- 思考内容切换 - 只在有思考内容时显示 -->
                  <div v-if="hasThinkingContent(message.content)" class="thinking-toggle">
                    <n-button size="small" text @click="toggleThinking(message.id)" class="thinking-btn">
                      <template #icon>
                        <n-icon size="14">
                          <Bulb />
                        </n-icon>
                      </template>
                      {{ showThinking[message.id] ? '隐藏思考过程' : '显示思考过程' }}
                    </n-button>
                  </div>
                  
                  <!-- 思考内容 -->
                  <div v-if="hasThinkingContent(message.content) && showThinking[message.id]" class="thinking-content">
                    <div class="thinking-header">
                      <n-icon size="16" color="var(--n-warning-color)">
                        <Bulb />
                      </n-icon>
                      <span>思考过程</span>
                    </div>
                    <div class="thinking-text" v-html="parseThinkingContent(message.content)"></div>
                  </div>
                  
                  <!-- 回复内容 -->
                  <div class="message-text" v-html="parseMarkdown(getReplyContent(message.content))"></div>
                  <div class="message-time">{{ formatTime(message.created_at) }}</div>
                </div>
              </div>
            </div>

            <!-- 流式消息 -->
            <div v-if="streamingMessage && chatStore.streaming" class="message-wrapper assistant">
              <div class="message-avatar">
                <n-avatar round size="medium" color="var(--n-primary-color)">
                  <template #default>
                    <n-icon><HardwareChip /></n-icon>
                  </template>
                </n-avatar>
              </div>
              <div class="message-content">
                <div class="message-text">
                  {{ streamingMessage }}
                  <span class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </span>
                </div>
              </div>
            </div>

            <!-- AI加载气泡 - 只在没有流式消息且正在流式传输时显示 -->
            <div v-if="chatStore.streaming && !streamingMessage" class="message-wrapper assistant">
              <div class="message-avatar">
                <n-avatar round size="medium" color="var(--n-primary-color)">
                  <template #default>
                    <n-icon><HardwareChip /></n-icon>
                  </template>
                </n-avatar>
              </div>
              <div class="message-content">
                <div class="loading-bubble">
                  <div class="loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span class="loading-text">AI正在思考中...</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="chat-input">
            <!-- 功能工具栏 -->
            <div class="input-toolbar">
              <div class="toolbar-left">
                <!-- 深度思考开关 -->
                <div class="tool-item">
                  <n-switch 
                    v-model:value="showThinkingEnabled" 
                    size="small"
                    class="thinking-switch"
                  >
                    <template #checked>
                      <n-icon size="14"><Bulb /></n-icon>
                    </template>
                    <template #unchecked>
                      <n-icon size="14"><Bulb /></n-icon>
                    </template>
                  </n-switch>
                  <span class="tool-label">深度思考</span>
                </div>
                
                <!-- 模型选择 -->
                <div class="tool-item">
                  <n-select
                    v-model:value="selectedModel"
                    :options="modelOptions"
                    :placeholder="currentConversation?.type === 'model' ? '请选择模型' : '模型选择'"
                    size="small"
                    class="model-select"
                    clearable
                    @update:value="handleModelChange"
                  />
                </div>
              </div>
              
              <div class="toolbar-right">
                <!-- 文件上传 -->
                <div class="tool-item">
                  <n-button 
                    quaternary 
                    size="small" 
                    @click="triggerFileUpload"
                    class="upload-btn"
                  >
                    <template #icon>
                      <n-icon><Attach /></n-icon>
                    </template>
                    上传文件
                  </n-button>
                  <input
                    ref="fileInputRef"
                    type="file"
                    multiple
                    accept=".txt,.md,.pdf,.doc,.docx,.jpg,.jpeg,.png,.gif"
                    @change="handleFileUpload"
                    style="display: none;"
                  />
                </div>
                
                <!-- 图片上传 -->
                <div class="tool-item">
                  <n-button 
                    quaternary 
                    size="small" 
                    @click="triggerImageUpload"
                    class="upload-btn"
                  >
                    <template #icon>
                      <n-icon><Image /></n-icon>
                    </template>
                    上传图片
                  </n-button>
                  <input
                    ref="imageInputRef"
                    type="file"
                    multiple
                    accept="image/*"
                    @change="handleImageUpload"
                    style="display: none;"
                  />
                </div>
              </div>
            </div>
            
            <!-- 已上传文件列表 -->
            <div v-if="uploadedFiles.length > 0" class="uploaded-files">
              <div 
                v-for="(file, index) in uploadedFiles" 
                :key="index"
                class="uploaded-file"
              >
                <div class="file-info">
                  <n-icon size="16" class="file-icon">
                    <Document v-if="file.type.startsWith('text/')" />
                    <Image v-else-if="file.type.startsWith('image/')" />
                    <Document v-else />
                  </n-icon>
                  <span class="file-name">{{ file.name }}</span>
                  <span class="file-size">{{ formatFileSize(file.size) }}</span>
                </div>
                <n-button 
                  quaternary 
                  size="small" 
                  @click="removeFile(index)"
                  class="remove-file-btn"
                >
                  <template #icon>
                    <n-icon><Close /></n-icon>
                  </template>
                </n-button>
              </div>
            </div>
            
            <div class="input-container">
              <div class="message-input">
                <n-input
                  v-model:value="messageText"
                  type="textarea"
                  placeholder="输入消息..."
                  :autosize="{ minRows: 1, maxRows: 4 }"
                  @keydown.enter.prevent="handleSendMessage"
                  class="input-field"
                />
              </div>
              <div class="send-button">
                <n-button
                  type="primary"
                  :disabled="!messageText.trim() || sending"
                  @click="handleSendMessage"
                  class="send-btn"
                >
                  <template #icon>
                    <n-icon><Send /></n-icon>
                  </template>
                  发送
                </n-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建对话对话框 -->
    <n-modal 
      v-model:show="showCreateDialog" 
      preset="card" 
      title="创建新对话" 
      class="create-dialog"
      style="width: 500px; max-width: 90vw;"
    >
      <n-form ref="createFormRef" :model="createForm" :rules="createRules">
        <n-form-item label="对话类型" path="type">
          <n-radio-group v-model:value="createForm.type">
            <n-radio value="agent">智能体对话</n-radio>
            <n-radio value="model">模型对话</n-radio>
          </n-radio-group>
        </n-form-item>
        
        <n-form-item v-if="createForm.type === 'agent'" label="选择智能体" path="agent_id">
          <n-select
            v-model:value="createForm.agent_id"
            :options="agentOptions"
            placeholder="请选择智能体"
            clearable
          />
        </n-form-item>
        
        <n-form-item label="对话标题" path="title">
          <n-input v-model:value="createForm.title" placeholder="请输入对话标题" />
        </n-form-item>
      </n-form>
      
      <template #footer>
        <div class="dialog-footer">
          <n-button @click="showCreateDialog = false">取消</n-button>
          <n-button type="primary" @click="createConversation" :loading="creating">
            创建
          </n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick, computed, watch } from 'vue'
import { Add, Trash, Send, Person, ChatbubblesOutline, Bulb, HardwareChip, Attach, Image, Document, Close } from '@vicons/ionicons5'
import { useChatStore } from '@/stores/chat'
import { useAgentsStore } from '@/stores/agents'
import { useModelsStore } from '@/stores/models'
import { useMessage } from 'naive-ui'
import {
  NButton,
  NIcon,
  NInput,
  NModal,
  NForm,
  NFormItem,
  NSelect,
  NAvatar,
  NTag,
  NRadioGroup,
  NRadio,
  NSwitch
} from 'naive-ui'
import { parseMarkdown, hasThinkingContent, extractThinkingContent } from '@/utils/markdown'
import { config } from '@/config'

const message = useMessage()
const chatStore = useChatStore()
const agentsStore = useAgentsStore()
const modelsStore = useModelsStore()

const currentConversationId = ref<string>('')
const messageText = ref<string>('')
const streamingMessage = ref<string>('')
const showCreateDialog = ref<boolean>(false)
const chatMessagesRef = ref<HTMLElement | null>(null)
const showThinking = ref<Record<string, boolean>>({})
const sending = ref<boolean>(false)
const creating = ref<boolean>(false)
const showThinkingEnabled = ref<boolean>(false)
const selectedModel = ref<string>('')
const uploadedFiles = ref<File[]>([])
const fileInputRef = ref<HTMLInputElement | null>(null)
const imageInputRef = ref<HTMLInputElement | null>(null)
const createForm = reactive({
  type: 'model' as 'agent' | 'model',
  agent_id: '',
  title: ''
})
const createFormRef = ref<any>(null)

const agentOptions = computed(() => {
  return agentsStore.agents.map(agent => ({
    label: agent.name,
    value: agent.id
  }))
})
const modelOptions = computed(() => {
  const validModels = modelsStore.models.filter(model =>
    model && model.id && model.name &&
    (model.status === 'active' || model.status === 'available' || 
     (typeof model.status === 'boolean' && model.status === true))
  )
  return validModels.map(model => ({
    label: model.name, // 只显示模型名称
    value: model.id,
    description: model.description || '',
    provider: model.provider || 'unknown',
    status: model.status,
    server_url: model.server_url
  }))
})
const currentConversation = computed(() => {
  return chatStore.conversations.find(c => c.id === currentConversationId.value) || null
})
const createRules = computed(() => ({
  type: {
    required: true,
    message: '请选择对话类型',
    trigger: 'change'
  },
  agent_id: {
    required: createForm.type === 'agent',
    message: '请选择智能体',
    trigger: 'change'
  },
  title: {
    required: true,
    message: '请输入对话标题',
    trigger: 'blur',
    min: 1,
    max: 50
  }
}))

// 方法
// 添加缺失的验证方法和错误处理方法
const validateMessageInput = () => {
  if (!messageText.value.trim()) {
    message.error('请输入消息内容')
    return false
  }
  
  if (!currentConversationId.value) {
    message.error('请先选择一个对话')
    return false
  }
  
  if (messageText.value.trim().length > 4000) {
    message.error('消息内容过长，请控制在4000字符以内')
    return false
  }
  
  // 检查是否有有效的对话
  const currentConversation = chatStore.conversations.find(c => c.id === currentConversationId.value)
  if (!currentConversation) {
    message.error('当前对话无效，请重新选择对话')
    return false
  }
  
  return true
}

const validateFileUpload = (file: File) => {
  const maxSize = config.upload?.maxSize || 10 * 1024 * 1024 // 默认10MB
  const allowedTypes = config.upload?.allowedTypes || ['.txt', '.md', '.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif']
  
  if (file.size > maxSize) {
    message.error(`文件 ${file.name} 过大，最大支持 ${maxSize / 1024 / 1024}MB`)
    return false
  }
  
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (ext && !allowedTypes.includes('.' + ext)) {
    message.error(`文件类型不支持: ${file.name}`)
    return false
  }
  
  // 检查文件名长度
  if (file.name.length > 100) {
    message.error(`文件名过长: ${file.name}`)
    return false
  }
  
  return true
}

const validateImageUpload = (file: File) => {
  const maxSize = config.upload?.maxSize || 10 * 1024 * 1024 // 默认10MB
  
  if (!file.type.startsWith('image/')) {
    message.error(`文件 ${file.name} 不是有效的图片格式`)
    return false
  }
  
  if (file.size > maxSize) {
    message.error(`图片 ${file.name} 过大，最大支持 ${maxSize / 1024 / 1024}MB`)
    return false
  }
  
  // 检查文件名长度
  if (file.name.length > 100) {
    message.error(`文件名过长: ${file.name}`)
    return false
  }
  
  return true
}

const handleError = (error: any, operation: string) => {
  console.error(`❌ ${operation}失败:`, error)
  
  // 根据错误类型显示不同的错误信息
  if (error.code === 'ECONNABORTED') {
    message.error('请求超时，请检查后端服务是否正常运行')
  } else if (error.code === 'ERR_NETWORK') {
    message.error('网络连接失败，请检查网络连接')
  } else if (error.response?.status === 500) {
    message.error('服务器内部错误，请稍后重试')
  } else if (error.response?.status === 404) {
    message.error('API端点不存在，请检查后端配置')
  } else if (error.response?.status === 401) {
    message.error('认证失败，请重新登录')
  } else if (error.response?.status === 403) {
    message.error('权限不足，请检查用户权限')
  } else if (error.response?.status === 422) {
    message.error('请求参数错误，请检查输入数据')
  } else {
    const errorMessage = error.response?.data?.message || error.message || `${operation}失败`
    message.error(errorMessage)
  }
}

// 优化 selectConversation 错误处理
const selectConversation = async (conversation: any) => {
  if (!conversation?.id) {
    message.error('无效的对话')
    return
  }
  
  try {
    currentConversationId.value = conversation.id
    chatStore.messages = []
    await chatStore.getMessages(conversation.id)
    
    // 根据对话类型设置模型
    if (conversation.type === 'model' && conversation.model_id) {
      selectedModel.value = conversation.model_id
    } else if (conversation.type === 'model') {
      const firstValidModel = modelsStore.models.find(model =>
        model && model.id && model.name &&
        (model.status === 'active' || model.status === 'available' || 
         (typeof model.status === 'boolean' && model.status === true))
      )
      selectedModel.value = firstValidModel ? firstValidModel.id : ''
      if (firstValidModel) {
        try {
          await chatStore.updateConversation(conversation.id, { model_id: firstValidModel.id })
          console.log('✅ 自动设置对话模型:', firstValidModel.name)
        } catch (error) {
          console.warn('⚠️ 自动设置对话模型失败:', error)
        }
      }
    } else {
      selectedModel.value = ''
    }
    
    await nextTick()
    scrollToBottom()
    console.log('✅ 对话选择成功:', conversation.title || conversation.id)
  } catch (error: any) {
    handleError(error, '选择对话')
  }
}

// 优化 handleSendMessage 错误处理
const handleSendMessage = async () => {
  if (!validateMessageInput()) return
  
  const content = messageText.value.trim()
  const files = uploadedFiles.value
  const currentConversation = chatStore.conversations.find(c => c.id === currentConversationId.value)
  
  if (currentConversation?.type === 'model' && !selectedModel.value) {
    message.error('请先选择一个模型')
    return
  }
  
  try {
    const userMessage = {
      id: `user_${Date.now()}`,
      conversation_id: currentConversationId.value,
      content,
      type: 'user' as const,
      attachments: files.map(file => ({
        name: file.name,
        size: file.size,
        type: file.type
      })),
      metadata: {},
      user_id: 'current-user',
      created_at: new Date().toISOString()
    }
    
    // 添加用户消息到列表
    chatStore.messages.push(userMessage)
    
    // 清空输入和文件
    messageText.value = ''
    uploadedFiles.value = []
    sending.value = true
    streamingMessage.value = ''
    
    await nextTick()
    scrollToBottom()
    
    // 开始流式发送
    await chatStore.streamMessage(
      currentConversationId.value,
      content,
      (chunk) => {
        streamingMessage.value += chunk
        scrollToBottom()
      },
      () => {
        streamingMessage.value = ''
        scrollToBottom()
      },
      (error) => {
        message.error(`发送消息失败: ${error}`)
        streamingMessage.value = ''
      },
      {
        files,
        showThinking: showThinkingEnabled.value,
        modelId: selectedModel.value || undefined
      }
    )
  } catch (error: any) {
    handleError(error, '发送消息')
  } finally {
    sending.value = false
  }
}

// 优化 createConversation 错误处理
const createConversation = async () => {
  if (!createFormRef.value) return
  try {
    await createFormRef.value.validate()
  } catch (errors: any) {
    if (errors && errors.length > 0) {
      message.error('请检查表单填写')
      return
    }
  }
  try {
    creating.value = true
    if (createForm.type === 'agent' && createForm.agent_id) {
      const agent = agentsStore.agents.find(a => a.id === createForm.agent_id)
      if (!agent) {
        message.error('选择的智能体不存在')
        return
      }
    }
    const payload: any = {
      type: createForm.type,
      title: createForm.title
    }
    if (createForm.type === 'agent') payload.agent_id = createForm.agent_id
    const result = await chatStore.createConversation(payload)
    if (result) {
      showCreateDialog.value = false
      createForm.type = 'model'
      createForm.agent_id = ''
      createForm.title = ''
      if (result.type === 'model') {
        const firstValidModel = modelsStore.models.find(model =>
          model && model.id && model.name &&
          (model.status === 'active' || model.status === 'available' || 
           (typeof model.status === 'boolean' && model.status === true))
        )
        if (firstValidModel) {
          selectedModel.value = firstValidModel.id
          try {
            await chatStore.updateConversation(result.id, {
              model_id: firstValidModel.id
            })
          } catch (error) {
            // 忽略错误
          }
        }
      }
      selectConversation(result)
      message.success('对话创建成功')
    }
  } catch (error: any) {
    handleError(error, '创建对话')
  } finally {
    creating.value = false
  }
}

// 1. 文件上传功能补全
const triggerFileUpload = () => {
  fileInputRef.value?.click()
}

const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    const files = Array.from(target.files)
    const validFiles = files.filter(validateFileUpload)
    
    if (validFiles.length !== files.length) {
      message.warning(`有 ${files.length - validFiles.length} 个文件不符合要求`)
    }
    
    if (validFiles.length > 0) {
      uploadedFiles.value.push(...validFiles)
      message.success(`成功添加 ${validFiles.length} 个文件`)
    }
    
    target.value = ''
  }
}

const triggerImageUpload = () => {
  imageInputRef.value?.click()
}

const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    const files = Array.from(target.files)
    const validFiles = files.filter(validateImageUpload)
    
    if (validFiles.length !== files.length) {
      message.warning(`有 ${files.length - validFiles.length} 个图片不符合要求`)
    }
    
    if (validFiles.length > 0) {
      uploadedFiles.value.push(...validFiles)
      message.success(`成功添加 ${validFiles.length} 个图片`)
    }
    
    target.value = ''
  }
}

const removeFile = (index: number) => {
  const removedFile = uploadedFiles.value[index]
  uploadedFiles.value.splice(index, 1)
  message.success(`已移除文件: ${removedFile.name}`)
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 2. 思考内容显示功能补全
const parseThinkingContent = (content: string) => {
  const { thinking } = extractThinkingContent(content)
  return parseMarkdown(thinking)
}

const getReplyContent = (content: string) => {
  const { reply } = extractThinkingContent(content)
  return reply
}

const toggleThinking = (messageId: string) => {
  showThinking.value[messageId] = !showThinking.value[messageId]
}

// 3. 模型/智能体切换功能补全
const handleModelChange = async (modelId: string) => {
  console.log('🔄 模型选择变化:', modelId)
  
  if (modelId && currentConversationId.value) {
    const selectedModelData = modelsStore.models.find(m => m.id === modelId)
    if (selectedModelData) {
      console.log('✅ 选择模型:', selectedModelData.name)
      message.success(`已选择模型: ${selectedModelData.name}`)
      
      // 更新对话的模型
      try {
        await chatStore.updateConversation(currentConversationId.value, {
          model_id: modelId
        })
        console.log('✅ 对话模型更新成功')
      } catch (error) {
        console.error('❌ 更新对话模型失败:', error)
        message.error('更新对话模型失败')
      }
    } else {
      console.error('❌ 选择的模型不存在:', modelId)
      message.error('选择的模型不存在')
    }
  } else {
    console.log('🔄 清除模型选择')
    message.info('已清除模型选择')
  }
}

// 4. 流式消息功能补全
const scrollToBottom = () => {
  nextTick(() => {
    if (chatMessagesRef.value) {
      const scrollElement = chatMessagesRef.value
      scrollElement.scrollTop = scrollElement.scrollHeight
    }
  })
}

const forceScrollToBottom = () => {
  nextTick(() => {
    if (chatMessagesRef.value) {
      const scrollElement = chatMessagesRef.value
      scrollElement.scrollTop = scrollElement.scrollHeight
    }
  })
}

// 平滑滚动到底部
const smoothScrollToBottom = () => {
  nextTick(() => {
    if (chatMessagesRef.value) {
      const scrollElement = chatMessagesRef.value
      scrollElement.scrollTo({
        top: scrollElement.scrollHeight,
        behavior: 'smooth'
      })
    }
  })
}

// 5. 对话管理功能补全
const formatTime = (time: string) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

// 优化 deleteConversation 错误处理
const deleteConversation = async (conversationId: string) => {
  if (!conversationId) {
    message.error('无效的对话ID')
    return
  }
  
  try {
    await chatStore.deleteConversation(conversationId)
    
    if (currentConversationId.value === conversationId) {
      const next = chatStore.conversations.find(c => c.id !== conversationId)
      if (next) {
        selectConversation(next)
      } else {
        currentConversationId.value = ''
        chatStore.messages = []
      }
    }
    
    message.success('对话删除成功')
  } catch (error: any) {
    handleError(error, '删除对话')
  }
}

// 优化 initializeData 错误处理
const initializeData = async () => {
  try {
    console.log('🔄 开始初始化聊天页面数据...')
    
    const promises = [
      agentsStore.getAgents(),
      modelsStore.getModels(),
      chatStore.getConversations()
    ]
    
    await Promise.all(promises)
    console.log('✅ 聊天页面数据初始化完成')
    
    // 检查是否有URL参数指定对话
    const urlParams = new URLSearchParams(window.location.search)
    const conversationId = urlParams.get('conversation_id')
    const agentId = urlParams.get('agent_id')
    
    if (conversationId) {
      const conversation = chatStore.conversations.find(c => c.id === conversationId)
      if (conversation) {
        await selectConversation(conversation)
      } else {
        console.warn('⚠️ URL指定的对话不存在:', conversationId)
      }
    } else if (agentId) {
      // 如果有agent_id参数，创建新的智能体对话
      const agent = agentsStore.agents.find(a => a.id === agentId)
      if (agent) {
        createForm.type = 'agent'
        createForm.agent_id = agentId
        createForm.title = `与 ${agent.name} 的对话`
        await createConversation()
      } else {
        console.warn('⚠️ URL指定的智能体不存在:', agentId)
      }
    }
    
    console.log('✅ 聊天页面初始化完成')
  } catch (error: any) {
    handleError(error, '初始化数据')
  }
}

// 生命周期
onMounted(async () => {
  await initializeData()
})

onUnmounted(() => {
  // 清理所有响应式数据
  currentConversationId.value = ''
  messageText.value = ''
  streamingMessage.value = ''
  showCreateDialog.value = false
  showThinking.value = {}
  sending.value = false
  creating.value = false
  showThinkingEnabled.value = false
  selectedModel.value = ''
  uploadedFiles.value = []
  chatStore.messages = []
})

// 监听消息变化，自动滚动到底部
watch(() => chatStore.messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

// 监听流式传输状态
watch(() => chatStore.streaming, (isStreaming) => {
  if (isStreaming) {
    forceScrollToBottom()
  } else {
    streamingMessage.value = ''
  }
})

// 监听流式消息变化
watch(streamingMessage, (newValue) => {
  if (newValue) {
    scrollToBottom()
  }
})

// 监听模型数据变化
watch(() => modelsStore.models, (newModels) => {
  if (selectedModel.value && !newModels.find(m => m.id === selectedModel.value)) {
    selectedModel.value = ''
    console.log('🔄 当前选择的模型已不存在，已清除选择')
  }
}, { deep: true })

// 监听智能体数据变化
watch(() => agentsStore.agents, (newAgents) => {
  console.log('📊 智能体数据更新:', newAgents.length, '个智能体')
}, { deep: true })

// 监听对话列表变化
watch(() => chatStore.conversations, (newConversations) => {
  console.log('📊 对话列表更新:', newConversations.length, '个对话')
}, { deep: true })
</script>

<style scoped>
/* 页面布局 */
.chat-page {
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  background: var(--n-color);
  padding: 16px;
  margin: 0;
  overflow: hidden;
}

/* 聊天容器 */
.chat-container {
  display: flex;
  height: 100%;
  background: var(--n-color);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  min-height: 600px;
  border: 1px solid var(--n-border-color);
  flex: 1;
}

/* 左侧对话列表 */
.conversation-sidebar {
  width: 320px;
  border-right: 1px solid var(--n-border-color);
  display: flex;
  flex-direction: column;
  background: var(--n-color);
  flex-shrink: 0;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid var(--n-border-color);
  background: var(--n-color);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: var(--n-text-color);
}

.new-chat-btn {
  color: var(--n-primary-color);
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.conversation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--n-border-color);
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--n-color);
}

.conversation-item:hover {
  background: var(--n-hover-color);
}

.conversation-item.active {
  background: var(--n-primary-color-1);
  border-left: 3px solid var(--n-primary-color);
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-title {
  font-weight: 500;
  color: var(--n-text-color);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.conversation-tag {
  flex-shrink: 0;
}

.conversation-name {
  font-size: 12px;
  color: var(--n-text-color-3);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-time {
  font-size: 11px;
  color: var(--n-text-color-4);
}

.conversation-actions {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.conversation-item:hover .conversation-actions {
  opacity: 1;
}

.delete-btn {
  color: var(--n-error-color);
}

.delete-btn:hover {
  background: var(--n-error-color-1);
}

/* 右侧聊天区域 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--n-color);
  min-width: 0;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--n-color);
}

.empty-content {
  text-align: center;
  padding: 40px;
}

.empty-icon {
  margin-bottom: 24px;
}

.empty-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--n-text-color);
  margin: 0 0 12px 0;
}

.empty-description {
  font-size: 14px;
  color: var(--n-text-color-3);
  margin: 0 0 24px 0;
}

.create-btn {
  font-weight: 500;
}

/* 聊天内容区域 */
.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--n-color);
  min-height: 0;
}

.chat-header {
  padding: 20px;
  border-bottom: 1px solid var(--n-border-color);
  background: var(--n-color);
  flex-shrink: 0;
}

.chat-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: var(--n-text-color);
}

.chat-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-tag {
  flex-shrink: 0;
}

.chat-name {
  font-size: 14px;
  color: var(--n-text-color-3);
}

/* 聊天消息区域 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  background: var(--n-color);
  min-height: 0;
  scroll-behavior: smooth;
}

.message-wrapper {
  display: flex;
  gap: 12px;
  max-width: 85%;
  margin-bottom: 16px;
  animation: fadeInUp 0.3s ease-out;
}

.message-wrapper.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-wrapper.assistant {
  align-self: flex-start;
}

/* 消息样式 */
.user-message,
.assistant-message {
  display: flex;
  gap: 12px;
  width: 100%;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-text {
  background: var(--n-hover-color);
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  color: var(--n-text-color);
  word-wrap: break-word;
  white-space: pre-wrap;
}

.user-message .message-text {
  background: var(--n-primary-color);
  color: white;
}

.assistant-message .message-text {
  background: var(--n-hover-color);
  color: var(--n-text-color);
}

.message-time {
  font-size: 11px;
  color: var(--n-text-color-4);
  margin-top: 4px;
  text-align: right;
}

.user-message .message-time {
  text-align: right;
}

.assistant-message .message-time {
  text-align: left;
}

/* 附件样式 */
.message-attachments {
  margin-top: 8px;
}

.attachment-item {
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  border-radius: 6px;
  padding: 8px 12px;
  margin-bottom: 4px;
}

.attachment-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.attachment-icon {
  color: var(--n-text-color-3);
  flex-shrink: 0;
}

.attachment-name {
  font-size: 12px;
  color: var(--n-text-color);
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.attachment-size {
  font-size: 11px;
  color: var(--n-text-color-4);
  flex-shrink: 0;
}

/* 思考内容样式 */
.thinking-toggle {
  margin-bottom: 8px;
}

.thinking-btn {
  color: var(--n-warning-color);
  font-size: 12px;
}

.thinking-content {
  background: var(--n-warning-color-1);
  border: 1px solid var(--n-warning-color-2);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
}

.thinking-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 500;
  color: var(--n-warning-color);
}

.thinking-text {
  font-size: 12px;
  line-height: 1.5;
  color: var(--n-text-color);
  opacity: 0.8;
}

/* 流式消息样式 */
.typing-indicator {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  margin-left: 4px;
}

.typing-indicator span {
  width: 4px;
  height: 4px;
  background: var(--n-text-color-3);
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

/* 加载气泡样式 */
.loading-bubble {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--n-hover-color);
  border-radius: 12px;
  color: var(--n-text-color-3);
}

.loading-dots {
  display: flex;
  gap: 2px;
}

.loading-dots span {
  width: 4px;
  height: 4px;
  background: var(--n-text-color-3);
  border-radius: 50%;
  animation: pulse 1.4s infinite ease-in-out;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

.loading-text {
  font-size: 12px;
}

@keyframes dot-pulse {
  0%, 80%, 100% { transform: scale(0.8); opacity: 0.6; }
  40% { transform: scale(1); opacity: 1; }
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes typing {
  0%, 20% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-7px);
  }
  80%, 100% {
    transform: translateY(0px);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.message-wrapper {
  animation: fadeInUp 0.3s ease-out;
}

/* 输入区域 */
.chat-input {
  border-top: 1px solid var(--n-border-color);
  padding: 20px;
  background: var(--n-color);
  flex-shrink: 0;
  min-height: 0;
}

/* 功能工具栏 */
.input-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  border-radius: 8px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tool-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tool-label {
  font-size: 12px;
  color: var(--n-text-color-3);
  font-weight: 500;
}

.thinking-switch {
  --n-color: var(--n-warning-color);
  --n-color-hover: var(--n-warning-color-hover);
}

.model-select {
  min-width: 120px;
}

.upload-btn {
  font-size: 12px;
  padding: 6px 12px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.upload-btn:hover {
  background: var(--n-hover-color);
  transform: translateY(-1px);
}

/* 已上传文件列表 */
.uploaded-files {
  margin-bottom: 16px;
  padding: 12px 16px;
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  border-radius: 8px;
  max-height: 120px;
  overflow-y: auto;
}

.uploaded-file {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  margin-bottom: 8px;
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  border-radius: 6px;
  transition: all 0.2s ease;
}

.uploaded-file:last-child {
  margin-bottom: 0;
}

.uploaded-file:hover {
  background: var(--n-hover-color);
  border-color: var(--n-primary-color);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.file-icon {
  color: var(--n-text-color-3);
  flex-shrink: 0;
}

.file-name {
  font-size: 12px;
  color: var(--n-text-color);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.file-size {
  font-size: 11px;
  color: var(--n-text-color-4);
  flex-shrink: 0;
}

.remove-file-btn {
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.remove-file-btn:hover {
  background: var(--n-error-color-1);
  color: var(--n-error-color);
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  max-width: 100%;
}

.message-input {
  flex: 1;
  min-width: 0;
}

.input-field {
  border-radius: 8px;
  border: 1px solid var(--n-border-color);
  padding: 16px 20px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--n-text-color);
  background-color: var(--n-color);
  transition: all 0.3s ease;
  width: 100%;
  resize: none;
  min-height: 48px;
  max-height: 120px;
}

.input-field:focus {
  outline: none;
  border-color: var(--n-primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.send-button {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.send-btn {
  background: var(--n-primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-weight: 500;
  transition: all 0.3s ease;
  min-width: 80px;
}

.send-btn:hover {
  background: var(--n-primary-color-hover);
  transform: translateY(-1px);
}

.send-btn:disabled {
  background: var(--n-text-color-4);
  cursor: not-allowed;
  transform: none;
}

.typing-indicator {
  display: inline-block;
  width: 6px;
  height: 6px;
  margin-left: 8px;
  background-color: var(--n-text-color-4);
  border-radius: 50%;
  animation: dot-pulse 1.2s infinite ease-in-out;
}

.typing-indicator:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator:nth-child(2) { animation-delay: -0.16s; }
.typing-indicator:nth-child(3) { animation-delay: 0s; }

/* 响应式设计 */
@media (max-width: 1024px) {
  .conversation-sidebar {
    width: 280px;
  }
}

@media (max-width: 768px) {
  .chat-page {
    padding: 8px;
    height: calc(100vh - 80px);
  }
  
  .chat-container {
    flex-direction: column;
    min-height: 500px;
  }
  
  .conversation-sidebar {
    width: 100%;
    height: 200px;
    border-right: none;
    border-bottom: 1px solid var(--n-border-color);
  }
  
  .message-wrapper {
    max-width: 95%;
  }
  
  .chat-messages {
    padding: 16px;
  }
  
  .chat-input {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .chat-page {
    padding: 4px;
  }
  
  .message-wrapper {
    max-width: 100%;
  }
  
  .chat-messages {
    padding: 12px;
  }
  
  .chat-input {
    padding: 12px;
  }
  
  .conversation-sidebar {
    height: 150px;
  }
}

/* 滚动条样式 */
.conversation-list::-webkit-scrollbar,
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.conversation-list::-webkit-scrollbar-track,
.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.conversation-list::-webkit-scrollbar-thumb,
.chat-messages::-webkit-scrollbar-thumb {
  background: var(--n-border-color);
  border-radius: 3px;
}

.conversation-list::-webkit-scrollbar-thumb:hover,
.chat-messages::-webkit-scrollbar-thumb:hover {
  background: var(--n-text-color-3);
}

/* Firefox 滚动条样式 */
.conversation-list,
.chat-messages {
  scrollbar-width: thin;
  scrollbar-color: var(--n-border-color) transparent;
}

/* Markdown 样式 */
.message-text :deep(h1),
.message-text :deep(h2),
.message-text :deep(h3),
.message-text :deep(h4),
.message-text :deep(h5),
.message-text :deep(h6) {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--n-text-color);
}

.message-text :deep(p) {
  margin: 0.5rem 0;
  line-height: 1.6;
  color: var(--n-text-color);
}

.message-text :deep(ul),
.message-text :deep(ol) {
  margin: 0.5rem 0;
  padding-left: 1.25rem;
}

.message-text :deep(li) {
  margin: 0.25rem 0;
  color: var(--n-text-color);
}

.message-text :deep(blockquote) {
  margin: 0.5rem 0;
  padding: 0.5rem 1rem;
  border-left: 4px solid var(--n-primary-color);
  background-color: var(--n-primary-color-1);
  color: var(--n-text-color);
}

.message-text :deep(code) {
  background-color: var(--n-hover-color);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-family: monospace;
  color: var(--n-text-color);
}

.message-text :deep(pre) {
  background-color: var(--n-hover-color);
  padding: 0.75rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin: 0.5rem 0;
}

.message-text :deep(pre code) {
  background-color: transparent;
  padding: 0;
}

.message-text :deep(table) {
  width: 100%;
  margin: 0.5rem 0;
  border-collapse: collapse;
}

.message-text :deep(th),
.message-text :deep(td) {
  border: 1px solid var(--n-border-color);
  padding: 0.5rem 0.75rem;
  text-align: left;
}

.message-text :deep(th) {
  background-color: var(--n-hover-color);
  font-weight: 600;
  color: var(--n-text-color);
}

.message-text :deep(td) {
  color: var(--n-text-color);
}

.message-text :deep(a) {
  color: var(--n-primary-color);
  text-decoration: none;
}

.message-text :deep(a:hover) {
  text-decoration: underline;
}

.message-text :deep(strong) {
  font-weight: 600;
  color: var(--n-text-color);
}

.message-text :deep(em) {
  font-style: italic;
  color: var(--n-text-color);
}

.message-text :deep(strike) {
  text-decoration: line-through;
  color: var(--n-text-color);
}

.message-text :deep(hr) {
  border: none;
  border-top: 1px solid var(--n-border-color);
  margin: 1rem 0;
}

/* 暗色主题特定样式 */
:deep(.n-card) {
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
}

:deep(.n-input) {
  background: var(--n-color);
  border-color: var(--n-border-color);
  color: var(--n-text-color);
}

:deep(.n-input:focus) {
  border-color: var(--n-primary-color);
}

:deep(.n-select) {
  background: var(--n-color);
  border-color: var(--n-border-color);
}

:deep(.n-select .n-base-selection) {
  background: var(--n-color);
  border-color: var(--n-border-color);
}

:deep(.n-modal) {
  background: var(--n-color);
}

:deep(.n-modal .n-card) {
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
}

/* 创建对话对话框特定样式 */
.create-dialog {
  max-width: 500px;
}

.create-dialog :deep(.n-card) {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
}

.create-dialog :deep(.n-card-header) {
  padding: 16px 20px;
  border-bottom: 1px solid var(--n-border-color);
}

.create-dialog :deep(.n-card__content) {
  padding: 20px;
}

.create-dialog :deep(.n-card__footer) {
  padding: 16px 20px;
  border-top: 1px solid var(--n-border-color);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .create-dialog {
    max-width: 95vw;
  }
  
  .create-dialog :deep(.n-card) {
    max-width: 95vw;
    margin: 10px;
  }
  
  .create-dialog :deep(.n-card__content) {
    padding: 16px;
  }
}

:deep(.n-form-item-label) {
  color: var(--n-text-color);
}

:deep(.n-radio) {
  color: var(--n-text-color);
}

:deep(.n-radio-group) {
  color: var(--n-text-color);
}
</style> 