<template>
  <div class="workflows-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">工作流管理</h1>
        <p class="page-description">设计和执行自动化工作流程</p>
      </div>
      <div class="header-right">
        <n-button type="primary" @click="showCreateModal = true">
          <template #icon>
            <n-icon>
              <AddOutline />
            </n-icon>
          </template>
          创建工作流
        </n-button>
      </div>
    </div>

    <!-- 工作流列表 -->
    <n-card>
      <n-data-table
        :columns="columns"
        :data="workflows"
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
      :title="currentWorkflow ? '编辑工作流' : '创建工作流'"
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
          <n-input v-model:value="formData.name" placeholder="请输入工作流名称" />
        </n-form-item>

        <n-form-item label="描述" path="description">
          <n-input
            v-model:value="formData.description"
            type="textarea"
            placeholder="请输入工作流描述"
            :rows="3"
          />
        </n-form-item>

        <n-form-item label="类型" path="type">
          <n-select
            v-model:value="formData.type"
            :options="typeOptions"
            placeholder="请选择工作流类型"
          />
        </n-form-item>

        <n-form-item label="状态" path="status">
          <n-switch v-model:value="formData.status" />
        </n-form-item>
      </n-form>

      <template #footer>
        <div class="modal-footer">
          <n-button @click="cancelEdit">取消</n-button>
          <n-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ currentWorkflow ? '更新' : '创建' }}
          </n-button>
        </div>
      </template>
    </n-modal>

    <!-- 工作流编辑器模态框 -->
    <n-modal
      v-model:show="showEditorModal"
      preset="card"
      title="工作流编辑器"
      style="width: 95vw; height: 90vh"
      :mask-closable="false"
    >
      <WorkflowEditor
        :workflow-id="currentWorkflow?.id"
        :initial-data="currentWorkflow?.definition"
        @save="handleSaveWorkflow"
        @test="handleTestWorkflow"
        @publish="handlePublishWorkflow"
      />
    </n-modal>

    <!-- 执行工作流模态框 -->
    <n-modal
      v-model:show="showExecuteModal"
      preset="card"
      title="执行工作流"
      style="width: 500px"
      :mask-closable="false"
    >
      <n-form
        ref="executeFormRef"
        :model="executeData"
        label-placement="left"
        label-width="auto"
      >
        <n-form-item label="输入参数" path="input">
          <n-input
            v-model:value="executeData.input"
            type="textarea"
            placeholder="请输入执行参数（JSON格式）"
            :rows="8"
          />
        </n-form-item>
      </n-form>

      <template #footer>
        <div class="modal-footer">
          <n-button @click="showExecuteModal = false">取消</n-button>
          <n-button type="primary" @click="handleExecuteSubmit" :loading="executing">
            执行
          </n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
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
  PlayOutline,
  PauseOutline,
  EyeOutline
} from '@vicons/ionicons5'
import { api } from '@/api'
import WorkflowEditor from '@/components/WorkflowEditor.vue'

const message = useMessage()

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const executing = ref(false)
const workflows = ref<any[]>([])
const showCreateModal = ref(false)
const showEditorModal = ref(false)
const showExecuteModal = ref(false)
const currentWorkflow = ref<any>(null)

// 表单数据
const formRef = ref()
const executeFormRef = ref()
const formData = ref({
  name: '',
  description: '',
  type: '',
  status: true
})

const executeData = ref({
  input: ''
})

// 表单验证规则
const rules = {
  name: {
    required: true,
    message: '请输入工作流名称',
    trigger: 'blur'
  },
  type: {
    required: true,
    message: '请选择工作流类型',
    trigger: 'change'
  }
}

// 选项配置
const typeOptions = [
  { label: '数据处理', value: 'data_processing' },
  { label: '自动化任务', value: 'automation' },
  { label: '决策流程', value: 'decision' },
  { label: '集成流程', value: 'integration' }
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
    fetchWorkflows()
  },
  onUpdatePageSize: (pageSize: number) => {
    pagination.value.pageSize = pageSize
    pagination.value.page = 1
    fetchWorkflows()
  }
})

