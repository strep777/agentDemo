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
      title="创建工作流"
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
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" @click="handleSubmit" :loading="submitting">
            确定
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
      return h(NTag, {
        type: row.status ? 'success' : 'error'
      }, { default: () => row.status ? '启用' : '禁用' })
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
    const response = await api.workflows.list()
    if (response.data && response.data.success) {
      workflows.value = response.data.data
    } else {
      // 使用模拟数据
      workflows.value = [
        {
          id: '1',
          name: '数据处理流程',
          description: '自动处理和分析数据',
          type: 'data_processing',
          status: true,
          execution_count: 156,
          created_at: new Date().toISOString()
        },
        {
          id: '2',
          name: '客户服务自动化',
          description: '自动处理客户请求和问题',
          type: 'automation',
          status: true,
          execution_count: 89,
          created_at: new Date(Date.now() - 86400000).toISOString()
        },
        {
          id: '3',
          name: '决策支持流程',
          description: '基于规则和AI的决策流程',
          type: 'decision',
          status: false,
          execution_count: 23,
          created_at: new Date(Date.now() - 172800000).toISOString()
        }
      ]
    }
  } catch (error) {
    console.error('获取工作流列表失败:', error)
    message.error('获取工作流列表失败')
    // 使用模拟数据
    workflows.value = [
      {
        id: '1',
        name: '数据处理流程',
        description: '自动处理和分析数据',
        type: 'data_processing',
        status: true,
        execution_count: 156,
        created_at: new Date().toISOString()
      },
      {
        id: '2',
        name: '客户服务自动化',
        description: '自动处理客户请求和问题',
        type: 'automation',
        status: true,
        execution_count: 89,
        created_at: new Date(Date.now() - 86400000).toISOString()
      },
      {
        id: '3',
        name: '决策支持流程',
        description: '基于规则和AI的决策流程',
        type: 'decision',
        status: false,
        execution_count: 23,
        created_at: new Date(Date.now() - 172800000).toISOString()
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

// 编辑工作流
const handleEdit = (item: any) => {
  currentWorkflow.value = item
  showEditorModal.value = true
}

// 保存工作流
const handleSaveWorkflow = async (data: any) => {
  try {
    if (currentWorkflow.value) {
      await api.workflows.update(currentWorkflow.value.id, {
        ...currentWorkflow.value,
        definition: data
      })
      message.success('工作流保存成功')
      showEditorModal.value = false
      await fetchWorkflows()
    }
  } catch (error) {
    console.error('保存工作流失败:', error)
    message.error('保存失败')
  }
}

// 测试工作流
const handleTestWorkflow = async (data: any) => {
  try {
    message.info('测试功能开发中...')
  } catch (error) {
    console.error('测试工作流失败:', error)
    message.error('测试失败')
  }
}

// 发布工作流
const handlePublishWorkflow = async (data: any) => {
  try {
    if (currentWorkflow.value) {
      await api.workflows.publish(currentWorkflow.value.id, {
        name: currentWorkflow.value.name,
        description: currentWorkflow.value.description
      })
      message.success('工作流发布成功')
    }
  } catch (error) {
    console.error('发布工作流失败:', error)
    message.error('发布失败')
  }
}

// 执行工作流
const handleExecute = (item: any) => {
  currentWorkflow.value = item
  executeData.value.input = ''
  showExecuteModal.value = true
}

// 处理执行提交
const handleExecuteSubmit = async () => {
  if (!currentWorkflow.value) return
  
  executing.value = true
  try {
    const input = executeData.value.input ? JSON.parse(executeData.value.input) : {}
    await api.workflows.execute(currentWorkflow.value.id, input)
    message.success('工作流执行成功')
    showExecuteModal.value = false
    await fetchWorkflows()
  } catch (error) {
    console.error('执行工作流失败:', error)
    message.error('执行失败')
  } finally {
    executing.value = false
  }
}

// 删除工作流
const handleDelete = async (item: any) => {
  try {
    await api.workflows.delete(item.id)
    message.success('删除成功')
    await fetchWorkflows()
  } catch (error) {
    console.error('删除工作流失败:', error)
    message.error('删除失败')
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true

    if (currentWorkflow.value) {
      // 更新
      await api.workflows.update(currentWorkflow.value.id, formData.value)
      message.success('更新成功')
    } else {
      // 创建
      await api.workflows.create(formData.value)
      message.success('创建成功')
    }

    showCreateModal.value = false
    await fetchWorkflows()
  } catch (error) {
    console.error('提交失败:', error)
    message.error('提交失败')
  } finally {
    submitting.value = false
  }
}

// 组件挂载
onMounted(() => {
  fetchWorkflows()
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