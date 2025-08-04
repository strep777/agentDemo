<template>
  <div class="training-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">智能体训练</h1>
        <p class="page-description">训练和优化您的AI智能体</p>
      </div>
      <div class="header-right">
        <n-button type="primary" @click="showCreateModal = true">
          <template #icon>
            <n-icon>
              <AddOutline />
            </n-icon>
          </template>
          创建训练任务
        </n-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <n-card class="filter-card">
      <div class="filter-content">
        <n-input
          v-model:value="searchQuery"
          placeholder="搜索训练任务..."
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
          <div class="stat-number">{{ totalTraining }}</div>
          <div class="stat-label">总任务</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ runningTraining }}</div>
          <div class="stat-label">运行中</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ completedTraining }}</div>
          <div class="stat-label">已完成</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ failedTraining }}</div>
          <div class="stat-label">失败</div>
        </div>
      </div>
    </n-card>

    <!-- 训练任务列表 -->
    <n-card>
      <n-data-table
        :columns="columns"
        :data="filteredTraining"
        :pagination="pagination"
        :loading="loading"
        :row-key="(row) => row.id"
        @update:page="handlePageChange"
      />
    </n-card>

    <!-- 创建训练任务模态框 -->
    <n-modal
      v-model:show="showCreateModal"
      preset="card"
      title="创建训练任务"
      style="width: 700px"
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
        <n-form-item label="任务名称" path="name">
          <n-input v-model:value="formData.name" placeholder="请输入训练任务名称" />
        </n-form-item>

        <n-form-item label="描述" path="description">
          <n-input
            v-model:value="formData.description"
            type="textarea"
            placeholder="请输入训练任务描述"
            :rows="3"
          />
        </n-form-item>

        <n-form-item label="智能体" path="agent_id">
          <n-select
            v-model:value="formData.agent_id"
            :options="agentOptions"
            placeholder="请选择要训练的智能体"
          />
        </n-form-item>

        <n-form-item label="训练类型" path="type">
          <n-select
            v-model:value="formData.type"
            :options="typeOptions"
            placeholder="请选择训练类型"
          />
        </n-form-item>

        <n-form-item label="训练数据" path="training_data">
          <n-input
            v-model:value="formData.training_data"
            type="textarea"
            placeholder="请输入训练数据配置（JSON格式）"
            :rows="5"
          />
        </n-form-item>

        <n-form-item label="训练参数" path="parameters">
          <n-input
            v-model:value="formData.parameters"
            type="textarea"
            placeholder="请输入训练参数（JSON格式）"
            :rows="5"
          />
        </n-form-item>
      </n-form>

      <template #footer>
        <div class="modal-footer">
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" @click="handleSubmit" :loading="submitting">
            确定
          </n-button>
        </div>
      </template>
    </n-modal>

    <!-- 训练详情模态框 -->
    <n-modal
      v-model:show="showDetailModal"
      preset="card"
      title="训练详情"
      style="width: 800px"
      :mask-closable="false"
    >
      <div v-if="currentTraining" class="training-detail">
        <div class="detail-section">
          <h3>基本信息</h3>
          <div class="detail-grid">
            <div class="detail-item">
              <label>任务名称:</label>
              <span>{{ currentTraining.name }}</span>
            </div>
            <div class="detail-item">
              <label>状态:</label>
              <n-tag :type="getStatusType(currentTraining.status)">
                {{ getStatusText(currentTraining.status) }}
              </n-tag>
            </div>
            <div class="detail-item">
              <label>进度:</label>
              <n-progress
                :percentage="currentTraining.progress || 0"
                :status="getProgressStatus(currentTraining.status)"
              />
            </div>
            <div class="detail-item">
              <label>开始时间:</label>
              <span>{{ formatTime(currentTraining.started_at) }}</span>
            </div>
            <div class="detail-item">
              <label>预计完成:</label>
              <span>{{ formatTime(currentTraining.estimated_completion) }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h3>训练指标</h3>
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-value">{{ currentTraining.metrics?.accuracy || 0 }}%</div>
              <div class="metric-label">准确率</div>
            </div>
            <div class="metric-card">
              <div class="metric-value">{{ currentTraining.metrics?.loss || 0 }}</div>
              <div class="metric-label">损失值</div>
            </div>
            <div class="metric-card">
              <div class="metric-value">{{ currentTraining.metrics?.epochs || 0 }}</div>
              <div class="metric-label">训练轮数</div>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h3>训练日志</h3>
          <div class="log-container">
            <pre class="log-content">{{ currentTraining.logs || '暂无日志' }}</pre>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="modal-footer">
          <n-button @click="showDetailModal = false">关闭</n-button>
          <n-button 
            v-if="currentTraining?.status === 'running'"
            type="warning" 
            @click="handleStop"
            :loading="stopping"
          >
            停止训练
          </n-button>
          <n-button 
            v-if="currentTraining?.status === 'stopped'"
            type="primary" 
            @click="handleStart"
            :loading="starting"
          >
            继续训练
          </n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, h } from 'vue'
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
  NTag,
  NSpace,
  NPopconfirm,
  NProgress
} from 'naive-ui'
import {
  AddOutline,
  SearchOutline,
  TrashOutline,
  PlayOutline,
  PauseOutline,
  EyeOutline,
  StopOutline
} from '@vicons/ionicons5'
import { api } from '@/api'
import dayjs from 'dayjs'

