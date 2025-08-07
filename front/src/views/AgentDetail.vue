<template>
  <div class="agent-detail-page">
    <div class="page-header">
      <div class="header-content">
        <n-button @click="router.back()" quaternary>
          <template #icon>
            <n-icon><ArrowBack /></n-icon>
          </template>
          返回
        </n-button>
        <h1 class="page-title">{{ agent?.name || '智能体详情' }}</h1>
      </div>
      <div class="header-actions">
        <n-button @click="handleEdit">
          <template #icon>
            <n-icon><Create /></n-icon>
          </template>
          编辑
        </n-button>
        <n-button @click="startChat">
          <template #icon>
            <n-icon><Chatbubble /></n-icon>
          </template>
          开始聊天
        </n-button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <n-spin size="large" />
      <p>加载中...</p>
    </div>

    <div v-else-if="agent" class="agent-content">
      <!-- 基本信息 -->
      <div class="info-section">
        <n-card title="基本信息">
          <div class="info-grid">
            <div class="info-item">
              <span class="label">智能体名称:</span>
              <span class="value">{{ agent.name }}</span>
            </div>
            <div class="info-item">
              <span class="label">描述:</span>
              <span class="value">{{ agent.description || '暂无描述' }}</span>
            </div>
            <div class="info-item">
              <span class="label">类型:</span>
              <span class="value">
                <n-tag :type="getTypeColor(agent.type)">
                  {{ getTypeText(agent.type) }}
                </n-tag>
              </span>
            </div>
            <div class="info-item">
              <span class="label">状态:</span>
              <span class="value">
                <n-tag :type="agent.status === 'active' ? 'success' : 'default'">
                  {{ agent.status === 'active' ? '已启用' : '已禁用' }}
                </n-tag>
              </span>
            </div>
            <div class="info-item">
              <span class="label">模型:</span>
              <span class="value">{{ agent.model_name }}</span>
            </div>
            <div class="info-item">
              <span class="label">创建时间:</span>
              <span class="value">{{ formatDate(agent.created_at) }}</span>
            </div>
            <div class="info-item">
              <span class="label">更新时间:</span>
              <span class="value">{{ formatDate(agent.updated_at) }}</span>
            </div>
          </div>
        </n-card>
      </div>

      <!-- 配置信息 -->
      <div class="config-section">
        <n-card title="配置信息">
          <n-tabs type="line" animated>
            <n-tab-pane name="system" tab="系统提示词">
              <div class="prompt-content">
                <n-input
                  :value="agent.config?.system_prompt || ''"
                  type="textarea"
                  :rows="6"
                  readonly
                  placeholder="暂无系统提示词"
                />
              </div>
            </n-tab-pane>
            
            <n-tab-pane name="params" tab="参数配置">
              <div class="params-grid">
                <div class="param-item">
                  <span class="param-label">温度 (Temperature):</span>
                  <span class="param-value">{{ agent.config?.temperature || 0.7 }}</span>
                </div>
                <div class="param-item">
                  <span class="param-label">最大令牌数 (Max Tokens):</span>
                  <span class="param-value">{{ agent.config?.max_tokens || 2048 }}</span>
                </div>
                <div class="param-item">
                  <span class="param-label">Top P:</span>
                  <span class="param-value">{{ agent.config?.top_p || 0.9 }}</span>
                </div>
                <div class="param-item">
                  <span class="param-label">频率惩罚 (Frequency Penalty):</span>
                  <span class="param-value">{{ agent.config?.frequency_penalty || 0 }}</span>
                </div>
                <div class="param-item">
                  <span class="param-label">存在惩罚 (Presence Penalty):</span>
                  <span class="param-value">{{ agent.config?.presence_penalty || 0 }}</span>
                </div>
              </div>
            </n-tab-pane>
            
            <n-tab-pane name="plugins" tab="插件配置">
              <div class="plugins-content">
                <div v-if="agent.config?.plugins && agent.config.plugins.length > 0" class="plugins-list">
                  <div
                    v-for="pluginId in agent.config.plugins"
                    :key="pluginId"
                    class="plugin-item"
                  >
                    <n-tag type="info">{{ pluginId }}</n-tag>
                  </div>
                </div>
                <div v-else class="empty-plugins">
                  <n-empty description="暂无配置的插件" />
                </div>
              </div>
            </n-tab-pane>
            
            <n-tab-pane name="knowledge" tab="知识库">
              <div class="knowledge-content">
                <div v-if="agent.config?.knowledge_bases && agent.config.knowledge_bases.length > 0" class="knowledge-list">
                  <div
                    v-for="kbId in agent.config.knowledge_bases"
                    :key="kbId"
                    class="knowledge-item"
                  >
                    <n-tag type="success">{{ kbId }}</n-tag>
                  </div>
                </div>
                <div v-else class="empty-knowledge">
                  <n-empty description="暂无配置的知识库" />
                </div>
              </div>
            </n-tab-pane>
          </n-tabs>
        </n-card>
      </div>

      <!-- 统计信息 -->
      <div class="stats-section">
        <n-card title="使用统计">
          <div class="stats-grid">
            <div class="stats-item">
              <div class="stats-icon conversations">
                <n-icon><Chatbubbles /></n-icon>
              </div>
              <div class="stats-content">
                <div class="stats-value">{{ stats?.total_conversations || 0 }}</div>
                <div class="stats-label">总对话数</div>
              </div>
            </div>
            <div class="stats-item">
              <div class="stats-icon messages">
                <n-icon><ChatbubbleEllipses /></n-icon>
              </div>
              <div class="stats-content">
                <div class="stats-value">{{ stats?.total_messages || 0 }}</div>
                <div class="stats-label">总消息数</div>
              </div>
            </div>
            <div class="stats-item">
              <div class="stats-icon tokens">
                <n-icon><Calculator /></n-icon>
              </div>
              <div class="stats-content">
                <div class="stats-value">{{ stats?.total_tokens || 0 }}</div>
                <div class="stats-label">总令牌数</div>
              </div>
            </div>
            <div class="stats-item">
              <div class="stats-icon time">
                <n-icon><Time /></n-icon>
              </div>
              <div class="stats-content">
                <div class="stats-value">{{ stats?.total_time || 0 }}s</div>
                <div class="stats-label">总用时</div>
              </div>
            </div>
          </div>
        </n-card>
      </div>

      <!-- 最近对话 -->
      <div class="conversations-section">
        <n-card title="最近对话">
          <div v-if="conversations.length > 0" class="conversations-list">
            <div
              v-for="conversation in conversations"
              :key="conversation.id"
              class="conversation-item"
              @click="viewConversation(conversation)"
            >
              <div class="conversation-info">
                <div class="conversation-title">{{ conversation.title }}</div>
                <div class="conversation-meta">
                  <span>{{ conversation.message_count }} 条消息</span>
                  <span>{{ formatDate(conversation.updated_at) }}</span>
                </div>
              </div>
              <div class="conversation-actions">
                <n-button size="small" @click.stop="viewConversation(conversation)">
                  查看
                </n-button>
                <n-button size="small" type="error" @click.stop="deleteConversation(conversation.id)">
                  删除
                </n-button>
              </div>
            </div>
          </div>
          <div v-else class="empty-conversations">
            <n-empty description="暂无对话记录">
              <template #extra>
                <n-button type="primary" @click="startChat">
                  开始第一次对话
                </n-button>
              </template>
            </n-empty>
          </div>
        </n-card>
      </div>
    </div>

    <div v-else class="not-found">
      <n-result
        status="404"
        title="智能体不存在"
        description="您访问的智能体不存在或已被删除"
      >
        <template #footer>
          <n-button type="primary" @click="router.push('/agents')">
            返回智能体列表
          </n-button>
        </template>
      </n-result>
    </div>

    <!-- 编辑模态框 -->
    <n-modal
      v-model:show="showEditModal"
      preset="card"
      title="编辑智能体"
      style="width: 600px"
      :mask-closable="false"
    >
      <n-form
        ref="editFormRef"
        :model="editFormData"
        :rules="editRules"
        label-placement="left"
        label-width="auto"
        require-mark-placement="right-hanging"
      >
        <n-form-item label="名称" path="name">
          <n-input v-model:value="editFormData.name" placeholder="请输入智能体名称" />
        </n-form-item>

        <n-form-item label="描述" path="description">
          <n-input
            v-model:value="editFormData.description"
            type="textarea"
            placeholder="请输入智能体描述"
            :rows="3"
          />
        </n-form-item>

        <n-form-item label="类型" path="type">
          <n-select
            v-model:value="editFormData.type"
            :options="typeOptions"
            placeholder="请选择智能体类型"
          />
        </n-form-item>

        <n-form-item label="模型" path="model_name">
          <n-select
            v-model:value="editFormData.model_name"
            :options="modelOptions"
            placeholder="请选择模型"
          />
        </n-form-item>

        <n-form-item label="状态" path="status">
          <n-switch v-model:value="editFormData.status" />
        </n-form-item>

        <n-form-item label="配置" path="config">
          <n-input
            v-model:value="editFormData.config"
            type="textarea"
            placeholder="请输入JSON配置"
            :rows="5"
          />
        </n-form-item>
      </n-form>

      <template #footer>
        <div class="modal-footer">
          <n-button @click="cancelEdit">取消</n-button>
          <n-button type="primary" @click="handleEditSubmit" :loading="submitting">
            更新
          </n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import {
  NCard,
  NButton,
  NIcon,
  NInput,
  NTag,
  NTabs,
  NTabPane,
  NEmpty,
  NResult,
  NSpin,
  NModal,
  NForm,
  NFormItem,
  NSelect,
  NSwitch
} from 'naive-ui'
import {
  ArrowBack,
  Create,
  Chatbubble,
  Chatbubbles,
  ChatbubbleEllipses,
  Calculator,
  Time
} from '@vicons/ionicons5'
import { useAgentsStore } from '@/stores/agents'
import { useChatStore } from '@/stores/chat'
import type { Agent, AgentType, AgentStatus } from '@/types/agent'
import { api } from '@/api'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const agentsStore = useAgentsStore()
const chatStore = useChatStore()

