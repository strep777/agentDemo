<template>
  <div class="plugins-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">插件管理</h1>
        <p class="page-description">管理和配置系统插件</p>
      </div>
      <div class="header-right">
        <n-button type="primary" @click="showUploadModal = true">
          <template #icon>
            <n-icon>
              <AddOutline />
            </n-icon>
          </template>
          上传插件
        </n-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <n-card class="filter-card">
      <div class="filter-content">
        <n-input
          v-model:value="searchQuery"
          placeholder="搜索插件..."
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

    <!-- 插件列表 -->
    <n-card>
      <n-data-table
        :columns="columns"
        :data="filteredPlugins"
        :pagination="pagination"
        :loading="loading"
        :row-key="(row) => row.id"
        @update:page="handlePageChange"
      />
    </n-card>

    <!-- 上传插件模态框 -->
    <n-modal
      v-model:show="showUploadModal"
      preset="card"
      title="上传插件"
      style="width: 500px"
      :mask-closable="false"
    >
      <n-upload
        ref="uploadRef"
        :custom-request="handleUpload"
        :file-list="fileList"
        :max="1"
        accept=".zip,.tar.gz"
      >
        <n-button>选择插件文件</n-button>
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

    <!-- 插件详情模态框 -->
    <n-modal
      v-model:show="showDetailModal"
      preset="card"
      title="插件详情"
      style="width: 600px"
      :mask-closable="false"
    >
      <div v-if="currentPlugin" class="plugin-detail">
        <div class="detail-item">
          <label>名称:</label>
          <span>{{ currentPlugin.name }}</span>
        </div>
        <div class="detail-item">
          <label>版本:</label>
          <span>{{ currentPlugin.version }}</span>
        </div>
        <div class="detail-item">
          <label>作者:</label>
          <span>{{ currentPlugin.author }}</span>
        </div>
        <div class="detail-item">
          <label>描述:</label>
          <span>{{ currentPlugin.description }}</span>
        </div>
        <div class="detail-item">
          <label>状态:</label>
          <n-tag :type="currentPlugin.status ? 'success' : 'error'">
            {{ currentPlugin.status ? '启用' : '禁用' }}
          </n-tag>
        </div>
        <div class="detail-item">
          <label>配置:</label>
          <n-input
            v-model:value="currentPlugin.config"
            type="textarea"
            :rows="5"
            placeholder="插件配置"
          />
        </div>
      </div>

      <template #footer>
        <div class="modal-footer">
          <n-button @click="showDetailModal = false">关闭</n-button>
          <n-button type="primary" @click="handleSaveConfig" :loading="saving">
            保存配置
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
  NTag,
  NSpace,
  NPopconfirm,
  NUpload
} from 'naive-ui'
import {
  AddOutline,
  SearchOutline,
  TrashOutline,
  PlayOutline,
  PauseOutline,
  EyeOutline,
  DownloadOutline,
  SettingsOutline
} from '@vicons/ionicons5'
import { api } from '@/api'

const message = useMessage()

// 响应式数据
const loading = ref(false)
const uploading = ref(false)
const saving = ref(false)
const plugins = ref<any[]>([])
const searchQuery = ref('')
const statusFilter = ref<string | null>(null)
const typeFilter = ref<string | null>(null)
const showUploadModal = ref(false)
const showDetailModal = ref(false)
const currentPlugin = ref<any>(null)
const fileList = ref<any[]>([])

// 筛选选项
const statusOptions = [
  { label: '启用', value: 'enabled' },
  { label: '禁用', value: 'disabled' }
]

const typeOptions = [
  { label: '数据处理', value: 'data_processing' },
  { label: 'API集成', value: 'api_integration' },
  { label: '工具插件', value: 'tool' },
  { label: '分析插件', value: 'analytics' }
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
      return h('div', { class: 'plugin-name' }, [
        h('span', { class: 'name' }, row.name),
        h('span', { class: 'version' }, `v${row.version}`)
      ])
    }
  },
  {
    title: '作者',
    key: 'author'
  },
  {
    title: '类型',
    key: 'type',
    render: (row: any) => {
      const typeMap: Record<string, string> = {
        data_processing: '数据处理',
        api_integration: 'API集成',
        tool: '工具插件',
        analytics: '分析插件'
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
    title: '安装时间',
    key: 'installed_at',
    render: (row: any) => {
      return new Date(row.installed_at).toLocaleString()
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
            type: row.status ? 'warning' : 'success',
            onClick: () => handleToggleStatus(row)
          }, { default: () => row.status ? '禁用' : '启用' }),
          h(NButton, {
            size: 'small',
            type: 'info',
            onClick: () => handleTest(row)
          }, { default: () => '测试' }),
          h(NPopconfirm, {
            onPositiveClick: () => handleDelete(row)
          }, {
            trigger: () => h(NButton, {
              size: 'small',
              type: 'error'
            }, { default: () => '卸载' }),
            default: () => '确定要卸载这个插件吗？'
          })
        ]
      })
    }
  }
]