const message = useMessage()

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const starting = ref(false)
const stopping = ref(false)
const training = ref<any[]>([])
const searchQuery = ref('')
const statusFilter = ref<string | null>(null)
const typeFilter = ref<string | null>(null)
const showCreateModal = ref(false)
const showDetailModal = ref(false)
const currentTraining = ref<any>(null)

// 表单数据
const formRef = ref()
const formData = ref({
  name: '',
  description: '',
  agent_id: '',
  type: '',
  training_data: '',
  parameters: ''
})

// 表单验证规则
const rules = {
  name: {
    required: true,
    message: '请输入训练任务名称',
    trigger: 'blur'
  },
  agent_id: {
    required: true,
    message: '请选择智能体',
    trigger: 'change'
  },
  type: {
    required: true,
    message: '请选择训练类型',
    trigger: 'change'
  }
}

// 筛选选项
const statusOptions = [
  { label: '运行中', value: 'running' },
  { label: '已完成', value: 'completed' },
  { label: '已停止', value: 'stopped' },
  { label: '失败', value: 'failed' }
]

const typeOptions = [
  { label: '监督学习', value: 'supervised' },
  { label: '强化学习', value: 'reinforcement' },
  { label: '微调', value: 'fine_tuning' },
  { label: '迁移学习', value: 'transfer' }
]

const agentOptions = [
  { label: '客服助手', value: '1' },
  { label: '数据分析师', value: '2' },
  { label: '任务执行器', value: '3' }
]

// 分页配置
const pagination = ref({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 30, 40],
  onChange: (page: number) => {
    pagination.value.page = page
  },
  onUpdatePageSize: (pageSize: number) => {
    pagination.value.pageSize = pageSize
    pagination.value.page = 1
  }
})

// 表格列配置
const columns = [
  {
    title: '任务名称',
    key: 'name',
    render: (row: any) => {
      return h('div', { class: 'training-name' }, [
        h('span', { class: 'name' }, row.name),
        h('span', { class: 'description' }, row.description)
      ])
    }
  },
  {
    title: '类型',
    key: 'type',
    render: (row: any) => {
      const typeMap: Record<string, string> = {
        supervised: '监督学习',
        reinforcement: '强化学习',
        fine_tuning: '微调',
        transfer: '迁移学习'
      }
      return h(NTag, { type: 'primary' }, { default: () => typeMap[row.type] || row.type })
    }
  },
  {
    title: '状态',
    key: 'status',
    render: (row: any) => {
      return h(NTag, {
        type: getStatusType(row.status)
      }, { default: () => getStatusText(row.status) })
    }
  },
  {
    title: '进度',
    key: 'progress',
    render: (row: any) => {
      return h(NProgress, {
        percentage: row.progress || 0,
        status: getProgressStatus(row.status),
        showIndicator: false
      })
    }
  },
  {
    title: '创建时间',
    key: 'created_at',
    render: (row: any) => {
      return new Date(row.created_at).toLocaleString()
    }
  },
  {
    title: '操作',
    key: 'actions',
    render: (row: any) => {
      return h(NSpace, { size: 'small' }, {
        default: () => [
          h(NButton, {
            size: 'small',
            onClick: () => handleView(row)
          }, { default: () => '详情' }),
          h(NButton, {
            size: 'small',
            type: 'primary',
            onClick: () => handleStart(row),
            disabled: row.status === 'running'
          }, { default: () => '启动' }),
          h(NButton, {
            size: 'small',
            type: 'warning',
            onClick: () => handleStop(row),
            disabled: row.status !== 'running'
          }, { default: () => '停止' }),
          h(NButton, {
            size: 'small',
            type: 'info',
            onClick: () => handleCopy(row)
          }, { default: () => '复制' }),
          h(NPopconfirm, {
            onPositiveClick: () => handleDelete(row)
          }, {
            trigger: () => h(NButton, {
              size: 'small',
              type: 'error'
            }, { default: () => '删除' }),
            default: () => '确定要删除这个训练任务吗？'
          })
        ]
      })
    }
  }
]

