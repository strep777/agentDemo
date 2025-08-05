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
                  {{ conversation.agent_name || conversation.model_name || '未知' }}
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
                  {{ currentConversation?.agent_name || currentConversation?.model_name || '未知' }}
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
              <div v-else-if="message.type === 'assistant'" class="ai-message">
                <div class="message-avatar">
                  <n-avatar round size="medium" color="var(--n-primary-color)">
                    <template #default>
                      <n-icon><HardwareChip /></n-icon>
                    </template>
                  </n-avatar>
                </div>
                <div class="message-content">
                  <!-- 思考内容切换 -->
                  <div v-if="hasThinkingContent(message.content)" class="thinking-toggle">
                    <n-button size="small" text @click="toggleThinking(message.id)">
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
import { ref, reactive, onMounted, nextTick, computed, watch } from 'vue'
import { Add, Trash, Send, Person, ServerOutline, ChatbubblesOutline, Bulb, HardwareChip, Attach, Image, Document, Close } from '@vicons/ionicons5'
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
  NSpace,
  NAvatar,
  NTag,
  NRadioGroup,
  NRadio,
  NSwitch
} from 'naive-ui'
import { parseMarkdown, hasThinkingContent, extractThinkingContent } from '@/utils/markdown'
import { config } from '@/config'

// 扩展消息类型以支持showThinking属性
interface ExtendedMessage {
  id: string
  conversation_id: string
  content: string
  type: 'user' | 'assistant'
  thinking?: string
  attachments: any[]
  metadata: any
  user_id: string
  created_at: string
  showThinking?: boolean
}

const message = useMessage()
const chatStore = useChatStore()
const agentsStore = useAgentsStore()
const modelsStore = useModelsStore()

// 响应式数据
const currentConversationId = ref('')
const messageText = ref('')
const streamingMessage = ref('')
const showCreateDialog = ref(false)
const chatMessagesRef = ref<HTMLElement>()
const showThinking = ref<Record<string, boolean>>({})
const sending = ref(false)
const creating = ref(false)

// 新增功能相关数据
const showThinkingEnabled = ref(false)
const selectedModel = ref('')
const uploadedFiles = ref<File[]>([])
const fileInputRef = ref<HTMLInputElement>()
const imageInputRef = ref<HTMLInputElement>()

// 创建对话表单
const createForm = reactive({
  type: 'model' as 'agent' | 'model',
  agent_id: '',
  title: ''
})

const createFormRef = ref()

// 计算属性 - 修复模型一致性
const agentOptions = computed(() => {
  return agentsStore.agents.map(agent => ({
    label: agent.name,
    value: agent.id
  }))
})

const modelOptions = computed(() => {
  // 确保模型数据一致性，过滤掉无效的模型
  const validModels = modelsStore.models.filter(model => 
    model && model.id && model.name && 
    (model.status === 'active' || model.status === 'available')
  )
  
  console.log('📊 有效模型数量:', validModels.length)
  validModels.forEach(model => {
    console.log(`  - ${model.name} (${model.id}) - ${model.status} - ${model.server_url || 'localhost'}`)
  })
  
  return validModels.map(model => ({
    label: model.name, // 只显示模型名称，不显示多余字符
    value: model.id,
    description: model.description || '',
    provider: model.provider || 'unknown',
    status: model.status,
    server_url: model.server_url
  }))
})

const currentConversation = computed(() => {
  return chatStore.conversations.find(c => c.id === currentConversationId.value)
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
  }
}))

