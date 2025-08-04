<template>
  <div class="knowledge-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">知识库管理</h1>
        <p class="page-description">管理和维护您的知识库资源</p>
      </div>
      <div class="header-right">
        <n-button type="primary" @click="showCreateModal = true">
          <template #icon>
            <n-icon>
              <AddOutline />
            </n-icon>
          </template>
          创建知识库
        </n-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <n-card class="filter-card">
      <div class="filter-content">
        <n-input
          v-model:value="searchQuery"
          placeholder="搜索知识库..."
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

    <!-- 知识库列表 -->
    <n-card>
      <n-data-table
        :columns="columns"
        :data="filteredKnowledge"
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
      title="创建知识库"
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
          <n-input v-model:value="formData.name" placeholder="请输入知识库名称" />
        </n-form-item>

        <n-form-item label="描述" path="description">
          <n-input
            v-model:value="formData.description"
            type="textarea"
            placeholder="请输入知识库描述"
            :rows="3"
          />
        </n-form-item>

        <n-form-item label="类型" path="type">
          <n-select
            v-model:value="formData.type"
            :options="typeOptions"
            placeholder="请选择知识库类型"
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
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" @click="handleSubmit" :loading="submitting">
            确定
          </n-button>
        </div>
      </template>
    </n-modal>

    <!-- 上传文件模态框 -->
    <n-modal
      v-model:show="showUploadModal"
      preset="card"
      title="上传文件"
      style="width: 500px"
      :mask-closable="false"
    >
      <n-upload
        ref="uploadRef"
        :custom-request="handleUpload"
        :file-list="fileList"
        :max="5"
        multiple
        accept=".txt,.pdf,.doc,.docx,.md"
      >
        <n-button>选择文件</n-button>
      </n-upload>

      <template #footer>
        <div class="modal-footer">
          <n-button @click="showUploadModal = false">取消</n-button>
          <n-button type="primary" @click="handleUploadSubmit" :loading="uploading">
            上传
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
  NPopconfirm,
  NUpload
} from 'naive-ui'
import {
  AddOutline,
  SearchOutline,
  TrashOutline,
  DownloadOutline,
  RefreshOutline,
  EyeOutline
} from '@vicons/ionicons5'
import { api } from '@/api'

const message = useMessage()

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const uploading = ref(false)
const knowledge = ref<any[]>([])
const searchQuery = ref('')
const statusFilter = ref<string | null>(null)
const typeFilter = ref<string | null>(null)
const showCreateModal = ref(false)
const showUploadModal = ref(false)
const currentKnowledge = ref<any>(null)
const fileList = ref<any[]>([])

// 表单数据
const formRef = ref()
const uploadRef = ref()
const formData = ref({
  name: '',
  description: '',
  type: '',
  status: true,
  config: ''
})

// 表单验证规则
const rules = {
  name: {
    required: true,
    message: '请输入知识库名称',
    trigger: 'blur'
  },
  type: {
    required: true,
    message: '请选择知识库类型',
    trigger: 'change'
  }
}

// 筛选选项
const statusOptions = [
  { label: '启用', value: 'active' },
  { label: '禁用', value: 'inactive' }
]

const typeOptions = [
  { label: '文档库', value: 'document' },
  { label: 'FAQ库', value: 'faq' },
  { label: '知识图谱', value: 'knowledge_graph' },
  { label: '向量库', value: 'vector' }
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
      return h('div', { class: 'knowledge-name' }, [
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
        document: '文档库',
        faq: 'FAQ库',
        knowledge_graph: '知识图谱',
        vector: '向量库'
      }
      return h(NTag, { type: 'primary' }, { default: () => typeMap[row.type] || row.type })
    }
  },
  {
    title: '文档数量',
    key: 'document_count'
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
          }, { default: () => '查看' }),
          h(NButton, {
            size: 'small',
            type: 'primary',
            onClick: () => handleUpload(row)
          }, { default: () => '上传' }),
          h(NButton, {
            size: 'small',
            type: 'info',
            onClick: () => handleRebuildIndex(row)
          }, { default: () => '重建索引' }),
          h(NPopconfirm, {
            onPositiveClick: () => handleDelete(row)
          }, {
            trigger: () => h(NButton, {
              size: 'small',
              type: 'error'
            }, { default: () => '删除' }),
            default: () => '确定要删除这个知识库吗？'
          })
        ]
      })
    }
  }
]

