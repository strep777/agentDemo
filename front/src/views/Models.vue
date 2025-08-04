<template>
  <div class="models-container p-6">
    <div class="page-header mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">模型管理</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2">管理和配置AI模型，支持Ollama和OpenAI</p>
    </div>

    <div class="actions mb-6">
      <n-space>
        <n-button type="primary" @click="showCreateModal = true">
          <template #icon>
            <n-icon><AddOutline /></n-icon>
          </template>
          添加模型
        </n-button>
        <n-button @click="refreshModels">
          <template #icon>
            <n-icon><RefreshOutline /></n-icon>
          </template>
          刷新
        </n-button>
        <n-button @click="openOllamaConfigModal">
          <template #icon>
            <n-icon><SettingsSharp /></n-icon>
          </template>
          Ollama配置
        </n-button>
        <n-button @click="checkOllamaHealth" :loading="checkingOllama">
          <template #icon>
            <n-icon><SettingsSharp /></n-icon>
          </template>
          检测Ollama
        </n-button>
      </n-space>
    </div>

    <!-- Ollama状态显示 -->
    <div v-if="ollamaHealth" class="ollama-status mb-6">
      <n-card title="Ollama服务器状态" class="mb-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <n-icon size="20" class="text-green-500 mr-2">
              <SettingsSharp />
            </n-icon>
            <span class="text-green-600">Ollama服务器连接正常</span>
          </div>
          <n-button size="small" @click="loadOllamaModels" :loading="loadingOllamaModels">
            刷新模型列表
          </n-button>
        </div>
        
        <div v-if="ollamaModels.length > 0" class="mt-4">
          <h4 class="text-sm font-medium mb-2">可用模型:</h4>
          <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
            <div v-for="model in ollamaModels" :key="model.name" 
                 class="p-2 border rounded text-xs flex items-center justify-between">
              <span>{{ model.name }}</span>
              <n-space>
                <n-button size="tiny" @click="selectOllamaModel(model.name)">
                  选择
                </n-button>
                <n-button size="tiny" @click="testOllamaModel(model.name)">
                  测试
                </n-button>
                <n-button size="tiny" @click="pullOllamaModel(model.name)">
                  拉取
                </n-button>
              </n-space>
            </div>
          </div>
        </div>
      </n-card>
    </div>

    <div class="models-list">
      <n-grid :cols="3" :x-gap="16" :y-gap="16">
        <n-grid-item v-for="model in models" :key="model.id">
          <n-card class="model-card" hoverable>
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center mb-2">
                  <n-icon size="20" class="mr-2">
                    <SettingsSharp />
                  </n-icon>
                  <h3 class="text-lg font-semibold">{{ model.name }}</h3>
                  <n-tag :type="getModelStatusType(model.status)" size="small" class="ml-2">
                    {{ model.status === 'available' ? '可用' : '不可用' }}
                  </n-tag>
                </div>
                
                <p class="text-gray-600 dark:text-gray-400 text-sm mb-3">{{ model.description }}</p>
                
                <div class="model-meta text-xs text-gray-500 mb-3">
                  <div>类型: {{ model.type }}</div>
                  <div>提供商: {{ model.provider }}</div>
                  <div>参数: {{ formatParameters(model.parameters) }}</div>
                </div>
              </div>
              
              <div class="model-actions ml-4">
                <n-space>
                  <n-button size="small" @click="editModel(model)">
                    <template #icon>
                      <n-icon><CreateOutline /></n-icon>
                    </template>
                    编辑
                  </n-button>
                  <n-button size="small" type="error" @click="deleteModel(model)">
                    <template #icon>
                      <n-icon><TrashOutline /></n-icon>
                    </template>
                    删除
                  </n-button>
                  <n-button size="small" @click="testModel(model)">
                    <template #icon>
                      <n-icon><PlayOutline /></n-icon>
                    </template>
                    测试
                  </n-button>
                </n-space>
              </div>
            </div>
          </n-card>
        </n-grid-item>
      </n-grid>
    </div>

    <n-modal v-model:show="showCreateModal" preset="card" :title="editingModel ? '编辑模型' : '添加模型'" style="width: 600px">
      <n-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-placement="left"
        label-width="auto"
      >
        <n-form-item label="模型名称" path="name">
          <n-input v-model:value="createForm.name" placeholder="输入模型名称" />
        </n-form-item>
        
        <n-form-item label="描述" path="description">
          <n-input
            v-model:value="createForm.description"
            type="textarea"
            placeholder="输入模型描述"
            :rows="3"
          />
        </n-form-item>
        
        <n-form-item label="模型类型" path="type">
          <n-select
            v-model:value="createForm.type"
            :options="modelTypeOptions"
            placeholder="选择模型类型"
          />
        </n-form-item>
        
        <n-form-item label="提供商" path="provider">
          <n-select
            v-model:value="createForm.provider"
            :options="providerOptions"
            placeholder="选择提供商"
          />
        </n-form-item>
        
        <n-form-item label="Ollama服务器地址" path="serverUrl">
          <n-input v-model:value="createForm.serverUrl" placeholder="http://localhost:11434" />
        </n-form-item>

        <n-form-item label="参数配置" path="parameters">
          <n-input
            v-model:value="createForm.parametersText"
            type="textarea"
            placeholder="输入JSON格式的参数配置"
            :rows="5"
          />
        </n-form-item>
      </n-form>
      
      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" @click="createModel" :loading="creating">
            {{ editingModel ? '更新' : '添加' }}
          </n-button>
        </n-space>
      </template>
    </n-modal>
    
    <!-- Ollama配置对话框 -->
    <n-modal v-model:show="showOllamaConfigModal" preset="dialog" title="Ollama服务器配置">
      <n-form :model="ollamaConfig" :rules="ollamaConfigRules" ref="ollamaConfigFormRef">
        <n-form-item label="服务器地址" path="serverUrl">
          <n-input v-model:value="ollamaConfig.serverUrl" placeholder="http://localhost:11434" />
        </n-form-item>
        <n-form-item label="连接测试">
          <n-space>
            <n-button @click="testOllamaConnection" :loading="testingConnection">
              测试连接
            </n-button>
            <n-button @click="loadOllamaModelsFromConfig" :loading="loadingOllamaModels">
              获取模型列表
            </n-button>
          </n-space>
        </n-form-item>
      </n-form>
      
      <template #footer>
        <n-space justify="end">
          <n-button @click="showOllamaConfigModal = false">取消</n-button>
          <n-button type="primary" @click="saveOllamaConfig">
            保存配置
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, h, watch } from 'vue'
import { api } from '@/api'
import type { Model } from '@/types'
import { useMessage, useDialog } from 'naive-ui'
import {
  NGrid,
  NGridItem,
  NCard,
  NButton,
  NSpace,
  NIcon,
  NTag,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  NDropdown
} from 'naive-ui'
import {
  AddOutline,
  RefreshOutline,
  EllipsisVerticalOutline,
  SettingsSharp,
  SettingsOutline,
  TrashOutline,
  DownloadOutline
} from '@vicons/ionicons5'