// 方法
const selectConversation = (conversation: any) => {
  currentConversationId.value = conversation.id
  chatStore.getMessages(conversation.id)
  
  // 如果是模型对话且有默认模型，自动选择该模型
  if (conversation.type === 'model' && conversation.model_id) {
    selectedModel.value = conversation.model_id
    console.log('🔄 自动选择对话默认模型:', conversation.model_id)
  } else if (conversation.type === 'model') {
    // 如果是模型对话但没有默认模型，尝试设置第一个有效模型
    const firstValidModel = modelsStore.models.find(model => 
      model && model.id && model.name && 
      (model.status === 'active' || model.status === 'available')
    )
    if (firstValidModel) {
      selectedModel.value = firstValidModel.id
      console.log('🔄 设置第一个有效模型作为默认模型:', firstValidModel.name)
      
      // 更新对话的默认模型
      chatStore.updateConversation(conversation.id, {
        model_id: firstValidModel.id
      }).catch(error => {
        console.error('❌ 更新对话默认模型失败:', error)
      })
    } else {
      selectedModel.value = ''
      console.log('🔄 模型对话无可用模型')
    }
  } else {
    // 智能体对话，清空模型选择
    selectedModel.value = ''
    console.log('🔄 智能体对话，清空模型选择')
  }
}

const handleSendMessage = async () => {
  if (!messageText.value.trim() || !currentConversationId.value) return
  
  const content = messageText.value.trim()
  const files = uploadedFiles.value
  
  // 检查当前对话类型和模型选择
  const currentConversation = chatStore.conversations.find(c => c.id === currentConversationId.value)
  if (currentConversation?.type === 'model' && !selectedModel.value) {
    message.error('请先选择一个模型')
    return
  }
  
  // 立即添加用户消息到聊天框，提供即时反馈
  const userMessage = {
    id: `user_${Date.now()}`,
    conversation_id: currentConversationId.value,
    content: content,
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
  
  // 添加到消息列表
  chatStore.messages.push(userMessage)
  
  // 清空输入和文件
  messageText.value = ''
  uploadedFiles.value = []
  sending.value = true
  
  // 清空之前的流式消息
  streamingMessage.value = ''
  
  // 立即滚动到底部，显示用户消息
  await nextTick()
  scrollToBottom()
  
  try {
    // 构建消息数据，包含文件和深度思考设置
    const messageData = {
      content,
      files: files.map(file => ({
        name: file.name,
        size: file.size,
        type: file.type,
        data: file // 实际使用时需要转换为base64或上传到服务器
      })),
      showThinking: showThinkingEnabled.value,
      modelId: selectedModel.value || undefined
    }
    
    // 调用store的streamMessage方法发送消息到后端
    await chatStore.streamMessage(
      currentConversationId.value,
      content,
      (chunk) => {
        streamingMessage.value += chunk
        // 每次收到数据块时都滚动到底部
        scrollToBottom()
      },
      (message) => {
        // 流式传输完成，清空流式消息
        streamingMessage.value = ''
        scrollToBottom()
      },
      (error) => {
        message.error(`发送消息失败: ${error}`)
        streamingMessage.value = ''
      },
      {
        files: files,
        showThinking: showThinkingEnabled.value,
        modelId: selectedModel.value || undefined
      }
    )
  } catch (error: any) {
    const errorMessage = error.response?.data?.message || error.message || '发送消息失败'
    message.error(errorMessage)
  } finally {
    sending.value = false
  }
}

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
    
    // 验证选择的智能体是否存在
    if (createForm.type === 'agent' && createForm.agent_id) {
      const agent = agentsStore.agents.find(a => a.id === createForm.agent_id)
      if (!agent) {
        message.error('选择的智能体不存在')
        return
      }
    }
    
    const result = await chatStore.createConversation(createForm)
    if (result) {
      showCreateDialog.value = false
      createForm.type = 'model'
      createForm.agent_id = ''
      createForm.title = ''
      
      // 如果是模型对话，设置默认模型为第一个有效模型
      if (result.type === 'model') {
        const firstValidModel = modelsStore.models.find(model => 
          model && model.id && model.name && 
          (model.status === 'active' || model.status === 'available')
        )
        if (firstValidModel) {
          selectedModel.value = firstValidModel.id
          console.log('🔄 自动设置默认模型:', firstValidModel.name)
          
          // 更新对话的默认模型
          try {
            await chatStore.updateConversation(result.id, {
              model_id: firstValidModel.id
            })
            console.log('✅ 对话默认模型更新成功')
          } catch (error) {
            console.error('❌ 更新对话默认模型失败:', error)
          }
        }
      }
      
      selectConversation(result)
      message.success('对话创建成功')
    }
  } catch (error: any) {
    console.error('创建对话失败:', error)
    const errorMessage = error.response?.data?.message || error.message || '创建对话失败'
    message.error(errorMessage)
  } finally {
    creating.value = false
  }
}

