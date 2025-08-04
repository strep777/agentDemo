<template>
  <div class="chat-container">
    <!-- 左侧对话列表 -->
    <div class="conversation-list">
      <div class="list-header">
        <n-button type="primary" @click="showCreateDialog = true">
          <template #icon>
            <n-icon><Add /></n-icon>
          </template>
          新建对话
        </n-button>
      </div>

      <div class="conversation-items">
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
              <n-tag size="small" :type="conversation.type === 'agent' ? 'primary' : 'success'">
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
            <n-button quaternary circle size="small" @click.stop="deleteConversation(conversation.id)">
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
        <n-icon size="64" color="#d9d9d9">
          <ChatbubblesOutline />
        </n-icon>
        <p>选择一个对话开始聊天</p>
      </div>

      <div v-else class="chat-content">
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
                <div class="message-time">
                  {{ formatTime(message.created_at) }}
                </div>
              </div>
              <div class="message-avatar">
                <n-avatar round size="small">
                  <template #default>
                    <n-icon><Person /></n-icon>
                  </template>
                </n-avatar>
              </div>
            </div>

            <!-- AI消息 -->
            <div v-else class="ai-message">
              <div class="message-avatar">
                <n-avatar round size="small">
                  <template #default>
                    <n-icon><ServerOutline /></n-icon>
                  </template>
                </n-avatar>
              </div>
              <div class="message-content">
                <div class="message-text">{{ message.content }}</div>
                <div class="message-time">
                  {{ formatTime(message.created_at) }}
                </div>
              </div>
            </div>
          </div>

          <!-- 流式消息 -->
          <div v-if="streamingMessage" class="message-wrapper assistant">
            <div class="ai-message">
              <div class="message-avatar">
                <n-avatar round size="small">
                  <template #default>
                    <n-icon><ServerOutline /></n-icon>
                  </template>
                </n-avatar>
              </div>
              <div class="message-content">
                <div class="message-text">
                  {{ streamingMessage }}
                  <span class="typing-indicator">|</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input">
          <div class="input-container">
            <n-input
              v-model:value="messageInput"
              type="textarea"
              placeholder="输入消息..."
              :rows="1"
              :autosize="{ minRows: 1, maxRows: 4 }"
              @keydown.enter.prevent="handleSendMessage"
            />
            <n-button
              type="primary"
              :disabled="!messageInput.trim() || chatStore.streaming"
              @click="handleSendMessage"
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

    <!-- 创建对话对话框 -->
    <n-modal v-model:show="showCreateDialog" preset="card" title="新建对话" style="width: 500px">
      <n-form ref="createFormRef" :model="createForm" :rules="getCreateRules" label-placement="left" label-width="auto">
        <n-form-item label="对话类型" path="type">
          <n-radio-group v-model:value="createForm.type">
            <n-space>
              <n-radio value="agent">智能体对话</n-radio>
              <n-radio value="model">模型对话</n-radio>
            </n-space>
          </n-radio-group>
        </n-form-item>

        <n-form-item label="选择智能体" path="agent_id" v-if="createForm.type === 'agent'">
          <n-select v-model:value="createForm.agent_id" :options="agentOptions" placeholder="选择智能体" filterable />
        </n-form-item>

        <n-form-item label="选择模型" path="model_id" v-if="createForm.type === 'model'">
          <n-select v-model:value="createForm.model_id" :options="modelOptions" placeholder="选择模型" filterable />
        </n-form-item>

        <n-form-item label="对话标题" path="title">
          <n-input v-model:value="createForm.title" placeholder="输入对话标题（可选）" />
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreateDialog = false">取消</n-button>
          <n-button type="primary" @click="handleCreateConversation">创建</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed, watch } from 'vue'
import { Add, Trash, Send, Person, ServerOutline, ChatbubblesOutline } from '@vicons/ionicons5'
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
  NRadio
} from 'naive-ui'

const message = useMessage()
const chatStore = useChatStore()
const agentsStore = useAgentsStore()
const modelsStore = useModelsStore()

// 响应式数据
const showCreateDialog = ref(false)
const messageInput = ref('')
const streamingMessage = ref('')
const chatMessagesRef = ref<HTMLElement>()

const createForm = reactive({
  type: 'agent' as 'agent' | 'model',
  agent_id: '',
  model_id: '',
  title: ''
})

// 动态验证规则
const getCreateRules = computed(() => {
  const rules: any = {
    type: [{ required: true, message: '请选择对话类型', trigger: 'change' }]
  }
  
  if (createForm.type === 'agent') {
    rules.agent_id = [{ required: true, message: '请选择智能体', trigger: 'change' }]
  } else if (createForm.type === 'model') {
    rules.model_id = [{ required: true, message: '请选择模型', trigger: 'change' }]
  }
  
  return rules
})

// 计算属性
const currentConversationId = computed(() => chatStore.currentConversation?.id)

const agentOptions = computed(() => 
  agentsStore.activeAgents.map(agent => ({
    label: agent.name,
    value: agent.id,
    description: agent.description
  }))
)

const modelOptions = computed(() => 
  modelsStore.activeModels.map(model => ({
    label: model.name,
    value: model.id,
    description: model.description
  }))
)

// 监听消息变化，自动滚动到底部
watch(() => chatStore.messages.length, () => {
  nextTick(() => {
    scrollToBottom()
  })
})

// 监听流式消息变化，自动滚动
watch(streamingMessage, () => {
  nextTick(() => {
    scrollToBottom()
  })
})