// 处理页面变化
const handlePageChange = (page: number) => {
  pagination.value.page = page
  fetchWorkflows()
}

// 表格列配置
const columns = [
  {
    title: '名称',
    key: 'name',
    render: (row: any) => {
      return h('div', { class: 'workflow-name' }, [
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
        data_processing: '数据处理',
        automation: '自动化任务',
        decision: '决策流程',
        integration: '集成流程'
      }
      return h(NTag, { type: 'primary' }, { default: () => typeMap[row.type] || row.type })
    }
  },
  {
    title: '状态',
    key: 'status',
    render: (row: any) => {
      const isActive = row.status === 'active' || row.status === true
      return h(NTag, {
        type: isActive ? 'success' : 'error'
      }, { default: () => isActive ? '启用' : '禁用' })
    }
  },
  {
    title: '执行次数',
    key: 'execution_count'
  },
  {
    title: '创建时间',
    key: 'created_at',
    render: (row: any) => {
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
    render: (row: any) => {
      return h(NSpace, { size: 'small' }, {
        default: () => [
          h(NButton, {
            size: 'small',
            onClick: () => handleEdit(row)
          }, { default: () => '编辑' }),
          h(NButton, {
            size: 'small',
            type: 'primary',
            onClick: () => handleExecute(row)
          }, { default: () => '执行' }),
          h(NPopconfirm, {
            onPositiveClick: () => handleDelete(row)
          }, {
            trigger: () => h(NButton, {
              size: 'small',
              type: 'error'
            }, { default: () => '删除' }),
            default: () => '确定要删除这个工作流吗？'
          })
        ]
      })
    }
  }
]

// 获取工作流列表
const fetchWorkflows = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      limit: pagination.value.pageSize
    }
    
    console.log('🔍 获取工作流列表，参数:', params)
    const response = await api.workflows.list(params)
    console.log('🔍 Workflows API响应:', response)
    
    if (response.data && response.data.success) {
      // 确保数据是数组
      const responseData = response.data.data
      if (Array.isArray(responseData)) {
        workflows.value = responseData
      } else if (responseData && Array.isArray(responseData.data)) {
        workflows.value = responseData.data
      } else if (responseData && Array.isArray(responseData.items)) {
        workflows.value = responseData.items
      } else {
        workflows.value = []
      }
      
      // 更新分页信息
      if (responseData && typeof responseData === 'object') {
        pagination.value.total = responseData.total || workflows.value.length
      }
      
      console.log('✅ 工作流数据:', workflows.value)
    } else {
      throw new Error('API响应格式错误')
    }
  } catch (error: any) {
    console.error('获取工作流列表失败:', error)
    
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
      message.error(`获取工作流列表失败: ${error.message || '未知错误'}`)
    }
    
    // 使用模拟数据
    workflows.value = [
      {
        id: '1',
        name: '数据处理流程',
        description: '自动处理和分析数据',
        type: 'data_processing',
        status: true,
        execution_count: 156,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: '2',
        name: '客户服务自动化',
        description: '自动处理客户请求和问题',
        type: 'automation',
        status: true,
        execution_count: 89,
        created_at: new Date(Date.now() - 86400000).toISOString(),
        updated_at: new Date(Date.now() - 86400000).toISOString()
      },
      {
        id: '3',
        name: '决策支持流程',
        description: '基于规则和AI的决策流程',
        type: 'decision',
        status: false,
        execution_count: 23,
        created_at: new Date(Date.now() - 172800000).toISOString(),
        updated_at: new Date(Date.now() - 172800000).toISOString()
      }
    ]
  } finally {
    loading.value = false
  }
}

// 编辑工作流
const handleEdit = (item: any) => {
  currentWorkflow.value = item
  formData.value = {
    name: item.name,
    description: item.description,
    type: item.type,
    status: item.status === 'active' || item.status === true
  }
  showCreateModal.value = true
}