// 筛选后的数据
const filteredTraining = computed(() => {
  let filtered = training.value

  if (searchQuery.value) {
    filtered = filtered.filter(item =>
      item.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(item => item.status === statusFilter.value)
  }

  if (typeFilter.value) {
    filtered = filtered.filter(item => item.type === typeFilter.value)
  }

  return filtered
})

// 统计信息
const totalTraining = computed(() => training.value.length)
const runningTraining = computed(() => training.value.filter(item => item.status === 'running').length)
const completedTraining = computed(() => training.value.filter(item => item.status === 'completed').length)
const failedTraining = computed(() => training.value.filter(item => item.status === 'failed').length)

// 获取状态类型
const getStatusType = (status: string): 'success' | 'info' | 'warning' | 'error' | 'default' => {
  const typeMap: Record<string, 'success' | 'info' | 'warning' | 'error' | 'default'> = {
    running: 'success',
    completed: 'info',
    stopped: 'warning',
    failed: 'error'
  }
  return typeMap[status] || 'default'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    running: '运行中',
    completed: '已完成',
    stopped: '已停止',
    failed: '失败'
  }
  return textMap[status] || status
}

// 获取进度状态
const getProgressStatus = (status: string): 'success' | 'warning' | 'error' | 'default' => {
  const statusMap: Record<string, 'success' | 'warning' | 'error' | 'default'> = {
    running: 'success',
    completed: 'success',
    stopped: 'warning',
    failed: 'error'
  }
  return statusMap[status] || 'default'
}

// 格式化时间
const formatTime = (timestamp: string) => {
  if (!timestamp) return '未知'
  return dayjs(timestamp).format('YYYY-MM-DD HH:mm:ss')
}

// 获取训练任务列表
const fetchTraining = async () => {
  loading.value = true
  try {
    const response = await api.training.list()
    if (response.data && response.data.success) {
      training.value = response.data.data
    } else {
      throw new Error('API响应格式错误')
    }
  } catch (error) {
    console.error('获取训练任务列表失败:', error)
    message.error('获取训练任务列表失败')
    // 使用模拟数据
    training.value = [
      {
        id: '1',
        name: '客服助手训练',
        description: '训练客服助手模型',
        type: 'supervised',
        status: 'running',
        progress: 65,
        created_at: new Date().toISOString(),
        started_at: new Date(Date.now() - 3600000).toISOString(),
        estimated_completion: new Date(Date.now() + 1800000).toISOString(),
        metrics: {
          accuracy: 85.6,
          loss: 0.12,
          epochs: 15
        },
        logs: 'Epoch 15/20 - Loss: 0.12 - Accuracy: 85.6%'
      },
      {
        id: '2',
        name: '数据分析师训练',
        description: '训练数据分析模型',
        type: 'fine_tuning',
        status: 'completed',
        progress: 100,
        created_at: new Date(Date.now() - 86400000).toISOString(),
        started_at: new Date(Date.now() - 172800000).toISOString(),
        estimated_completion: new Date(Date.now() - 86400000).toISOString(),
        metrics: {
          accuracy: 92.3,
          loss: 0.08,
          epochs: 20
        },
        logs: 'Training completed successfully'
      },
      {
        id: '3',
        name: '任务执行器训练',
        description: '训练任务执行模型',
        type: 'reinforcement',
        status: 'stopped',
        progress: 30,
        created_at: new Date(Date.now() - 172800000).toISOString(),
        started_at: new Date(Date.now() - 259200000).toISOString(),
        estimated_completion: null,
        metrics: {
          accuracy: 45.2,
          loss: 0.35,
          epochs: 8
        },
        logs: 'Training stopped by user'
      }
    ]
  } finally {
    loading.value = false
  }
}