const deleteConversation = async (conversationId: string) => {
  try {
    await chatStore.deleteConversation(conversationId)
    if (currentConversationId.value === conversationId) {
      currentConversationId.value = ''
    }
    message.success('对话删除成功')
  } catch (error: any) {
    console.error('删除对话失败:', error)
    message.error('删除对话失败')
  }
}

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

const scrollToBottom = () => {
  nextTick(() => {
    if (chatMessagesRef.value) {
      const scrollElement = chatMessagesRef.value
      scrollElement.scrollTop = scrollElement.scrollHeight
      console.log('🔄 滚动到底部:', scrollElement.scrollTop, scrollElement.scrollHeight)
    }
  })
}

// 强制滚动到底部
const forceScrollToBottom = () => {
  nextTick(() => {
    if (chatMessagesRef.value) {
      const scrollElement = chatMessagesRef.value
      scrollElement.scrollTop = scrollElement.scrollHeight
      console.log('🔄 强制滚动到底部')
    }
  })
}

// 思考内容相关方法
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

// 文件上传相关方法
const triggerFileUpload = () => {
  fileInputRef.value?.click()
}

const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    const files = Array.from(target.files)
    // 验证文件大小和类型
    const validFiles = files.filter(file => {
      if (file.size > config.upload.maxSize) {
        message.error(`文件 ${file.name} 过大，最大支持 ${config.upload.maxSize / 1024 / 1024}MB`)
        return false
      }
      return true
    })
    uploadedFiles.value.push(...validFiles)
    target.value = '' // 清空input
  }
}

const triggerImageUpload = () => {
  imageInputRef.value?.click()
}

const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    const files = Array.from(target.files)
    // 验证图片文件
    const validFiles = files.filter(file => {
      if (!file.type.startsWith('image/')) {
        message.error(`文件 ${file.name} 不是有效的图片格式`)
        return false
      }
      if (file.size > config.upload.maxSize) {
        message.error(`图片 ${file.name} 过大，最大支持 ${config.upload.maxSize / 1024 / 1024}MB`)
        return false
      }
      return true
    })
    uploadedFiles.value.push(...validFiles)
    target.value = '' // 清空input
  }
}

