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
        <n-button @click="showEditModal = true">
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
                  v-model:value="agent.config.system_prompt"
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
                  <span class="param-value">{{ agent.config.temperature || 0.7 }}</span>
                </div>
                <div class="param-item">
                  <span class="param-label">最大令牌数 (Max Tokens):</span>
                  <span class="param-value">{{ agent.config.max_tokens || 2048 }}</span>
                </div>
                <div class="param-item">
                  <span class="param-label">Top P:</span>
                  <span class="param-value">{{ agent.config.top_p || 0.9 }}</span>
                </div>
                <div class="param-item">
                  <span class="param-label">频率惩罚 (Frequency Penalty):</span>
                  <span class="param-value">{{ agent.config.frequency_penalty || 0 }}</span>
                </div>
                <div class="param-item">
                  <span class="param-label">存在惩罚 (Presence Penalty):</span>
                  <span class="param-value">{{ agent.config.presence_penalty || 0 }}</span>
                </div>
              </div>
            </n-tab-pane>
            
            <n-tab-pane name="plugins" tab="插件配置">
              <div class="plugins-content">
                <div v-if="agent.config.plugins && agent.config.plugins.length > 0" class="plugins-list">
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
                <div v-if="agent.config.knowledge_bases && agent.config.knowledge_bases.length > 0" class="knowledge-list">
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
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
import type { Agent, AgentType } from '@/types/agent'

const route = useRoute()
const router = useRouter()
const agentsStore = useAgentsStore()

// 响应式数据
const loading = ref(false)
const agent = ref<Agent | null>(null)
const stats = ref<any>(null)
const conversations = ref<any[]>([])
const showEditModal = ref(false)

// 计算属性
const agentId = computed(() => route.params.id as string)

// 方法
const loadAgentDetail = async () => {
  if (!agentId.value) return
  
  try {
    loading.value = true
    const result = await agentsStore.getAgent(agentId.value)
    if (result) {
      agent.value = result
      await loadAgentStats()
      await loadConversations()
    }
  } catch (error) {
    // message.error('加载智能体详情失败') // Removed useMessage
  } finally {
    loading.value = false
  }
}

const loadAgentStats = async () => {
  try {
    // TODO: 实现获取智能体统计信息的API
    stats.value = {
      total_conversations: 0,
      total_messages: 0,
      total_tokens: 0,
      total_time: 0
    }
  } catch (error) {
    // message.error('加载统计信息失败') // Removed useMessage
  }
}

const loadConversations = async () => {
  try {
    // TODO: 实现获取智能体对话历史的API
    conversations.value = []
  } catch (error) {
    // message.error('加载对话历史失败') // Removed useMessage
  }
}

const getTypeColor = (type: AgentType) => {
  const colorMap: Record<AgentType, string> = {
    chat: 'info',
    assistant: 'success',
    specialist: 'warning',
    creative: 'error'
  }
  return colorMap[type] || 'default'
}

const getTypeText = (type: AgentType) => {
  const textMap: Record<AgentType, string> = {
    chat: '聊天',
    assistant: '助手',
    specialist: '专家',
    creative: '创意'
  }
  return textMap[type] || type
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString()
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
    // TODO: 实现删除对话的API
    // message.success('对话删除成功') // Removed useMessage
    await loadConversations()
  } catch (error) {
    // message.error('删除对话失败') // Removed useMessage
  }
}

// 生命周期
onMounted(() => {
  loadAgentDetail()
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
  color: var(--text-color);
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
  padding: 48px;
  gap: 16px;
}

.agent-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-section,
.config-section,
.stats-section,
.conversations-section {
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
  border-bottom: 1px solid var(--color-border-2);
}

.info-item .label {
  font-weight: 500;
  color: var(--text-color);
}

.info-item .value {
  color: var(--text-color-secondary);
}

.prompt-content {
  padding: 16px 0;
}

.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.param-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.param-label {
  font-weight: 500;
  color: var(--text-color);
}

.param-value {
  color: var(--text-color-secondary);
}

.plugins-content,
.knowledge-content {
  padding: 16px 0;
}

.plugins-list,
.knowledge-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.plugin-item,
.knowledge-item {
  margin-bottom: 8px;
}

.empty-plugins,
.empty-knowledge {
  padding: 24px 0;
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
  background: var(--color-fill-2);
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
  background: var(--color-info-1);
  color: var(--color-info);
}

.stats-icon.messages {
  background: var(--color-success-1);
  color: var(--color-success);
}

.stats-icon.tokens {
  background: var(--color-warning-1);
  color: var(--color-warning);
}

.stats-icon.time {
  background: var(--color-primary-1);
  color: var(--color-primary);
}

.stats-content {
  flex: 1;
}

.stats-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color);
}

.stats-label {
  font-size: 14px;
  color: var(--text-color-secondary);
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
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.conversation-item:hover {
  border-color: var(--color-primary);
  background: var(--color-fill-1);
}

.conversation-info {
  flex: 1;
}

.conversation-title {
  font-weight: 500;
  color: var(--text-color);
  margin-bottom: 4px;
}

.conversation-meta {
  font-size: 12px;
  color: var(--text-color-secondary);
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
</style> 