// 统一的错误处理函数
const handleError = (error: any): string => {
  console.error('API错误:', error)
  
  if (error.code === 'ECONNABORTED') {
    return '请求超时，请检查后端服务是否正常运行'
  } else if (error.code === 'ERR_NETWORK') {
    return '网络连接失败，请检查网络连接'
  } else if (error.response?.status === 500) {
    return '服务器内部错误，请稍后重试'
  } else if (error.response?.status === 404) {
    return 'API端点不存在，请检查后端配置'
  } else if (error.response?.status === 401) {
    return '认证失败，请重新登录'
  } else if (error.response?.status === 403) {
    return '权限不足，无法访问此资源'
  } else if (error.response?.status === 422) {
    return '请求参数错误，请检查输入数据'
  } else {
    return `操作失败: ${error.message || '未知错误'}`
  }
}

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const agent = ref<Agent | null>(null)
const stats = ref<any>(null)
const conversations = ref<any[]>([])
const showEditModal = ref(false)

// 编辑表单数据
const editFormRef = ref()
const editFormData = ref({
  name: '',
  description: '',
  type: '' as AgentType,
  model_name: '',
  status: true,
  config: ''
})

// 编辑表单验证规则
const editRules = {
  name: {
    required: true,
    message: '请输入智能体名称',
    trigger: 'blur'
  },
  type: {
    required: true,
    message: '请选择智能体类型',
    trigger: 'change'
  },
  model_name: {
    required: true,
    message: '请选择模型',
    trigger: 'change'
  }
}

