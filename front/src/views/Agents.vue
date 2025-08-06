<template>
  <div class="agents-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">智能体管理</h1>
        <p class="page-description">管理和配置您的AI智能体</p>
      </div>
      <div class="header-right">
        <n-button type="primary" @click="showCreateModal = true">
          <template #icon>
            <n-icon>
              <AddOutline />
            </n-icon>
          </template>
          创建智能体
        </n-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <n-card class="filter-card">
      <div class="filter-content">
        <n-input
          v-model:value="searchQuery"
          placeholder="搜索智能体..."
          clearable
          class="search-input"
        >
          <template #prefix>
            <n-icon>
              <SearchOutline />
            </n-icon>
          </template>
        </n-input>

        <n-select
          v-model:value="statusFilter"
          :options="statusOptions"
          placeholder="状态筛选"
          clearable
          class="filter-select"
        />

        <n-select
          v-model:value="typeFilter"
          :options="typeOptions"
          placeholder="类型筛选"
          clearable
          class="filter-select"
        />
      </div>
    </n-card>

    <!-- 统计信息 -->
    <n-card class="stats-card">
      <div class="stats-content">
        <div class="stat-item">
          <div class="stat-number">{{ totalAgents }}</div>
          <div class="stat-label">总智能体</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ activeAgents }}</div>
          <div class="stat-label">启用中</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ inactiveAgents }}</div>
          <div class="stat-label">已禁用</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ chatAgents }}</div>
          <div class="stat-label">对话型</div>
        </div>
      </div>
    </n-card>

    <!-- 智能体列表 -->
    <n-card>
      <n-data-table
        :columns="columns"
        :data="filteredAgents"
        :pagination="pagination"
        :loading="loading"
        :row-key="(row) => row.id"
        @update:page="handlePageChange"
      />
    </n-card>

    <!-- 创建/编辑模态框 -->
    <n-modal
      v-model:show="showCreateModal"
      preset="card"
      :title="currentAgent ? '编辑智能体' : '创建智能体'"
      style="width: 600px"
      :mask-closable="false"
    >
      <n-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-placement="left"
        label-width="auto"
        require-mark-placement="right-hanging"
      >
        <n-form-item label="名称" path="name">
          <n-input v-model:value="formData.name" placeholder="请输入智能体名称" />
        </n-form-item>

        <n-form-item label="描述" path="description">
          <n-input
            v-model:value="formData.description"
            type="textarea"
            placeholder="请输入智能体描述"
            :rows="3"
          />
        </n-form-item>

        <n-form-item label="类型" path="type">
          <n-select
            v-model:value="formData.type"
            :options="typeOptions"
            placeholder="请选择智能体类型"
          />
        </n-form-item>

        <n-form-item label="模型" path="model_name">
          <n-select
            v-model:value="formData.model_name"
            :options="modelOptions"
            placeholder="请选择模型"
          />
        </n-form-item>

        <n-form-item label="状态" path="status">
          <n-switch v-model:value="formData.status" />
        </n-form-item>

        <n-form-item label="配置" path="config">
          <n-input
            v-model:value="formData.config"
            type="textarea"
            placeholder="请输入JSON配置"
            :rows="5"
          />
        </n-form-item>
      </n-form>

      <template #footer>
        <div class="modal-footer">
          <n-button @click="cancelEdit">取消</n-button>
          <n-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ currentAgent ? '更新' : '创建' }}
          </n-button>
        </div>
      </template>
    </n-modal>

    <!-- 删除确认对话框 -->
    <n-modal
      v-model:show="showDeleteModal"
      preset="dialog"
      title="确认删除"
      content="确定要删除这个智能体吗？此操作不可撤销。"
      positive-text="确定"
      negative-text="取消"
      @positive-click="confirmDelete"
      @negative-click="showDeleteModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import {
  NCard,
  NButton,
  NIcon,
  NInput,
  NSelect,
  NDataTable,
  NModal,
  NForm,
  NFormItem,
  NSwitch,
  NTag,
  NSpace,
  NPopconfirm
} from 'naive-ui'
import {
  AddOutline,
  SearchOutline,
  TrashOutline,
  EyeOutline,
  PlayOutline,
  PauseOutline
} from '@vicons/ionicons5'
import { api } from '@/api'
import type { Agent, AgentType } from '@/types/agent'

