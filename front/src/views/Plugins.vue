<template>
  <div class="plugins-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">插件管理</h1>
        <p class="page-description">管理和配置系统插件，支持上传、安装、测试等功能</p>
      </div>
      <div class="header-right">
        <n-space>
          <n-button @click="refreshPlugins" :loading="loading">
            <template #icon>
              <n-icon><RefreshOutline /></n-icon>
            </template>
            刷新
          </n-button>
          <n-button type="primary" @click="showUploadModal = true">
            <template #icon>
              <n-icon><AddOutline /></n-icon>
            </template>
            上传插件
          </n-button>
        </n-space>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <n-card class="filter-card">
      <div class="filter-content">
        <n-input
          v-model:value="searchQuery"
          placeholder="搜索插件名称、描述、作者..."
          clearable
          class="search-input"
          @input="handleSearch"
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
          @update:value="handleFilterChange"
        />

        <n-select
          v-model:value="typeFilter"
          :options="typeOptions"
          placeholder="类型筛选"
          clearable
          class="filter-select"
          @update:value="handleFilterChange"
        />

        <n-button @click="clearFilters" :disabled="!hasActiveFilters">
          清除筛选
        </n-button>
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
        @update:page-size="handlePageSizeChange"
      />
    </n-card>

    <!-- 上传插件模态框 -->
    <n-modal
      v-model:show="showUploadModal"
      preset="card"
      title="上传插件"
      style="width: 600px"
      :mask-closable="false"
      :closable="!uploading"
    >
      <div class="upload-content">
        <n-alert type="info" :show-icon="false" class="upload-tip">
          <template #header>
            <div class="upload-tip-header">
              <n-icon size="16" color="var(--n-info-color)">
                <InformationCircleOutline />
              </n-icon>
              <span>插件上传说明</span>
            </div>
          </template>
          <div class="upload-tip-content">
            <p>• 支持ZIP格式的插件文件</p>
            <p>• 插件包必须包含 plugin.json 配置文件</p>
            <p>• 插件名称不能重复</p>
            <p>• 上传后插件默认为禁用状态</p>
          </div>
        </n-alert>

        <n-upload
          ref="uploadRef"
          :custom-request="handleUpload"
          :file-list="fileList"
          :max="1"
          accept=".zip"
          :disabled="uploading"
          @change="handleFileChange"
        >
          <n-upload-dragger>
            <div class="upload-dragger">
              <n-icon size="48" color="var(--n-text-color-3)">
                <CloudUploadOutline />
              </n-icon>
              <p class="upload-text">点击或拖拽文件到此处上传</p>
              <p class="upload-hint">支持 .zip 格式</p>
            </div>
          </n-upload-dragger>
        </n-upload>

        <div v-if="uploadError" class="upload-error">
          <n-alert type="error" :show-icon="false">
            {{ uploadError }}
          </n-alert>
        </div>
      </div>

      <template #footer>
        <div class="modal-footer">
          <n-button @click="cancelUpload" :disabled="uploading">取消</n-button>
          <n-button 
            type="primary" 
            @click="handleUploadSubmit" 
            :loading="uploading"
            :disabled="fileList.length === 0"
          >
            {{ uploading ? '上传中...' : '上传' }}
          </n-button>
        </div>
      </template>
    </n-modal>

    <!-- 插件详情模态框 -->
    <n-modal
      v-model:show="showDetailModal"
      preset="card"
      title="插件详情"
      style="width: 700px"
      :mask-closable="false"
    >
      <div v-if="currentPlugin" class="plugin-detail">
        <n-tabs type="line" animated>
          <n-tab-pane name="basic" tab="基本信息">
            <div class="detail-section">
              <div class="detail-item">
                <label>插件名称:</label>
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
                <label>类型:</label>
                <n-tag :type="getTypeTagType(currentPlugin.type)">
                  {{ getTypeLabel(currentPlugin.type) }}
                </n-tag>
              </div>
              <div class="detail-item">
                <label>状态:</label>
                <n-tag :type="currentPlugin.status === 'active' ? 'success' : 'error'">
                  {{ currentPlugin.status === 'active' ? '启用' : '禁用' }}
                </n-tag>
              </div>
              <div class="detail-item">
                <label>描述:</label>
                <span>{{ currentPlugin.description || '暂无描述' }}</span>
              </div>
              <div class="detail-item">
                <label>创建时间:</label>
                <span>{{ formatDateTime(currentPlugin.created_at) }}</span>
              </div>
              <div class="detail-item">
                <label>更新时间:</label>
                <span>{{ formatDateTime(currentPlugin.updated_at) }}</span>
              </div>
            </div>
          </n-tab-pane>

          <n-tab-pane name="config" tab="配置管理">
            <div class="detail-section">
              <div class="config-editor">
                <div class="config-header">
                  <span>插件配置 (JSON格式)</span>
                  <n-button size="small" @click="validateConfig" :loading="validating">
                    验证配置
                  </n-button>
                </div>
                <n-input
                  v-model:value="currentPlugin.config"
                  type="textarea"
                  :rows="12"
                  placeholder="请输入插件配置，JSON格式"
                  :status="configStatus"
                />
                <div v-if="configError" class="config-error">
                  <n-alert type="error" :show-icon="false">
                    {{ configError }}
                  </n-alert>
                </div>
              </div>
            </div>
          </n-tab-pane>

          <n-tab-pane name="test" tab="插件测试">
            <div class="detail-section">
              <div class="test-section">
                <div class="test-input">
                  <label>测试输入 (JSON格式):</label>
                  <n-input
                    v-model:value="testInput"
                    type="textarea"
                    :rows="6"
                    placeholder="请输入测试数据，JSON格式"
                  />
                </div>
                <div class="test-actions">
                  <n-button @click="testPlugin" :loading="testing" type="primary">
                    执行测试
                  </n-button>
                  <n-button @click="clearTestResult">
                    清除结果
                  </n-button>
                </div>
                <div v-if="testResult" class="test-result">
                  <label>测试结果:</label>
                  <n-input
                    :value="JSON.stringify(testResult, null, 2)"
                    type="textarea"
                    :rows="8"
                    readonly
                  />
                </div>
              </div>
            </div>
          </n-tab-pane>
        </n-tabs>
      </div>

      <template #footer>
        <div class="modal-footer">
          <n-space>
            <n-button @click="showDetailModal = false">关闭</n-button>
            <n-button 
              type="primary" 
              @click="handleSaveConfig" 
              :loading="saving"
              :disabled="!currentPlugin"
            >
              保存配置
            </n-button>
          </n-space>
        </div>
      </template>
    </n-modal>

    <!-- 确认删除对话框 -->
    <n-modal
      v-model:show="showDeleteModal"
      preset="dialog"
      title="确认删除"
      :mask-closable="false"
    >
      <div class="delete-content">
        <p>确定要删除以下插件吗？</p>
        <ul class="delete-list">
          <li v-for="plugin in pluginsToDelete" :key="plugin.id">
            {{ plugin.name }} (v{{ plugin.version }})
          </li>
        </ul>
        <p class="delete-warning">此操作不可恢复！</p>
      </div>

      <template #action>
        <n-space>
          <n-button @click="showDeleteModal = false">取消</n-button>
          <n-button type="error" @click="confirmDelete" :loading="deleting">
            确认删除
          </n-button>
        </n-space>
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
  NUpload,
  NUploadDragger,
  NAlert,
  NTabs,
  NTabPane
} from 'naive-ui'
import {
  AddOutline,
  SearchOutline,
  TrashOutline,
  PlayOutline,
  PauseOutline,
  EyeOutline,
  DownloadOutline,
  SettingsOutline,
  RefreshOutline,
  CloudUploadOutline,
  InformationCircleOutline
} from '@vicons/ionicons5'
import { api } from '@/api'