// 取消编辑
const cancelEdit = () => {
  showCreateModal.value = false
  currentWorkflow.value = null
  formData.value = {
    name: '',
    description: '',
    type: '',
    status: true
  }
  // 重置表单验证状态
  formRef.value?.restoreValidation()
}

// 保存工作流
const handleSaveWorkflow = async (data: any) => {
  try {
    if (currentWorkflow.value) {
      const response = await api.workflows.update(currentWorkflow.value.id, {
        ...currentWorkflow.value,
        definition: data
      })
      if (response.data && response.data.success) {
        message.success('工作流保存成功')
        showEditorModal.value = false
        await fetchWorkflows()
      } else {
        throw new Error('保存失败')
      }
    }
  } catch (error: any) {
    console.error('保存工作流失败:', error)
    message.error('保存失败')
  }
}

// 测试工作流
const handleTestWorkflow = async (data: any) => {
  try {
    message.info('测试功能开发中...')
    // TODO: 实现工作流测试功能
    console.log('测试工作流数据:', data)
  } catch (error: any) {
    console.error('测试工作流失败:', error)
    message.error('测试失败')
  }
}

// 发布工作流
const handlePublishWorkflow = async (data: any) => {
  try {
    if (currentWorkflow.value) {
      const response = await api.workflows.publish(currentWorkflow.value.id, {
        name: currentWorkflow.value.name,
        description: currentWorkflow.value.description
      })
      if (response.data && response.data.success) {
        message.success('工作流发布成功')
      } else {
        throw new Error('发布失败')
      }
    }
  } catch (error: any) {
    console.error('发布工作流失败:', error)
    message.error('发布失败')
  }
}

// 执行工作流
const handleExecute = (item: any) => {
  currentWorkflow.value = item
  executeData.value.input = ''
  showExecuteModal.value = true
  console.log('准备执行工作流:', item)
}

// 处理执行提交
const handleExecuteSubmit = async () => {
  if (!currentWorkflow.value) return
  
  executing.value = true
  try {
    let input = {}
    if (executeData.value.input) {
      try {
        input = JSON.parse(executeData.value.input)
      } catch (e) {
        message.error('输入参数JSON格式错误')
        return
      }
    }
    
    const response = await api.workflows.execute(currentWorkflow.value.id, input)
    if (response.data && response.data.success) {
      message.success('工作流执行成功')
      showExecuteModal.value = false
      await fetchWorkflows()
    } else {
      throw new Error('执行失败')
    }
  } catch (error: any) {
    console.error('执行工作流失败:', error)
    message.error('执行失败')
  } finally {
    executing.value = false
  }
}

// 删除工作流
const handleDelete = async (item: any) => {
  try {
    const response = await api.workflows.delete(item.id)
    if (response.data && response.data.success) {
      message.success('删除成功')
      await fetchWorkflows()
    } else {
      throw new Error('删除失败')
    }
  } catch (error: any) {
    console.error('删除工作流失败:', error)
    message.error('删除失败')
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true

    const submitData = {
      name: formData.value.name,
      description: formData.value.description,
      type: formData.value.type,
      status: formData.value.status ? 'active' : 'inactive'
    }

    if (currentWorkflow.value) {
      // 更新
      const response = await api.workflows.update(currentWorkflow.value.id, submitData)
      if (response.data && response.data.success) {
        message.success('更新成功')
      } else {
        throw new Error('更新失败')
      }
    } else {
      // 创建
      const response = await api.workflows.create(submitData)
      if (response.data && response.data.success) {
        message.success('创建成功')
      } else {
        throw new Error('创建失败')
      }
    }

    showCreateModal.value = false
    currentWorkflow.value = null
    formData.value = {
      name: '',
      description: '',
      type: '',
      status: true
    }
    await fetchWorkflows()
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
  fetchWorkflows()
  console.log('工作流页面已挂载')
})
</script>

<style scoped>
.workflows-page {
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

.workflow-name {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.workflow-name .name {
  font-weight: 500;
  color: var(--n-text-color);
}

.workflow-name .description {
  font-size: 12px;
  color: var(--n-text-color-3);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style> 