const router = useRouter()
const message = useMessage()

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const agents = ref<Agent[]>([])
const searchQuery = ref('')
const statusFilter = ref<string | null>(null)
const typeFilter = ref<string | null>(null)
const showCreateModal = ref(false)
const showDeleteModal = ref(false)
const currentAgent = ref<Agent | null>(null)
const agentToDelete = ref<Agent | null>(null)

// 表单数据
const formRef = ref()
const formData = ref({
  name: '',
  description: '',
  type: '' as AgentType,
  model_name: '',
  status: true,
  config: ''
})

// 表单验证规则
const rules = {
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

// 筛选选项
const statusOptions = [
  { label: '启用', value: 'active' },
  { label: '禁用', value: 'inactive' }
]

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

// 分页配置
const pagination = ref({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 30, 40],
  total: 0,
  onChange: (page: number) => {
    pagination.value.page = page
    fetchAgents()
  },
  onUpdatePageSize: (pageSize: number) => {
    pagination.value.pageSize = pageSize
    pagination.value.page = 1
    fetchAgents()
  }
})

// 表格列配置
const columns = [
  {
    title: '名称',
    key: 'name',
    render: (row: Agent) => {
      return h('div', { class: 'agent-name' }, [
        h('span', { class: 'name' }, row.name),
        h('span', { class: 'description' }, row.description)
      ])
    }
  },
  {
    title: '类型',
    key: 'type',
    render: (row: Agent) => {
      const typeMap: Record<AgentType, string> = {
        chat: '对话型',
        assistant: '助手型',
        specialist: '专家型',
        creative: '创意型'
      }
      return h(NTag, { type: 'primary' }, { default: () => typeMap[row.type] || row.type })
    }
  },
  {
    title: '模型',
    key: 'model_name'
  },
  {
    title: '状态',
    key: 'status',
    render: (row: Agent) => {
      return h(NSpace, { size: 'small' }, {
        default: () => [
          h(NTag, {
            type: row.status === 'active' ? 'success' : 'error'
          }, { default: () => row.status === 'active' ? '启用' : '禁用' }),
          h(NButton, {
            size: 'tiny',
            type: row.status === 'active' ? 'warning' : 'success',
            onClick: () => handleToggleStatus(row)
          }, { default: () => row.status === 'active' ? '禁用' : '启用' })
        ]
      })
    }
  },
  {
    title: '创建时间',
    key: 'created_at',
    render: (row: Agent) => {
      if (!row.created_at) return '未知时间'
      try {
        return new Date(row.created_at).toLocaleString('zh-CN')
      } catch (error) {
        return '未知时间'
      }
    }
  },
  {
    title: '操作',
    key: 'actions',
    render: (row: Agent) => {
      return h(NSpace, { size: 'small' }, {
        default: () => [
          h(NButton, {
            size: 'small',
            onClick: () => handleView(row)
          }, { default: () => '查看' }),
          h(NButton, {
            size: 'small',
            type: 'primary',
            onClick: () => handleEdit(row)
          }, { default: () => '编辑' }),
          h(NButton, {
            size: 'small',
            type: 'info',
            onClick: () => handleCopy(row)
          }, { default: () => '复制' }),
          h(NPopconfirm, {
            onPositiveClick: () => {
              agentToDelete.value = row
              confirmDelete()
            }
          }, {
            trigger: () => h(NButton, {
              size: 'small',
              type: 'error'
            }, { default: () => '删除' }),
            default: () => '确定要删除这个智能体吗？'
          })
        ]
      })
    }
  }
]