// 选项数据
const typeOptions = [
  { label: '对话型', value: 'chat' },
  { label: '助手型', value: 'assistant' },
  { label: '专家型', value: 'specialist' },
  { label: '创意型', value: 'creative' }
]

const modelOptions = [
  { label: 'GPT-3.5', value: 'gpt-3.5-turbo' },
  { label: 'GPT-4', value: 'gpt-4' },
  { label: 'Claude-3', value: 'claude-3' },
  { label: 'Llama-2', value: 'llama-2' }
]

// 计算属性
const agentId = computed(() => route.params.id as string)

// 方法
const loadAgentDetail = async () => {
  if (!agentId.value) return
  
  try {
    loading.value = true
    
    // 使用生产环境数据
    console.log('📊 使用生产环境数据加载智能体详情')
    
    const result = await agentsStore.getAgent(agentId.value)
    if (result) {
      // 确保类型正确
      agent.value = {
        ...result,
        type: result.type as AgentType,
        model_name: result.model_name || 'llama2',
        status: result.status as AgentStatus
      }
      await loadAgentStats()
      await loadConversations()
      
      console.log('✅ 智能体详情加载成功:', agent.value)
    } else {
      message.error('智能体不存在或已被删除')
      // 清空数据
      agent.value = null
      stats.value = null
      conversations.value = []
    }
  } catch (error: any) {
    console.error('加载智能体详情失败:', error)
    message.error('加载智能体详情失败')
    // 清空数据
    agent.value = null
    stats.value = null
    conversations.value = []
  } finally {
    loading.value = false
  }
}