// 类型定义
interface Plugin {
  id: string
  name: string
  version: string
  author: string
  description: string
  type: string
  status: string
  config: string
  created_at: string
  updated_at: string
}

const message = useMessage()

// 响应式数据
const loading = ref(false)
const uploading = ref(false)
const saving = ref(false)
const testing = ref(false)
const validating = ref(false)
const deleting = ref(false)
const plugins = ref<Plugin[]>([])
const searchQuery = ref('')
const statusFilter = ref<string | null>(null)
const typeFilter = ref<string | null>(null)
const showUploadModal = ref(false)
const showDetailModal = ref(false)
const showDeleteModal = ref(false)
const currentPlugin = ref<Plugin | null>(null)
const fileList = ref<any[]>([])
const uploadError = ref('')
const testInput = ref('')
const testResult = ref<any>(null)
const configStatus = ref<'success' | 'error' | 'warning' | undefined>(undefined)
const configError = ref('')
const pluginsToDelete = ref<Plugin[]>([])

// 筛选选项
const statusOptions = [
  { label: '启用', value: 'active' },
  { label: '禁用', value: 'inactive' }
]

const typeOptions = [
  { label: '数据处理', value: 'data_processing' },
  { label: 'API集成', value: 'api_integration' },
  { label: '工具插件', value: 'tool' },
  { label: '分析插件', value: 'analytics' },
  { label: 'HTTP插件', value: 'http' },
  { label: 'Python插件', value: 'python' },
  { label: '工作流插件', value: 'workflow' }
]