// 处理页面变化
const handlePageChange = (page: number) => {
  pagination.value.page = page
}

// 查看训练详情
const handleView = (item: any) => {
  currentTraining.value = { ...item }
  showDetailModal.value = true
}

// 启动训练
const handleStart = async (item: any) => {
  starting.value = true
  try {
    const response = await api.training.start(item.id)
    if (response.data && response.data.success) {
      message.success('训练已启动')
      await fetchTraining()
    } else {
      throw new Error('启动失败')
    }
  } catch (error) {
    console.error('启动训练失败:', error)
    message.error('启动失败')
  } finally {
    starting.value = false
  }
}

// 停止训练
const handleStop = async (item: any) => {
  stopping.value = true
  try {
    const response = await api.training.stop(item.id)
    if (response.data && response.data.success) {
      message.success('训练已停止')
      await fetchTraining()
    } else {
      throw new Error('停止失败')
    }
  } catch (error) {
    console.error('停止训练失败:', error)
    message.error('停止失败')
  } finally {
    stopping.value = false
  }
}

// 删除训练任务
const handleDelete = async (item: any) => {
  try {
    const response = await api.training.delete(item.id)
    if (response.data && response.data.success) {
      message.success('删除成功')
      await fetchTraining()
    } else {
      throw new Error('删除失败')
    }
  } catch (error) {
    console.error('删除训练任务失败:', error)
    message.error('删除失败')
  }
}

// 复制训练任务
const handleCopy = async (item: any) => {
  try {
    const copyData = {
      ...item,
      name: `${item.name} (副本)`,
      status: 'pending',
      progress: 0
    }
    delete copyData.id
    delete copyData.created_at
    delete copyData.started_at
    delete copyData.estimated_completion
    delete copyData.metrics
    delete copyData.logs
    
    const response = await api.training.create(copyData)
    if (response.data && response.data.success) {
      message.success('复制成功')
      await fetchTraining()
    } else {
      throw new Error('复制失败')
    }
  } catch (error) {
    console.error('复制训练任务失败:', error)
    message.error('复制失败')
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true

    const response = await api.training.create(formData.value)
    if (response.data && response.data.success) {
      message.success('创建成功')
      showCreateModal.value = false
      formData.value = {
        name: '',
        description: '',
        agent_id: '',
        type: '',
        training_data: '',
        parameters: ''
      }
      await fetchTraining()
    } else {
      throw new Error('创建失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    message.error('提交失败')
  } finally {
    submitting.value = false
  }
}

// 组件挂载
onMounted(() => {
  fetchTraining()
  
  // 定时更新运行中的训练任务状态
  const interval = setInterval(() => {
    const runningTasks = training.value.filter(item => item.status === 'running')
    if (runningTasks.length > 0) {
      fetchTraining()
    }
  }, 10000) // 每10秒更新一次
  
  // 组件卸载时清除定时器
  onUnmounted(() => {
    clearInterval(interval)
  })
})
</script>

<style scoped>
.training-page {
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

.training-name {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.training-name .name {
  font-weight: 500;
  color: var(--n-text-color);
}

.training-name .description {
  font-size: 12px;
  color: var(--n-text-color-3);
}

.training-detail {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-section {
  border: 1px solid var(--n-border-color);
  border-radius: 8px;
  padding: 16px;
}

.detail-section h3 {
  margin: 0 0 16px 0;
  color: var(--n-text-color);
  font-size: 16px;
  font-weight: 500;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item label {
  font-size: 12px;
  color: var(--n-text-color-3);
}

.detail-item span {
  color: var(--n-text-color);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
}

.metric-card {
  text-align: center;
  padding: 16px;
  border: 1px solid var(--n-border-color);
  border-radius: 8px;
  background: var(--n-color);
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--n-text-color);
  margin-bottom: 4px;
}

.metric-label {
  font-size: 12px;
  color: var(--n-text-color-3);
}

.log-container {
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  border-radius: 4px;
  padding: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.log-content {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: var(--n-text-color-2);
  white-space: pre-wrap;
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