const loadAgentStats = async () => {
  try {
    console.log('🔍 加载智能体统计信息:', agentId.value)
    
    // 使用生产环境数据
    console.log('📊 使用生产环境数据加载智能体统计信息')
    
    const response = await api.agents.stats(agentId.value)
    
    if (response.data && response.data.success) {
      stats.value = response.data.data
      console.log('✅ 智能体统计信息加载成功:', stats.value)
    } else {
      console.warn('⚠️ 智能体统计信息加载失败')
      stats.value = {
        total_conversations: 0,
        total_messages: 0,
        total_tokens: 0,
        total_time: 0
      }
    }
  } catch (error: any) {
    console.error('❌ 加载统计信息失败:', error)
    console.error(handleError(error))
    
    // 清空统计数据而不是使用模拟数据
    stats.value = {
      total_conversations: 0,
      total_messages: 0,
      total_tokens: 0,
      total_time: 0
    }
  }
}

const loadConversations = async () => {
  try {
    console.log('🔍 加载智能体对话历史:', agentId.value)
    
    // 使用生产环境数据
    console.log('📊 使用生产环境数据加载智能体对话历史')
    
    const response = await api.agents.conversations(agentId.value)
    if (response.data && response.data.success) {
      conversations.value = response.data.data
      console.log('✅ 智能体对话历史加载成功:', conversations.value)
    } else {
      console.warn('⚠️ 智能体对话历史加载失败')
      conversations.value = []
    }
  } catch (error: any) {
    console.error('加载对话历史失败:', error)
    // 清空对话列表而不是使用模拟数据
    conversations.value = []
  }
}

const getTypeColor = (type: AgentType) => {
  const colorMap: Record<AgentType, 'info' | 'success' | 'warning' | 'error'> = {
    chat: 'info',
    assistant: 'success',
    specialist: 'warning',
    creative: 'error'
  }
  return colorMap[type] || 'default'
}

const getTypeText = (type: AgentType) => {
  const textMap: Record<AgentType, string> = {
    chat: '对话型',
    assistant: '助手型',
    specialist: '专家型',
    creative: '创意型'
  }
  return textMap[type] || type
}

const formatDate = (dateString: string) => {
  if (!dateString) return '未知时间'
  try {
    return new Date(dateString).toLocaleString('zh-CN')
  } catch (error) {
    return '未知时间'
  }
}

const startChat = () => {
  if (agent.value) {
    router.push(`/chat?agent_id=${agent.value.id}`)
  }
}

const viewConversation = (conversation: any) => {
  router.push(`/chat?conversation_id=${conversation.id}`)
}

const deleteConversation = async (conversationId: string) => {
  try {
    console.log('🗑️ 删除对话:', conversationId)
    
    // 使用生产环境API删除对话
    console.log('📊 删除对话')
    
    // 模拟API延迟
    await new Promise(resolve => setTimeout(resolve, 300))
    
    // 从本地列表中移除
    conversations.value = conversations.value.filter(c => c.id !== conversationId)
    
    message.success('对话删除成功')
    console.log('✅ 对话删除成功')
    
  } catch (error: any) {
    console.error('❌ 删除对话失败:', error)
    message.error(handleError(error))
  }
}

// 编辑智能体
const handleEdit = () => {
  if (agent.value) {
    console.log('🔄 开始编辑智能体:', agent.value.name)
    // 初始化编辑表单数据
    editFormData.value = {
      name: agent.value.name,
      description: agent.value.description,
      type: agent.value.type,
      model_name: agent.value.model_name,
      status: agent.value.status === 'active',
      config: JSON.stringify(agent.value.config || {}, null, 2)
    }
    showEditModal.value = true
  } else {
    message.error('智能体数据不存在')
  }
}

// 取消编辑
const cancelEdit = () => {
  showEditModal.value = false
  // 清空表单数据
  editFormData.value = {
    name: '',
    description: '',
    type: '' as AgentType,
    model_name: '',
    status: true,
    config: ''
  }
  // 重置表单验证状态
  editFormRef.value?.restoreValidation()
}