// 分页配置
const pagination = ref({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100],
  onChange: (page: number) => {
    pagination.value.page = page
  },
  onUpdatePageSize: (pageSize: number) => {
    pagination.value.pageSize = pageSize
    pagination.value.page = 1
  }
})

// 计算属性
const hasActiveFilters = computed(() => {
  return searchQuery.value || statusFilter.value || typeFilter.value
})

const filteredPlugins = computed(() => {
  let filtered = plugins.value

  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(item =>
      item.name.toLowerCase().includes(query) ||
      item.description.toLowerCase().includes(query) ||
      item.author.toLowerCase().includes(query)
    )
  }

  // 状态筛选
  if (statusFilter.value) {
    filtered = filtered.filter(item => item.status === statusFilter.value)
  }

  // 类型筛选
  if (typeFilter.value) {
    filtered = filtered.filter(item => item.type === typeFilter.value)
  }

  return filtered
})

// 表格列配置
const columns = [
  {
    title: '插件信息',
    key: 'info',
    width: 300,
    fixed: 'left' as const,
    render: (row: Plugin) => {
      return h('div', { class: 'plugin-info' }, [
        h('div', { class: 'plugin-name' }, [
          h('span', { class: 'name' }, row.name),
          h('span', { class: 'version' }, `v${row.version}`)
        ]),
        h('div', { class: 'plugin-meta' }, [
          h('span', { class: 'author' }, `作者: ${row.author}`),
          h('span', { class: 'description' }, row.description)
        ])
      ])
    }
  },
  {
    title: '类型',
    key: 'type',
    width: 120,
    render: (row: Plugin) => {
      return h(NTag, { 
        type: getTypeTagType(row.type),
        size: 'small'
      }, { default: () => getTypeLabel(row.type) })
    }
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row: Plugin) => {
      return h(NTag, {
        type: row.status === 'active' ? 'success' : 'error',
        size: 'small'
      }, { default: () => row.status === 'active' ? '启用' : '禁用' })
    }
  },
  {
    title: '更新时间',
    key: 'updated_at',
    width: 180,
    render: (row: Plugin) => {
      return formatDateTime(row.updated_at)
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 300,
    fixed: 'right' as const,
    render: (row: Plugin) => {
      return h(NSpace, { size: 'small' }, {
        default: () => [
          h(NButton, {
            size: 'small',
            onClick: () => handleView(row)
          }, { default: () => '详情' }),
          h(NButton, {
            size: 'small',
            type: row.status === 'active' ? 'warning' : 'success',
            onClick: () => handleToggleStatus(row)
          }, { default: () => row.status === 'active' ? '禁用' : '启用' }),
          h(NButton, {
            size: 'small',
            type: 'info',
            onClick: () => handleTest(row)
          }, { default: () => '测试' }),
          h(NPopconfirm, {
            onPositiveClick: () => handleDelete([row])
          }, {
            trigger: () => h(NButton, {
              size: 'small',
              type: 'error'
            }, { default: () => '删除' }),
            default: () => '确定要删除这个插件吗？'
          })
        ]
      })
    }
  }
]

// 工具函数
const getTypeLabel = (type: string): string => {
  const typeMap: Record<string, string> = {
    data_processing: '数据处理',
    api_integration: 'API集成',
    tool: '工具插件',
    analytics: '分析插件',
    http: 'HTTP插件',
    python: 'Python插件',
    workflow: '工作流插件'
  }
  return typeMap[type] || type
}

const getTypeTagType = (type: string): 'primary' | 'success' | 'warning' | 'error' | 'info' => {
  const typeColorMap: Record<string, 'primary' | 'success' | 'warning' | 'error' | 'info'> = {
    data_processing: 'primary',
    api_integration: 'success',
    tool: 'warning',
    analytics: 'info',
    http: 'primary',
    python: 'success',
    workflow: 'warning'
  }
  return typeColorMap[type] || 'primary'
}

const formatDateTime = (dateString: string): string => {
  try {
    return new Date(dateString).toLocaleString('zh-CN')
  } catch {
    return dateString
  }
}