const message = useMessage()
const dialog = useDialog()

const models = ref<Model[]>([])
const loading = ref(false)
const creating = ref(false)
const showCreateModal = ref(false)
const showOllamaConfigModal = ref(false)
const testingConnection = ref(false)
const createFormRef = ref()
const ollamaConfigFormRef = ref()

// Ollama配置
const ollamaConfig = reactive({
  serverUrl: localStorage.getItem('ollama_server_url') || 'http://localhost:11434'
})

const ollamaConfigRules = {
  serverUrl: [
    { required: true, message: '请输入Ollama服务器地址', trigger: 'blur' },
    { pattern: /^https?:\/\/.+/, message: '请输入有效的URL地址', trigger: 'blur' }
  ]
}

// 监听ollamaConfig变化，同步到createForm
const syncOllamaConfig = () => {
  createForm.serverUrl = ollamaConfig.serverUrl
}

const createForm = reactive({
  name: '',
  description: '',
  type: 'llm',
  provider: 'ollama',
  parametersText: '{}',
  serverUrl: localStorage.getItem('ollama_server_url') || 'http://localhost:11434'
})

// 初始化时同步配置
syncOllamaConfig()

const createRules = {
  name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入模型描述', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择模型类型', trigger: 'change' }
  ],
  provider: [
    { required: true, message: '请选择提供商', trigger: 'change' }
  ],
  serverUrl: [
    { required: true, message: '请输入Ollama服务器地址', trigger: 'blur' }
  ]
}

const modelTypeOptions = [
  { label: '大语言模型', value: 'llm' },
  { label: '嵌入模型', value: 'embedding' }
]

const providerOptions = [
  { label: 'Ollama', value: 'ollama' },
  { label: 'OpenAI', value: 'openai' },
  { label: '本地模型', value: 'local' }
]

const getModelStatusType = (status: string) => {
  return status === 'available' ? 'success' : 'warning'
}

const getModelActions = (model: Model) => {
  return [
    {
      label: '编辑',
      key: 'edit',
      icon: () => h(SettingsOutline)
    },
    {
      label: '下载',
      key: 'download',
      icon: () => h(DownloadOutline)
    },
    {
      label: '删除',
      key: 'delete',
      icon: () => h(TrashOutline)
    }
  ]
}

const handleModelAction = async (key: string, model: any) => {
  switch (key) {
    case 'edit':
      // TODO: 实现编辑功能
      break
    case 'download':
      await downloadModel(model)
      break
    case 'delete':
      await deleteModel(model)
      break
  }
}