// 筛选后的数据
const filteredAgents = computed(() => {
  // 由于现在使用服务器端筛选，直接返回agents数据
  return agents.value
})

// 监听筛选条件变化
watch([searchQuery, statusFilter, typeFilter], () => {
  pagination.value.page = 1
  fetchAgents()
}, { deep: true })

// 统计信息
const totalAgents = computed(() => pagination.value.total || agents.value.length)
const activeAgents = computed(() => agents.value.filter(agent => agent.status === 'active').length)
const inactiveAgents = computed(() => agents.value.filter(agent => agent.status === 'inactive').length)
const chatAgents = computed(() => agents.value.filter(agent => agent.type === 'chat').length)

// 获取智能体列表
const fetchAgents = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.pageSize,
      search: searchQuery.value,
      status: statusFilter.value,
      type: typeFilter.value
    }
    
    console.log('🔍 获取智能体列表，参数:', params)
    const response = await api.agents.list(params)
    console.log('🔍 Agents API响应:', response)
    
    if (response.data && response.data.success) {
      // 确保数据是数组
      const responseData = response.data.data
      if (Array.isArray(responseData)) {
        agents.value = responseData
      } else if (responseData && Array.isArray(responseData.data)) {
        agents.value = responseData.data
      } else if (responseData && Array.isArray(responseData.items)) {
        agents.value = responseData.items
      } else {
        agents.value = []
      }
      
      // 确保智能体数据的一致性
      agents.value = agents.value.filter(agent => 
        agent && agent.id && agent.name && 
        (agent.status === 'active' || agent.status === 'inactive')
      )
      
      // 更新分页信息
      if (responseData && typeof responseData === 'object') {
        pagination.value.total = responseData.total || agents.value.length
      }
      
      console.log('✅ 智能体数据:', agents.value)
    } else {
      throw new Error('API响应格式错误')
    }
  } catch (error: any) {
    console.error('获取智能体列表失败:', error)
    
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
    } else {
      message.error(`获取智能体列表失败: ${error.message || '未知错误'}`)
    }
    
    // 使用模拟数据
    agents.value = [
      {
        id: '1',
        name: '客服助手',
        description: '专业的客户服务智能体',
        type: 'chat',
        model_name: 'gpt-3.5-turbo',
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: '2',
        name: '数据分析师',
        description: '数据分析专家智能体',
        type: 'specialist',
        model_name: 'gpt-4',
        status: 'active',
        created_at: new Date(Date.now() - 86400000).toISOString(),
        updated_at: new Date(Date.now() - 86400000).toISOString()
      },
      {
        id: '3',
        name: '任务执行器',
        description: '自动化任务执行智能体',
        type: 'assistant',
        model_name: 'claude-3',
        status: 'inactive',
        created_at: new Date(Date.now() - 172800000).toISOString(),
        updated_at: new Date(Date.now() - 172800000).toISOString()
      }
    ]
  } finally {
    loading.value = false
  }
}

// 处理页面变化
const handlePageChange = (page: number) => {
  // 这个方法已经不需要了，因为分页配置的onChange已经处理了
  console.log('页面变化:', page)
}

// 查看智能体详情
const handleView = (agent: Agent) => {
  router.push(`/agents/${agent.id}`)
}

// 编辑智能体
const handleEdit = (agent: Agent) => {
  currentAgent.value = agent
  formData.value = { 
    name: agent.name,
    description: agent.description,
    type: agent.type,
    model_name: agent.model_name,
    status: agent.status === 'active',
    config: JSON.stringify(agent.config || {}, null, 2)
  }
  showCreateModal.value = true
}

// 取消编辑
const cancelEdit = () => {
  showCreateModal.value = false
  currentAgent.value = null
  formData.value = {
    name: '',
    description: '',
    type: '' as AgentType,
    model_name: '',
    status: true,
    config: ''
  }
  // 重置表单验证状态
  formRef.value?.restoreValidation()
}