// API调用函数
const fetchPlugins = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (statusFilter.value) params.status = statusFilter.value
    if (typeFilter.value) params.type = typeFilter.value
    
    const response = await api.plugins.list(params)
    if (response.data?.success) {
      plugins.value = response.data.data?.data || []
    } else {
      throw new Error(response.data?.message || '获取插件列表失败')
    }
  } catch (error: any) {
    console.error('获取插件列表失败:', error)
    message.error(error.response?.data?.message || '获取插件列表失败')
    // 使用模拟数据
    plugins.value = [
      {
        id: '1',
        name: '数据分析插件',
        version: '1.0.0',
        author: 'AI Team',
        description: '提供数据分析和可视化功能',
        type: 'analytics',
        status: 'active',
        config: '{"max_data_points": 1000}',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: '2',
        name: 'API集成插件',
        version: '2.1.0',
        author: 'Integration Team',
        description: '支持多种API集成',
        type: 'api_integration',
        status: 'active',
        config: '{"timeout": 30}',
        created_at: new Date(Date.now() - 86400000).toISOString(),
        updated_at: new Date(Date.now() - 86400000).toISOString()
      },
      {
        id: '3',
        name: '数据处理工具',
        version: '1.5.2',
        author: 'Data Team',
        description: '高效的数据处理工具',
        type: 'data_processing',
        status: 'inactive',
        config: '{"batch_size": 100}',
        created_at: new Date(Date.now() - 172800000).toISOString(),
        updated_at: new Date(Date.now() - 172800000).toISOString()
      }
    ]
  } finally {
    loading.value = false
  }
}

// 事件处理函数
const handlePageChange = (page: number) => {
  pagination.value.page = page
}

const handlePageSizeChange = (pageSize: number) => {
  pagination.value.pageSize = pageSize
  pagination.value.page = 1
}

const handleSearch = () => {
  pagination.value.page = 1
  fetchPlugins()
}

const handleFilterChange = () => {
  pagination.value.page = 1
  fetchPlugins()
}

const clearFilters = () => {
  searchQuery.value = ''
  statusFilter.value = null
  typeFilter.value = null
  pagination.value.page = 1
  fetchPlugins()
}

const refreshPlugins = () => {
  fetchPlugins()
}

const handleView = (item: Plugin) => {
  currentPlugin.value = { ...item }
  showDetailModal.value = true
}

const handleToggleStatus = async (item: Plugin) => {
  try {
    await api.plugins.toggleStatus(item.id)
    message.success(item.status === 'active' ? '插件已禁用' : '插件已启用')
    await fetchPlugins()
  } catch (error: any) {
    console.error('切换插件状态失败:', error)
    message.error(error.response?.data?.message || '操作失败')
  }
}

const handleTest = async (item: Plugin) => {
  try {
    const response = await api.plugins.test(item.id, {})
    if (response.data?.success) {
      message.success('插件测试成功')
    } else {
      throw new Error(response.data?.message || '插件测试失败')
    }
  } catch (error: any) {
    console.error('插件测试失败:', error)
    message.error(error.response?.data?.message || '插件测试失败')
  }
}

const handleDelete = (items: Plugin[]) => {
  pluginsToDelete.value = items
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  if (pluginsToDelete.value.length === 0) return
  
  deleting.value = true
  try {
    const ids = pluginsToDelete.value.map(p => p.id)
    await api.plugins.batchDelete(ids)
    message.success('插件删除成功')
    showDeleteModal.value = false
    await fetchPlugins()
  } catch (error: any) {
    console.error('删除插件失败:', error)
    message.error(error.response?.data?.message || '删除失败')
  } finally {
    deleting.value = false
  }
}

const handleFileChange = (options: any) => {
  const { fileList: newFileList } = options
  fileList.value = newFileList
  uploadError.value = ''
}

const handleUpload = async (options: any) => {
  const { file } = options
  uploading.value = true
  uploadError.value = ''
  
  try {
    const response = await api.plugins.upload(file.file)
    if (response.data?.success) {
      message.success('插件上传成功')
      showUploadModal.value = false
      await fetchPlugins()
    } else {
      throw new Error(response.data?.message || '上传失败')
    }
  } catch (error: any) {
    console.error('上传插件失败:', error)
    uploadError.value = error.response?.data?.message || '上传失败'
    message.error(uploadError.value)
  } finally {
    uploading.value = false
  }
}

const handleUploadSubmit = async () => {
  if (fileList.value.length === 0) {
    message.warning('请选择插件文件')
    return
  }
  
  // 触发上传
  const uploadRef = document.querySelector('.n-upload') as any
  if (uploadRef && uploadRef.submit) {
    uploadRef.submit()
  }
}