// Ollama相关功能
const ollamaHealth = ref(false)
const ollamaModels = ref<any[]>([])
const checkingOllama = ref(false)
const loadingOllamaModels = ref(false)
const editingModel = ref<Model | null>(null)

// Ollama配置管理
const testOllamaConnection = async () => {
  try {
    testingConnection.value = true
    const response = await api.models.checkOllamaHealth(ollamaConfig.serverUrl)
    if (response.data.success && response.data.data.healthy) {
      message.success('Ollama服务器连接成功')
      ollamaHealth.value = true
    } else {
      message.error('Ollama服务器连接失败')
      ollamaHealth.value = false
    }
  } catch (error: any) {
    message.error(error.response?.data?.message || 'Ollama服务器连接失败')
    ollamaHealth.value = false
  } finally {
    testingConnection.value = false
  }
}

const loadOllamaModelsFromConfig = async () => {
  try {
    loadingOllamaModels.value = true
    const response = await api.models.getOllamaModels(ollamaConfig.serverUrl)
    if (response.data.success) {
      ollamaModels.value = response.data.data
      message.success(`发现 ${ollamaModels.value.length} 个可用模型`)
    } else {
      message.error(response.data.message || '获取Ollama模型列表失败')
    }
  } catch (error: any) {
    message.error(error.response?.data?.message || '获取Ollama模型列表失败')
  } finally {
    loadingOllamaModels.value = false
  }
}

const saveOllamaConfig = () => {
  ollamaConfigFormRef.value?.validate(async (errors: any) => {
    if (!errors) {
      localStorage.setItem('ollama_server_url', ollamaConfig.serverUrl)
      // 同步到createForm
      createForm.serverUrl = ollamaConfig.serverUrl
      message.success('Ollama配置已保存')
      showOllamaConfigModal.value = false
    } else {
      message.error('请检查Ollama服务器地址格式')
    }
  })
}

// 监听ollamaConfig.serverUrl变化
const watchOllamaConfig = () => {
  if (ollamaConfig.serverUrl !== createForm.serverUrl) {
    createForm.serverUrl = ollamaConfig.serverUrl
  }
}

// 在配置对话框打开时同步
const openOllamaConfigModal = () => {
  ollamaConfig.serverUrl = localStorage.getItem('ollama_server_url') || 'http://localhost:11434'
  showOllamaConfigModal.value = true
}

const checkOllamaHealth = async () => {
  try {
    checkingOllama.value = true
    const response = await api.models.checkOllamaHealth(createForm.serverUrl)
    if (response.data.success) {
      ollamaHealth.value = response.data.data.healthy
      if (ollamaHealth.value) {
        message.success('Ollama服务器连接成功')
        await loadOllamaModels()
      } else {
        message.error('Ollama服务器连接失败')
      }
    } else {
      message.error(response.data.message || '检查Ollama服务器状态失败')
    }
  } catch (error: any) {
    message.error(error.response?.data?.message || '检查Ollama服务器状态失败')
    ollamaHealth.value = false
  } finally {
    checkingOllama.value = false
  }
}

const loadOllamaModels = async () => {
  try {
    loadingOllamaModels.value = true
    const response = await api.models.getOllamaModels(createForm.serverUrl)
    if (response.data.success) {
      ollamaModels.value = response.data.data
      message.success(`发现 ${ollamaModels.value.length} 个可用模型`)
    } else {
      message.error(response.data.message || '获取Ollama模型列表失败')
    }
  } catch (error: any) {
    message.error(error.response?.data?.message || '获取Ollama模型列表失败')
  } finally {
    loadingOllamaModels.value = false
  }
}

const pullOllamaModel = async (modelName: string) => {
  try {
    const response = await api.models.pullOllamaModel(modelName, createForm.serverUrl)
    if (response.data.success) {
      message.success(`模型 ${modelName} 拉取成功`)
      await loadOllamaModels()
    } else {
      message.error(response.data.message || '模型拉取失败')
    }
  } catch (error: any) {
    message.error(error.response?.data?.message || '模型拉取失败')
  }
}

const testOllamaModel = async (modelName: string) => {
  try {
    const response = await api.models.testOllamaModel(modelName, 'Hello, how are you?', createForm.serverUrl)
    message.success('测试成功')
  } catch (error) {
    message.error('测试失败')
  }
}

const downloadModel = async (model: Model) => {
  try {
    const response = await api.models.get(model.id)
    if (response.data.success) {
      message.success('模型下载成功')
    } else {
      message.error(response.data.message || '下载失败')
    }
  } catch (error: any) {
    message.error(error.response?.data?.message || '下载失败')
  }
}