// 删除智能体
const handleDelete = async (agent: Agent) => {
  try {
    const response = await api.agents.delete(agent.id)
    if (response.data && response.data.success) {
      message.success('删除成功')
      await fetchAgents()
    } else {
      throw new Error('删除失败')
    }
  } catch (error: any) {
    console.error('删除智能体失败:', error)
    message.error('删除失败')
  }
}

// 确认删除
const confirmDelete = async () => {
  if (agentToDelete.value) {
    await handleDelete(agentToDelete.value)
    agentToDelete.value = null
  }
}

// 切换智能体状态
const handleToggleStatus = async (agent: Agent) => {
  try {
    const newStatus = agent.status === 'active' ? 'inactive' : 'active'
    const response = await api.agents.update(agent.id, {
      ...agent,
      status: newStatus
    })
    if (response.data && response.data.success) {
      message.success(agent.status === 'active' ? '禁用成功' : '启用成功')
      await fetchAgents()
    } else {
      throw new Error('状态更新失败')
    }
  } catch (error: any) {
    console.error('切换状态失败:', error)
    message.error('切换状态失败')
  }
}

// 复制智能体
const handleCopy = async (agent: Agent) => {
  try {
    const copyData = {
      name: `${agent.name} (副本)`,
      description: agent.description,
      type: agent.type,
      model_name: agent.model_name,
      status: 'inactive' as const, // 复制的智能体默认禁用
      config: agent.config
    }
    
    const response = await api.agents.create(copyData)
    if (response.data && response.data.success) {
      message.success('复制成功')
      await fetchAgents()
    } else {
      throw new Error('复制失败')
    }
  } catch (error: any) {
    console.error('复制智能体失败:', error)
    message.error('复制失败')
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true

    // 解析配置JSON
    let config = {}
    if (formData.value.config) {
      try {
        config = JSON.parse(formData.value.config)
      } catch (e) {
        message.error('配置JSON格式错误')
        return
      }
    }

    const submitData = {
      name: formData.value.name,
      description: formData.value.description,
      type: formData.value.type,
      model_name: formData.value.model_name,
      status: formData.value.status ? 'active' : 'inactive',
      config
    }

    if (currentAgent.value) {
      // 更新
      const response = await api.agents.update(currentAgent.value.id, submitData)
      if (response.data && response.data.success) {
        message.success('更新成功')
      } else {
        throw new Error('更新失败')
      }
    } else {
      // 创建
      const response = await api.agents.create(submitData)
      if (response.data && response.data.success) {
        message.success('创建成功')
      } else {
        throw new Error('创建失败')
      }
    }

    showCreateModal.value = false
    currentAgent.value = null
    formData.value = {
      name: '',
      description: '',
      type: '' as AgentType,
      model_name: '',
      status: true,
      config: ''
    }
    await fetchAgents()
  } catch (error: any) {
    console.error('提交失败:', error)
    if (error.message) {
      message.error(error.message)
    } else {
      message.error('提交失败')
    }
  } finally {
    submitting.value = false
  }
}

// 组件挂载
onMounted(() => {
  fetchAgents()
  console.log('智能体页面已挂载')
})
</script>

<style scoped>
.agents-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 8px 0;
  color: var(--n-text-color);
}

.page-description {
  margin: 0;
  color: var(--n-text-color-3);
}

.filter-card {
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
}

.filter-content {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input {
  flex: 1;
  max-width: 300px;
}

.filter-select {
  min-width: 150px;
}

.agent-name {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.agent-name .name {
  font-weight: 500;
  color: var(--n-text-color);
}

.agent-name .description {
  font-size: 12px;
  color: var(--n-text-color-3);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.stats-card {
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
}

.stats-content {
  display: flex;
  gap: 32px;
  justify-content: space-around;
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: var(--n-text-color);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--n-text-color-3);
}
</style> 