// 方法
const formatTime = (time: string) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const selectConversation = async (conversation: { id: string }) => {
  try {
    await chatStore.getConversation(conversation.id)
    await chatStore.getMessages(conversation.id)
    streamingMessage.value = ''
  } catch (error) {
    message.error('加载对话失败')
  }
}

const handleSendMessage = async () => {
  if (!messageInput.value.trim() || !currentConversationId.value) {
    message.warning('请输入消息内容')
    return
  }

  if (chatStore.streaming) {
    return
  }

  const content = messageInput.value.trim()
  messageInput.value = ''
  streamingMessage.value = ''

  try {
    await chatStore.streamMessage(
      currentConversationId.value,
      content,
      (chunk: string) => {
        streamingMessage.value += chunk
      },
      (message: any) => {
        streamingMessage.value = ''
        console.log('✅ 流式消息发送完成')
      },
      (error: string) => {
        console.error('❌ 流式消息发送失败:', error)
        message.error(`发送消息失败: ${error}`)
        streamingMessage.value = ''
      }
    )
  } catch (error: any) {
    console.error('❌ 发送消息异常:', error)
    const errorMessage = error.response?.data?.message || error.message || '发送消息失败'
    message.error(errorMessage)
    streamingMessage.value = ''
  }
}

const handleCreateConversation = async () => {
  if (!createForm.type) {
    message.error('请选择对话类型')
    return
  }

  if (createForm.type === 'agent' && !createForm.agent_id) {
    message.error('请选择智能体')
    return
  }

  if (createForm.type === 'model' && !createForm.model_id) {
    message.error('请选择模型')
    return
  }
  
  try {
    const conversationData: any = {
      type: createForm.type,
      title: createForm.title || '新对话'
    }
    
    if (createForm.type === 'agent') {
      conversationData.agent_id = createForm.agent_id
    } else if (createForm.type === 'model') {
      conversationData.model_id = createForm.model_id
    }
    
    console.log('发送的对话数据:', conversationData)
    
    const conversation = await chatStore.createConversation(conversationData)
    
    if (conversation) {
      showCreateDialog.value = false
      createForm.type = 'agent'
      createForm.agent_id = ''
      createForm.model_id = ''
      createForm.title = ''
      message.success('对话创建成功')
      await chatStore.getConversations()
    } else {
      message.error('创建对话失败，请检查网络连接')
    }
  } catch (error) {
    console.error('创建对话失败:', error)
    message.error('创建对话失败，请稍后重试')
  }
}

const deleteConversation = async (conversationId: string) => {
  try {
    const success = await chatStore.deleteConversation(conversationId)
    if (success) {
      message.success('删除成功')
    }
  } catch (error) {
    message.error('删除对话失败')
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  })
}

// 生命周期
onMounted(async () => {
  try {
    console.log('🔄 开始加载聊天页面数据...')
    await Promise.all([
      chatStore.getConversations(),
      agentsStore.getAgents(),
      modelsStore.getModels()
    ])
    console.log('✅ 聊天页面数据加载完成')
  } catch (error) {
    console.error('❌ 加载数据失败:', error)
    message.error('数据加载失败，请刷新页面重试')
  }
})
</script>

<style scoped>
.chat-container {
  display: flex;
  height: 100%;
  background: var(--n-color);
}

.conversation-list {
  width: 300px;
  border-right: 1px solid var(--n-border-color);
  display: flex;
  flex-direction: column;
  background: var(--n-color);
}

.list-header {
  padding: 16px;
  border-bottom: 1px solid var(--n-border-color);
}

.conversation-items {
  flex: 1;
  overflow-y: auto;
}

.conversation-item {
  padding: 12px 16px;
  border-bottom: 1px solid var(--n-border-color);
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conversation-item:hover {
  background-color: var(--n-hover-color);
}

.conversation-item.active {
  background-color: var(--n-primary-color-1);
  color: var(--n-primary-color);
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-title {
  font-weight: 500;
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

.conversation-name {
  font-size: 12px;
  color: var(--n-text-color-3);
}

.conversation-time {
  font-size: 12px;
  color: var(--n-text-color-3);
}

.conversation-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.conversation-item:hover .conversation-actions {
  opacity: 1;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--n-color);
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--n-text-color-3);
}

.empty-state p {
  margin-top: 16px;
  font-size: 16px;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-wrapper {
  display: flex;
  gap: 12px;
}

.message-wrapper.user {
  justify-content: flex-end;
}

.message-wrapper.assistant {
  justify-content: flex-start;
}

.user-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 70%;
}

.ai-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 70%;
}

.message-content {
  background: var(--n-primary-color-1);
  padding: 12px 16px;
  border-radius: 12px;
  position: relative;
}

.user-message .message-content {
  background: var(--n-primary-color);
  color: white;
}

.message-text {
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-time {
  font-size: 12px;
  color: var(--n-text-color-3);
  margin-top: 4px;
}

.user-message .message-time {
  color: rgba(255, 255, 255, 0.7);
}

.typing-indicator {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.chat-input {
  border-top: 1px solid var(--n-border-color);
  background: var(--n-color);
  padding: 16px;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-container .n-input {
  flex: 1;
}

.input-container .n-button {
  flex-shrink: 0;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: var(--n-border-color);
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: var(--n-text-color-3);
}

.conversation-items::-webkit-scrollbar {
  width: 6px;
}

.conversation-items::-webkit-scrollbar-track {
  background: transparent;
}

.conversation-items::-webkit-scrollbar-thumb {
  background: var(--n-border-color);
  border-radius: 3px;
}

.conversation-items::-webkit-scrollbar-thumb:hover {
  background: var(--n-text-color-3);
}
</style> 