const editModel = async (model: Model) => {
  try {
    // 填充编辑表单
    createForm.name = model.name
    createForm.description = model.description || ''
    createForm.type = model.type || 'llm'
    createForm.provider = model.provider
    createForm.serverUrl = 'http://localhost:11434' // 默认Ollama地址
    createForm.parametersText = JSON.stringify(model.parameters || {}, null, 2)
    
    // 标记为编辑模式
    editingModel.value = model
    showCreateModal.value = true
  } catch (error: any) {
    message.error('编辑模型失败')
  }
}

const testModel = async (model: Model) => {
  try {
    const testMessage = 'Hello, how are you?'
    const response = await api.models.test(model.id, { message: testMessage })
    
    if (response.data.success) {
      const result = response.data.data
      if (result.success) {
        message.success(`模型测试成功: ${result.response}`)
      } else {
        message.error(`模型测试失败: ${result.error}`)
      }
    } else {
      message.error(response.data.message || '测试失败')
    }
  } catch (error: any) {
    message.error(error.response?.data?.message || '测试失败')
  }
}

const deleteModel = async (model: Model) => {
  try {
    const response = await api.models.delete(model.id)
    if (response.data.success) {
      message.success('模型删除成功')
      await loadModels()
    } else {
      message.error(response.data.message || '删除失败')
    }
  } catch (error: any) {
    message.error(error.response?.data?.message || '删除失败')
  }
}

const createModel = async () => {
  createFormRef.value?.validate(async (errors: any) => {
    if (!errors) {
      try {
        creating.value = true
        
        const modelData = {
          name: createForm.name,
          description: createForm.description,
          type: createForm.type,
          provider: createForm.provider,
          server_url: createForm.serverUrl,
          parameters: JSON.parse(createForm.parametersText)
        }
        
        let response
        if (editingModel.value) {
          // 编辑模式
          response = await api.models.update(editingModel.value.id, modelData)
          if (response.data.success) {
            message.success('模型更新成功')
          }
        } else {
          // 创建模式
          response = await api.models.create(modelData)
          if (response.data.success) {
            message.success('模型创建成功')
          }
        }
        
        if (response.data.success) {
          showCreateModal.value = false
          await loadModels()
          // 重置表单和编辑状态
          createForm.name = ''
          createForm.description = ''
          createForm.type = 'llm'
          createForm.provider = 'ollama'
          createForm.parametersText = '{}'
          createForm.serverUrl = localStorage.getItem('ollama_server_url') || 'http://localhost:11434'
          editingModel.value = null
        } else {
          message.error(response.data.message || (editingModel.value ? '更新失败' : '创建失败'))
        }
      } catch (error: any) {
        message.error(error.response?.data?.message || (editingModel.value ? '更新失败' : '创建失败'))
      } finally {
        creating.value = false
      }
    } else {
      message.error('请检查模型信息')
    }
  })
}

const loadModels = async () => {
  try {
    loading.value = true
    console.log('🔍 开始加载模型列表...')
    const response = await api.models.list()
    console.log('📊 模型列表响应:', response)
    if (response.data.success) {
      // 修复：正确访问嵌套的data字段
      models.value = response.data.data.data || response.data.data
      console.log('✅ 模型列表加载成功，共', models.value.length, '个模型')
    }
  } catch (error) {
    console.error('❌ 加载模型列表失败:', error)
    message.error('加载模型列表失败')
  } finally {
    loading.value = false
  }
}

const refreshModels = () => {
  loadModels()
}

const formatParameters = (parameters: Record<string, any> | undefined) => {
  if (!parameters || Object.keys(parameters).length === 0) {
    return '无'
  }
  return Object.entries(parameters)
    .map(([key, value]) => `${key}: ${value}`)
    .join(', ')
}

const selectOllamaModel = (modelName: string) => {
  // 将选中的模型名称设置到 createForm 中
  createForm.name = modelName
  createForm.description = `Ollama模型: ${modelName}`
  createForm.provider = 'ollama'
  createForm.type = 'llm'
  createForm.serverUrl = ollamaConfig.serverUrl
  message.success(`已选择 Ollama 模型: ${modelName}`)
  // 自动打开创建模型对话框
  showCreateModal.value = true
}

onMounted(() => {
  // 调试信息
  console.log('🔧 检查localStorage中的token:', localStorage.getItem('token'))
  console.log('🔧 开发环境:', import.meta.env.DEV)
  
  loadModels()
  // 监听ollamaConfig变化
  watch(() => ollamaConfig.serverUrl, (newUrl) => {
    if (newUrl !== createForm.serverUrl) {
      createForm.serverUrl = newUrl
    }
  })
})
</script>

<style scoped>
.models-container {
  min-height: 100vh;
}

.model-card {
  transition: all 0.3s ease;
}

.model-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style> 