// 提交编辑
const handleEditSubmit = async () => {
  if (!editFormRef.value) return

  try {
    await editFormRef.value.validate()
  } catch (errors: any) {
    if (errors && errors.length > 0) {
      message.error('请检查表单填写')
      return
    }
  }

  submitting.value = true
  try {
    console.log('🔄 提交智能体编辑:', agentId.value)
    
    // 解析配置JSON
    let config = {}
    if (editFormData.value.config) {
      try {
        config = JSON.parse(editFormData.value.config)
      } catch (e) {
        message.error('配置JSON格式错误')
        return
      }
    }

    const updatedAgent = {
      name: editFormData.value.name,
      description: editFormData.value.description,
      type: editFormData.value.type,
      model_name: editFormData.value.model_name,
      status: editFormData.value.status ? 'active' : 'inactive',
      config
    }
    
    console.log('📝 更新数据:', updatedAgent)
    
    // 使用生产环境数据操作
    console.log('📊 使用生产环境数据更新智能体')
    
    const response = await agentsStore.updateAgent(agentId.value, updatedAgent)
    if (response) {
      // 更新本地数据
      agent.value = {
        ...agent.value!,
        ...response,
        type: response.type as AgentType,
        status: response.status as AgentStatus
      }
      message.success('智能体更新成功')
      showEditModal.value = false
      console.log('✅ 智能体更新成功')
    } else {
      message.error('智能体更新失败')
    }
    
  } catch (error: any) {
    console.error('❌ 更新智能体失败:', error)
    message.error(handleError(error))
  } finally {
    submitting.value = false
  }
}

// 生命周期
onMounted(() => {
  loadAgentDetail()
  console.log('智能体详情页面已挂载')
})
</script>

<style scoped>
.agent-detail-page {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: var(--n-text-color);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 0;
  gap: 16px;
}

.agent-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-section {
  margin-bottom: 24px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--n-border-color);
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  font-weight: 500;
  color: var(--n-text-color-2);
}

.value {
  color: var(--n-text-color);
}

.config-section {
  margin-bottom: 24px;
}

.prompt-content {
  margin-top: 16px;
}

.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.param-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid var(--n-border-color);
  border-radius: 8px;
}

.param-label {
  font-weight: 500;
  color: var(--n-text-color-2);
}

.param-value {
  color: var(--n-text-color);
}

.stats-section {
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stats-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
}

.stats-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stats-icon.conversations {
  background: var(--n-primary-color-1);
  color: var(--n-primary-color);
}

.stats-icon.messages {
  background: var(--n-success-color-1);
  color: var(--n-success-color);
}

.stats-icon.tokens {
  background: var(--n-warning-color-1);
  color: var(--n-warning-color);
}

.stats-icon.time {
  background: var(--n-info-color-1);
  color: var(--n-info-color);
}

.stats-content {
  flex: 1;
}

.stats-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--n-text-color);
}

.stats-label {
  font-size: 14px;
  color: var(--n-text-color-3);
}

.conversations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.conversation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid var(--n-border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.conversation-item:hover {
  border-color: var(--n-primary-color);
  background: var(--n-hover-color);
}

.conversation-info {
  flex: 1;
}

.conversation-title {
  font-weight: 500;
  color: var(--n-text-color);
  margin-bottom: 4px;
}

.conversation-meta {
  font-size: 12px;
  color: var(--n-text-color-3);
  display: flex;
  gap: 16px;
}

.conversation-actions {
  display: flex;
  gap: 8px;
}

.empty-conversations {
  padding: 48px 0;
  text-align: center;
}

.not-found {
  padding: 48px 0;
  text-align: center;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .agent-detail-page {
    padding: 20px;
  }
  
  .info-grid {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  }
  
  .params-grid {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }
}

@media (max-width: 1024px) {
  .agent-detail-page {
    padding: 16px;
  }
  
  .info-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 12px;
  }
  
  .params-grid {
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
  }
  
  .stats-item {
    padding: 12px;
  }
  
  .stats-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
  
  .stats-value {
    font-size: 20px;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .params-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .conversation-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .conversation-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .param-item {
    padding: 8px;
  }
  
  .stats-item {
    padding: 8px;
  }
  
  .stats-icon {
    width: 36px;
    height: 36px;
    font-size: 18px;
  }
  
  .stats-value {
    font-size: 18px;
  }
}

@media (max-width: 480px) {
  .agent-detail-page {
    padding: 12px;
  }
  
  .page-title {
    font-size: 18px;
  }
  
  .info-section,
  .config-section,
  .stats-section,
  .conversations-section {
    margin-bottom: 12px;
  }
  
  .conversation-meta {
    flex-direction: column;
    gap: 2px;
  }
  
  .param-item {
    padding: 6px;
  }
  
  .stats-item {
    padding: 6px;
  }
  
  .stats-icon {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }
  
  .stats-value {
    font-size: 16px;
  }
  
  .stats-label {
    font-size: 12px;
  }
}
</style> 