// 筛选后的数据
const filteredKnowledge = computed(() => {
  let filtered = knowledge.value

  if (searchQuery.value) {
    filtered = filtered.filter(item =>
      item.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(item => item.status === (statusFilter.value === 'active'))
  }

  if (typeFilter.value) {
    filtered = filtered.filter(item => item.type === typeFilter.value)
  }

  return filtered
})

// 获取知识库列表
const fetchKnowledge = async () => {
  loading.value = true
  try {
    const response = await api.knowledge.list()
    knowledge.value = response.data
  } catch (error) {
    console.error('获取知识库列表失败:', error)
    message.error('获取知识库列表失败')
    // 使用模拟数据
    knowledge.value = [
      {
        id: '1',
        name: '产品文档库',
        description: '包含所有产品相关文档',
        type: 'document',
        document_count: 25,
        status: true,
        created_at: new Date().toISOString()
      },
      {
        id: '2',
        name: '客服FAQ库',
        description: '常见问题解答库',
        type: 'faq',
        document_count: 150,
        status: true,
        created_at: new Date(Date.now() - 86400000).toISOString()
      },
      {
        id: '3',
        name: '技术知识图谱',
        description: '技术知识关联图谱',
        type: 'knowledge_graph',
        document_count: 8,
        status: false,
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

// 查看知识库详情
const handleView = (item: any) => {
  // 这里可以跳转到知识库详情页面
  message.info(`查看知识库: ${item.name}`)
}

// 上传文件
const handleUpload = (item: any) => {
  currentKnowledge.value = item
  showUploadModal.value = true
}

// 处理文件上传
const handleUploadSubmit = async () => {
  if (!currentKnowledge.value) return
  
  uploading.value = true
  try {
    for (const file of fileList.value) {
      await api.knowledge.upload(file.file)
    }
    message.success('上传成功')
    showUploadModal.value = false
    await fetchKnowledge()
  } catch (error) {
    console.error('上传失败:', error)
    message.error('上传失败')
  } finally {
    uploading.value = false
  }
}

// 重建索引
const handleRebuildIndex = async (item: any) => {
  try {
    await api.knowledge.rebuildIndex(item.id)
    message.success('索引重建成功')
  } catch (error) {
    console.error('重建索引失败:', error)
    message.error('重建索引失败')
  }
}

// 删除知识库
const handleDelete = async (item: any) => {
  try {
    await api.knowledge.delete(item.id)
    message.success('删除成功')
    await fetchKnowledge()
  } catch (error) {
    console.error('删除知识库失败:', error)
    message.error('删除失败')
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true

    if (currentKnowledge.value) {
      // 更新
      await api.knowledge.update(currentKnowledge.value.id, formData.value)
      message.success('更新成功')
    } else {
      // 创建
      await api.knowledge.create(formData.value)
      message.success('创建成功')
    }

    showCreateModal.value = false
    await fetchKnowledge()
  } catch (error) {
    console.error('提交失败:', error)
    message.error('提交失败')
  } finally {
    submitting.value = false
  }
}

// 组件挂载
onMounted(() => {
  fetchKnowledge()
})
</script>

<style scoped>
.knowledge-page {
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

.knowledge-name {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.knowledge-name .name {
  font-weight: 500;
  color: var(--n-text-color);
}

.knowledge-name .description {
  font-size: 12px;
  color: var(--n-text-color-3);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style> 