// 筛选后的数据
const filteredPlugins = computed(() => {
  let filtered = plugins.value

  if (searchQuery.value) {
    filtered = filtered.filter(item =>
      item.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(item => item.status === (statusFilter.value === 'enabled'))
  }

  if (typeFilter.value) {
    filtered = filtered.filter(item => item.type === typeFilter.value)
  }

  return filtered
})

// 获取插件列表
const fetchPlugins = async () => {
  loading.value = true
  try {
    const response = await api.plugins.list()
    plugins.value = response.data
  } catch (error) {
    console.error('获取插件列表失败:', error)
    message.error('获取插件列表失败')
    // 使用模拟数据
    plugins.value = [
      {
        id: '1',
        name: '数据分析插件',
        version: '1.0.0',
        author: 'AI Team',
        description: '提供数据分析和可视化功能',
        type: 'analytics',
        status: true,
        installed_at: new Date().toISOString(),
        config: '{"max_data_points": 1000}'
      },
      {
        id: '2',
        name: 'API集成插件',
        version: '2.1.0',
        author: 'Integration Team',
        description: '支持多种API集成',
        type: 'api_integration',
        status: true,
        installed_at: new Date(Date.now() - 86400000).toISOString(),
        config: '{"timeout": 30}'
      },
      {
        id: '3',
        name: '数据处理工具',
        version: '1.5.2',
        author: 'Data Team',
        description: '高效的数据处理工具',
        type: 'data_processing',
        status: false,
        installed_at: new Date(Date.now() - 172800000).toISOString(),
        config: '{"batch_size": 100}'
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

// 查看插件详情
const handleView = (item: any) => {
  currentPlugin.value = { ...item }
  showDetailModal.value = true
}

// 切换插件状态
const handleToggleStatus = async (item: any) => {
  try {
    await api.plugins.toggleStatus(item.id)
    message.success(item.status ? '插件已禁用' : '插件已启用')
    await fetchPlugins()
  } catch (error) {
    console.error('切换插件状态失败:', error)
    message.error('操作失败')
  }
}

// 测试插件
const handleTest = async (item: any) => {
  try {
    await api.plugins.test(item.id)
    message.success('插件测试成功')
  } catch (error) {
    console.error('插件测试失败:', error)
    message.error('插件测试失败')
  }
}

// 卸载插件
const handleDelete = async (item: any) => {
  try {
    await api.plugins.delete(item.id)
    message.success('插件卸载成功')
    await fetchPlugins()
  } catch (error) {
    console.error('卸载插件失败:', error)
    message.error('卸载失败')
  }
}

// 处理文件上传
const handleUpload = async (options: any) => {
  const { file } = options
  try {
    await api.plugins.upload(file)
    message.success('插件上传成功')
    showUploadModal.value = false
    await fetchPlugins()
  } catch (error) {
    console.error('上传插件失败:', error)
    message.error('上传失败')
  }
}

// 处理上传提交
const handleUploadSubmit = async () => {
  if (fileList.value.length === 0) {
    message.warning('请选择插件文件')
    return
  }
  
  uploading.value = true
  try {
    for (const file of fileList.value) {
      await api.plugins.upload(file.file)
    }
    message.success('插件上传成功')
    showUploadModal.value = false
    await fetchPlugins()
  } catch (error) {
    console.error('上传失败:', error)
    message.error('上传失败')
  } finally {
    uploading.value = false
  }
}

// 保存插件配置
const handleSaveConfig = async () => {
  if (!currentPlugin.value) return
  
  saving.value = true
  try {
    await api.plugins.update(currentPlugin.value.id, {
      config: currentPlugin.value.config
    })
    message.success('配置保存成功')
    showDetailModal.value = false
    await fetchPlugins()
  } catch (error) {
    console.error('保存配置失败:', error)
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 组件挂载
onMounted(() => {
  fetchPlugins()
})
</script>

<style scoped>
.plugins-page {
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

.plugin-name {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.plugin-name .name {
  font-weight: 500;
  color: var(--n-text-color);
}

.plugin-name .version {
  font-size: 12px;
  color: var(--n-text-color-3);
}

.plugin-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.detail-item label {
  font-weight: 500;
  min-width: 80px;
  color: var(--n-text-color);
}

.detail-item span {
  flex: 1;
  color: var(--n-text-color-2);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style> 