const removeFile = (index: number) => {
  uploadedFiles.value.splice(index, 1)
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 处理模型选择变化
const handleModelChange = (modelId: string) => {
  console.log('🔄 模型选择变化:', modelId)
  if (modelId) {
    const selectedModelData = modelsStore.models.find(m => m.id === modelId)
    if (selectedModelData) {
      const serverInfo = selectedModelData.server_url ? ` (${selectedModelData.server_url})` : ' (localhost)'
      console.log('✅ 选择模型:', selectedModelData.name + serverInfo)
      message.success(`已选择模型: ${selectedModelData.name}${serverInfo}`)
    }
  } else {
    console.log('🔄 清除模型选择')
  }
}

// 初始化数据
const initializeData = async () => {
  try {
    console.log('🔄 开始初始化聊天页面数据...')
    
    // 并行加载所有必要的数据
    const promises = [
      agentsStore.getAgents(),
      modelsStore.getModels(),
      chatStore.getConversations()
    ]
    
    await Promise.all(promises)
    
    console.log('✅ 聊天页面数据初始化完成')
    console.log(`📊 智能体数量: ${agentsStore.agents.length}`)
    console.log(`📊 模型数量: ${modelsStore.models.length}`)
    console.log(`📊 对话数量: ${chatStore.conversations.length}`)
    
  } catch (error: any) {
    console.error('❌ 初始化聊天页面数据失败:', error)
    message.error('初始化数据失败，请刷新页面重试')
  }
}

// 生命周期
onMounted(async () => {
  await initializeData()
})

// 监听消息变化，自动滚动到底部
watch(() => chatStore.messages, () => {
  scrollToBottom()
}, { deep: true })

// 监听流式传输状态
watch(() => chatStore.streaming, (isStreaming) => {
  if (isStreaming) {
    console.log('🔄 开始流式传输，滚动到底部')
    forceScrollToBottom()
  } else {
    console.log('🔄 流式传输结束，清空流式消息')
    streamingMessage.value = ''
  }
})

// 监听流式消息变化
watch(streamingMessage, (newValue) => {
  if (newValue) {
    console.log('🔄 收到流式消息，滚动到底部')
    scrollToBottom()
  }
})

// 监听模型数据变化，确保模型选择器更新
watch(() => modelsStore.models, (newModels) => {
  console.log('📊 模型数据更新:', newModels.length, '个模型')
  // 如果当前选择的模型不存在了，清空选择
  if (selectedModel.value && !newModels.find(m => m.id === selectedModel.value)) {
    selectedModel.value = ''
    console.log('🔄 清空无效的模型选择')
  }
}, { deep: true })

// 监听智能体数据变化
watch(() => agentsStore.agents, (newAgents) => {
  console.log('📊 智能体数据更新:', newAgents.length, '个智能体')
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

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.conversation-item {
  padding: 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 4px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: var(--n-color);
  border: 1px solid transparent;
}

.conversation-item:hover {
  background: var(--n-hover-color);
  border-color: var(--n-border-color);
}

.conversation-item.active {
  background: var(--n-primary-color-1);
  border-color: var(--n-primary-color);
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-title {
  font-weight: 500;
  margin-bottom: 6px;
  color: var(--n-text-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
}

.conversation-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.conversation-name {
  font-size: 12px;
  color: var(--n-text-color-3);
}

.conversation-time {
  font-size: 12px;
  color: var(--n-text-color-4);
}

.conversation-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.conversation-item:hover .conversation-actions {
  opacity: 1;
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
  min-height: 400px;
}

.empty-content {
  text-align: center;
  color: var(--n-text-color-3);
  max-width: 400px;
  padding: 40px 20px;
}

.empty-content .n-icon {
  color: var(--n-text-color-4);
}

.empty-icon {
  margin-bottom: 24px;
  opacity: 0.5;
}

.empty-title {
  font-size: 24px;
  font-weight: 600;
  margin: 16px 0 12px 0;
  color: var(--n-text-color);
}

.empty-description {
  font-size: 16px;
  margin: 0 0 32px 0;
  color: var(--n-text-color-3);
  line-height: 1.5;
}

.create-btn {
  background-color: var(--n-primary-color);
  color: white;
  border-color: var(--n-primary-color);
}

.create-btn:hover {
  background-color: var(--n-primary-color-hover);
  border-color: var(--n-primary-color-hover);
}

.new-chat-btn {
  background-color: var(--n-primary-color);
  color: white;
  border-color: var(--n-primary-color);
}

.new-chat-btn:hover {
  background-color: var(--n-primary-color-hover);
  border-color: var(--n-primary-color-hover);
}

.delete-btn {
  color: var(--n-error-color);
}

.delete-btn:hover {
  background-color: var(--n-error-color);
  color: white;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* 聊天头部 */
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
  background-color: var(--n-primary-color-1);
  color: var(--n-primary-color);
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
}

.message-wrapper {
  display: flex;
  gap: 12px;
  max-width: 85%;
  margin-bottom: 16px;
}

.message-wrapper.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-wrapper.assistant {
  align-self: flex-start;
}

/* 用户消息 */
.user-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 100%;
}

.user-message .message-content {
  text-align: right;
  flex: 1;
  min-width: 0;
}

.user-message .message-text {
  display: inline-block;
  background: var(--n-primary-color);
  color: white;
  padding: 16px 20px;
  border-radius: 20px;
  line-height: 1.6;
  word-wrap: break-word;
  max-width: 100%;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
}

.user-message .message-time {
  font-size: 12px;
  color: var(--n-text-color-4);
  margin-top: 4px;
  text-align: right;
}

/* 消息附件 */
.message-attachments {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.attachment-item {
  display: flex;
  align-items: center;
  padding: 6px 8px;
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  border-radius: 6px;
  transition: all 0.2s ease;
}

.attachment-item:hover {
  background: var(--n-hover-color);
  border-color: var(--n-primary-color);
}

.attachment-info {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.attachment-icon {
  color: var(--n-text-color-3);
  flex-shrink: 0;
}

.attachment-name {
  font-size: 11px;
  color: var(--n-text-color);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.attachment-size {
  font-size: 10px;
  color: var(--n-text-color-4);
  flex-shrink: 0;
}

/* AI消息 */
.ai-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 100%;
}

.ai-message .message-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.ai-message .message-text {
  background: var(--n-color);
  color: var(--n-text-color);
  border: 1px solid var(--n-border-color);
  padding: 16px 20px;
  border-radius: 20px;
  line-height: 1.6;
  word-wrap: break-word;
  font-size: 14px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.ai-message .message-time {
  font-size: 12px;
  color: var(--n-text-color-4);
  margin-top: 4px;
}

/* 思考内容切换 */
.thinking-toggle {
  margin-bottom: 8px;
  display: flex;
  justify-content: flex-end;
}

.thinking-toggle .n-button {
  color: var(--n-warning-color);
}

.thinking-toggle .n-button:hover {
  color: var(--n-warning-color-hover);
}

/* 思考内容 */
.thinking-content {
  background: var(--n-warning-color-1);
  padding: 12px 16px;
  border-radius: 12px;
  margin-bottom: 8px;
  border: 1px solid var(--n-warning-color);
}

.thinking-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: var(--n-warning-color);
  font-size: 14px;
  font-weight: 500;
}

.thinking-text {
  line-height: 1.6;
  font-size: 14px;
  color: var(--n-warning-color);
}

/* 加载气泡 */
.loading-bubble {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--n-text-color-3);
  font-size: 14px;
  padding: 12px 16px;
  background: var(--n-color);
  border-radius: 18px;
  border: 1px solid var(--n-border-color);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.loading-dots {
  display: flex;
  gap: 4px;
}

.loading-dots span {
  display: inline-block;
  width: 6px;
  height: 6px;
  background-color: var(--n-text-color-4);
  border-radius: 50%;
  animation: dot-pulse 1.2s infinite ease-in-out;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
.loading-dots span:nth-child(3) { animation-delay: 0s; }

.loading-text {
  font-size: 14px;
  color: var(--n-text-color-3);
}

@keyframes dot-pulse {
  0%, 80%, 100% { transform: scale(0.8); opacity: 0.6; }
  40% { transform: scale(1); opacity: 1; }
}

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

.message-wrapper {
  animation: fadeInUp 0.3s ease-out;
}

/* 输入区域 */
.chat-input {
  border-top: 1px solid var(--n-border-color);
  padding: 20px;
  background: var(--n-color);
  flex-shrink: 0;
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
}

.send-btn:hover {
  background: var(--n-primary-color-hover);
  transform: translateY(-1px);
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
    height: calc(100vh - 80px);
    padding: 8px;
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