const cancelUpload = () => {
  showUploadModal.value = false
  fileList.value = []
  uploadError.value = ''
}

const validateConfig = async () => {
  if (!currentPlugin.value) return
  
  validating.value = true
  configError.value = ''
  configStatus.value = undefined
  
  try {
    const config = currentPlugin.value.config
    if (!config) {
      configStatus.value = 'warning'
      configError.value = '配置为空'
      return
    }
    
    JSON.parse(config)
    configStatus.value = 'success'
    message.success('配置格式正确')
  } catch (error) {
    configStatus.value = 'error'
    configError.value = 'JSON格式错误: ' + (error as Error).message
  } finally {
    validating.value = false
  }
}

const testPlugin = async () => {
  if (!currentPlugin.value) return
  
  testing.value = true
  testResult.value = null
  
  try {
    let input = {}
    if (testInput.value) {
      try {
        input = JSON.parse(testInput.value)
      } catch (error) {
        message.error('测试输入格式错误')
        return
      }
    }
    
    const response = await api.plugins.test(currentPlugin.value.id, input)
    if (response.data?.success) {
      testResult.value = response.data.data
      message.success('插件测试成功')
    } else {
      throw new Error(response.data?.message || '插件测试失败')
    }
  } catch (error: any) {
    console.error('插件测试失败:', error)
    message.error(error.response?.data?.message || '插件测试失败')
  } finally {
    testing.value = false
  }
}

const clearTestResult = () => {
  testInput.value = ''
  testResult.value = null
}

const handleSaveConfig = async () => {
  if (!currentPlugin.value) return
  
  // 验证配置格式
  try {
    if (currentPlugin.value.config) {
      JSON.parse(currentPlugin.value.config)
    }
  } catch (error) {
    message.error('配置格式错误')
    return
  }
  
  saving.value = true
  try {
    await api.plugins.update(currentPlugin.value.id, {
      config: currentPlugin.value.config
    })
    message.success('配置保存成功')
    showDetailModal.value = false
    await fetchPlugins()
  } catch (error: any) {
    console.error('保存配置失败:', error)
    message.error(error.response?.data?.message || '保存失败')
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
  padding: 24px;
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
  font-size: 28px;
  font-weight: bold;
  margin: 0 0 8px 0;
  color: var(--n-text-color);
}

.page-description {
  margin: 0;
  color: var(--n-text-color-3);
  font-size: 14px;
}

.filter-card {
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
}

.filter-content {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 250px;
  max-width: 400px;
}

.filter-select {
  min-width: 150px;
}

.plugin-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.plugin-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.plugin-name .name {
  font-weight: 500;
  color: var(--n-text-color);
}

.plugin-name .version {
  font-size: 12px;
  color: var(--n-text-color-3);
  background: var(--n-border-color);
  padding: 2px 6px;
  border-radius: 4px;
}

.plugin-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: var(--n-text-color-3);
}

.plugin-meta .author {
  color: var(--n-text-color-2);
}

.plugin-meta .description {
  color: var(--n-text-color-3);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.upload-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.upload-tip {
  margin-bottom: 16px;
}

.upload-tip-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.upload-tip-content p {
  margin: 4px 0;
  font-size: 13px;
}

.upload-dragger {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 32px;
}

.upload-text {
  font-size: 16px;
  font-weight: 500;
  margin: 0;
  color: var(--n-text-color);
}

.upload-hint {
  font-size: 12px;
  margin: 0;
  color: var(--n-text-color-3);
}

.upload-error {
  margin-top: 16px;
}

.plugin-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid var(--n-border-color);
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item label {
  font-weight: 500;
  min-width: 100px;
  color: var(--n-text-color);
}

.detail-item span {
  flex: 1;
  color: var(--n-text-color-2);
}

.config-editor {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

.config-error {
  margin-top: 8px;
}

.test-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.test-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.test-input label {
  font-weight: 500;
  color: var(--n-text-color);
}

.test-actions {
  display: flex;
  gap: 12px;
}

.test-result {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.test-result label {
  font-weight: 500;
  color: var(--n-text-color);
}

.delete-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.delete-list {
  margin: 8px 0;
  padding-left: 20px;
}

.delete-list li {
  margin: 4px 0;
  color: var(--n-text-color-2);
}

.delete-warning {
  color: var(--n-error-color);
  font-weight: 500;
  margin: 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .plugins-page {
    padding: 16px;
    gap: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .filter-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input {
    max-width: none;
  }
  
  .detail-item {
    flex-direction: column;
    gap: 4px;
  }
  
  .detail-item label {
    min-width: auto;
  }
}
</style> 