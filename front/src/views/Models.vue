<template>
  <!-- 模型管理页面主容器 -->
  <div class="models-container p-6">
    <!-- 页面头部 -->
    <div class="page-header mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">模型管理</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2">管理和配置AI模型，支持Ollama和OpenAI</p>
    </div>

    <!-- 操作按钮区域 -->
    <div class="actions mb-6">
      <n-space>
        <!-- 添加模型按钮 -->
        <n-button type="primary" @click="showCreateModal = true">
          <template #icon>
            <n-icon><AddOutline /></n-icon>
          </template>
          添加模型
        </n-button>
        <!-- 刷新按钮 -->
        <n-button @click="refreshModels" :loading="loading">
          <template #icon>
            <n-icon><RefreshOutline /></n-icon>
          </template>
          刷新
        </n-button>
        <!-- 快速连接Ollama按钮 -->
        <n-button @click="quickConnectOllama" :loading="checkingOllama" type="success" ghost>
          <template #icon>
            <n-icon><SettingsSharp /></n-icon>
          </template>
          快速连接Ollama
        </n-button>
        <!-- Ollama配置按钮 -->
        <n-button @click="openOllamaConfigModal">
          <template #icon>
            <n-icon><SettingsSharp /></n-icon>
          </template>
          Ollama配置
        </n-button>
        <!-- 检测Ollama按钮 -->
        <n-button @click="checkOllamaHealth" :loading="checkingOllama">
          <template #icon>
            <n-icon><SettingsSharp /></n-icon>
          </template>
          检测Ollama
        </n-button>
        <!-- 查看配置按钮 -->
        <n-button @click="showCurrentOllamaConfig" size="small" ghost>
          <template #icon>
            <n-icon><SettingsSharp /></n-icon>
          </template>
          查看配置
        </n-button>
      </n-space>
    </div>

    <!-- 模型列表展示区域 -->
    <div class="models-list">
      <!-- 使用网格布局展示模型卡片 -->
      <n-grid 
        :cols="24" 
        :x-gap="16" 
        :y-gap="16" 
        responsive="screen"
        :collapsed="false"
        :collapsed-rows="1"
      >
        <!-- 模型卡片 -->
        <n-grid-item 
          :span="24" 
          :md="12" 
          :lg="8" 
          :xl="6"
          v-for="model in models" 
          :key="model.id"
        >
          <n-card class="model-card" hoverable>
            <div class="model-card-content">
              <!-- 模型头部信息 -->
              <div class="model-header mb-4">
                <div class="flex items-center justify-between mb-2">
                  <div class="flex items-center">
                    <n-icon size="24" class="mr-3 text-blue-500">
                      <SettingsSharp />
                    </n-icon>
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{{ model.name }}</h3>
                  </div>
                  <!-- 模型状态标签 -->
                  <n-tag :type="getModelStatusType(model.status)" size="small">
                    {{ getModelStatusText(model.status) }}
                  </n-tag>
                </div>
                
                <p class="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">{{ model.description }}</p>
              </div>
              
              <!-- 模型元信息 -->
              <div class="model-meta mb-4">
                <div class="grid grid-cols-1 gap-2 text-xs text-gray-500 dark:text-gray-400">
                  <div class="flex items-center">
                    <span class="font-medium mr-2">类型:</span>
                    <span>{{ getModelTypeText(model.type) }}</span>
                  </div>
                  <div class="flex items-center">
                    <span class="font-medium mr-2">提供商:</span>
                    <span>{{ getProviderText(model.provider) }}</span>
                  </div>
                  <div class="flex items-start">
                    <span class="font-medium mr-2">参数:</span>
                    <span class="flex-1 break-all">{{ formatParameters(model.parameters) }}</span>
                  </div>
                  <div v-if="model.server_url" class="flex items-center">
                    <span class="font-medium mr-2">服务器:</span>
                    <span class="text-xs">{{ model.server_url }}</span>
                  </div>
                </div>
              </div>
              
              <!-- 操作按钮 -->
              <div class="model-actions">
                <n-space justify="space-between" align="center">
                  <n-space>
                    <!-- 编辑按钮 -->
                    <n-button size="small" @click="editModel(model)" type="primary" ghost>
                      <template #icon>
                        <n-icon><CreateOutline /></n-icon>
                      </template>
                      编辑
                    </n-button>
                    <!-- 测试按钮 -->
                    <n-button size="small" @click="testModel(model)" type="info" ghost>
                      <template #icon>
                        <n-icon><PlayOutline /></n-icon>
                      </template>
                      测试
                    </n-button>
                  </n-space>
                  <!-- 删除按钮 -->
                  <n-button size="small" type="error" ghost @click="deleteModel(model)">
                    <template #icon>
                      <n-icon><TrashOutline /></n-icon>
                    </template>
                    删除
                  </n-button>
                </n-space>
              </div>
            </div>
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- 空状态显示 -->
      <div v-if="models.length === 0 && !loading" class="empty-state text-center py-12">
        <n-icon size="64" class="text-gray-400 mb-4">
          <SettingsSharp />
        </n-icon>
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">暂无模型</h3>
        <p class="text-gray-500 mb-4">开始添加您的第一个AI模型</p>
        <n-button type="primary" @click="showCreateModal = true">
          添加模型
        </n-button>
      </div>

      <!-- 加载状态显示 -->
      <div v-if="loading" class="loading-state text-center py-12">
        <n-spin size="large">
          <template #description>
            <span class="text-gray-500">加载模型中...</span>
          </template>
        </n-spin>
      </div>
    </div>

    <!-- 创建/编辑模型对话框 -->
    <n-modal 
      v-model:show="showCreateModal" 
      preset="card" 
      :title="editingModel ? '编辑模型' : '添加模型'" 
      style="width: 600px; max-width: 90vw;"
    >
      <n-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-placement="left"
        label-width="auto"
      >
        <!-- 提供商选择 -->
        <n-form-item label="提供商" path="provider">
          <n-select
            v-model:value="createForm.provider"
            :options="providerOptions"
            placeholder="选择提供商"
            @update:value="handleProviderChange"
          />
        </n-form-item>
        
        <!-- Ollama服务器配置 -->
        <n-form-item v-if="createForm.provider === 'ollama'" label="Ollama服务器" path="serverUrl">
          <n-input 
            v-model:value="createForm.serverUrl" 
            placeholder="http://localhost:11434"
            :disabled="!canEditServerUrl"
          >
            <template #suffix>
              <n-button 
                size="small" 
                @click="testOllamaConnection" 
                :loading="testingConnection"
                type="primary"
                ghost
              >
                测试连接
              </n-button>
            </template>
          </n-input>
        </n-form-item>
        
        <!-- 模型名称选择 -->
        <n-form-item label="模型名称" path="name">
          <!-- 当选择Ollama且有可用模型时，显示下拉选择框 -->
          <n-select
            v-if="createForm.provider === 'ollama' && availableOllamaModels.length > 0"
            v-model:value="createForm.name"
            :options="availableOllamaModels"
            placeholder="从Ollama可用模型中选择"
            filterable
            :loading="loadingOllamaModels"
            @update:value="handleModelNameChange"
          />
          <!-- 否则显示普通输入框 -->
          <n-input
            v-else
            v-model:value="createForm.name"
            :placeholder="createForm.provider === 'ollama' ? '请输入模型名称' : '输入模型名称'"
          />
        </n-form-item>
        
        <!-- 模型描述 -->
        <n-form-item label="描述" path="description">
          <n-input
            v-model:value="createForm.description"
            type="textarea"
            placeholder="输入模型描述"
            :rows="3"
          />
        </n-form-item>
        
        <!-- 模型类型 -->
        <n-form-item label="模型类型" path="type">
          <n-select
            v-model:value="createForm.type"
            :options="modelTypeOptions"
            placeholder="选择模型类型"
          />
        </n-form-item>

        <!-- 参数配置 -->
        <n-form-item label="参数配置" path="parameters">
          <n-input
            v-model:value="createForm.parametersText"
            type="textarea"
            placeholder="输入JSON格式的参数配置"
            :rows="5"
          />
        </n-form-item>
      </n-form>
      
      <!-- 对话框底部按钮 -->
      <template #footer>
        <n-space justify="end">
          <n-button @click="cancelCreate">取消</n-button>
          <n-button type="primary" @click="createModel" :loading="creating">
            {{ editingModel ? '更新' : '添加' }}
          </n-button>
        </n-space>
      </template>
    </n-modal>
    
    <!-- Ollama配置对话框 -->
    <n-modal 
      v-model:show="showOllamaConfigModal" 
      preset="dialog" 
      title="Ollama服务器配置"
      style="width: 500px; max-width: 90vw;"
    >
      <n-form :model="ollamaConfig" :rules="ollamaConfigRules" ref="ollamaConfigFormRef">
        <n-form-item label="服务器地址" path="serverUrl">
          <n-input v-model:value="ollamaConfig.serverUrl" placeholder="http://localhost:11434" />
        </n-form-item>
        <n-form-item label="连接测试">
          <n-space>
            <n-button @click="testOllamaConnection" :loading="testingConnection">
              测试连接
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
// 导入Vue相关功能
import { ref, reactive, onMounted, watch } from 'vue'
// 导入API接口
import { api } from '@/api'
// 导入类型定义
import type { Model } from '@/types'
// 导入Naive UI组件
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
  NSpin
} from 'naive-ui'
// 导入图标
import {
  AddOutline,
  RefreshOutline,
  SettingsSharp,
  TrashOutline,
  CreateOutline,
  PlayOutline
} from '@vicons/ionicons5'

// 获取消息和对话框实例
const message = useMessage()
const dialog = useDialog()

// ==================== 响应式数据定义 ====================

// 模型列表数据
const models = ref<Model[]>([])
// 加载状态
const loading = ref(false)
// 创建/更新状态
const creating = ref(false)
// 显示创建对话框
const showCreateModal = ref(false)
// 显示Ollama配置对话框
const showOllamaConfigModal = ref(false)
// 测试连接状态
const testingConnection = ref(false)
// 表单引用
const createFormRef = ref()
const ollamaConfigFormRef = ref()

// Ollama相关状态
const availableOllamaModels = ref<Array<{ label: string; value: string }>>([])
const loadingOllamaModels = ref(false)
const canEditServerUrl = ref(true)

// Ollama配置对象
const ollamaConfig = reactive({
  serverUrl: localStorage.getItem('ollama_server_url') || 'http://localhost:11434'
})

// Ollama配置验证规则
const ollamaConfigRules = {
  serverUrl: [
    { required: true, message: '请输入Ollama服务器地址', trigger: 'blur' },
    { pattern: /^https?:\/\/.+/, message: '请输入有效的URL地址', trigger: 'blur' }
  ]
}

// 创建表单数据
const createForm = reactive({
  name: '',                    // 模型名称
  description: '',             // 模型描述
  type: 'llm',                // 模型类型
  provider: 'ollama',         // 提供商
  parametersText: '{}',       // 参数字符串
  serverUrl: localStorage.getItem('ollama_server_url') || 'http://localhost:11434'  // 服务器地址
})

// 表单验证规则
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
    { required: true, message: '请输入服务器地址', trigger: 'blur' }
  ]
}

// 模型类型选项
const modelTypeOptions = [
  { label: '大语言模型', value: 'llm' },
  { label: '嵌入模型', value: 'embedding' },
  { label: '图像模型', value: 'image' },
  { label: '语音模型', value: 'speech' }
]

// 提供商选项
const providerOptions = [
  { label: 'Ollama', value: 'ollama' },
  { label: 'OpenAI', value: 'openai' },
  { label: '本地模型', value: 'local' },
  { label: 'Hugging Face', value: 'huggingface' }
]

// Ollama相关状态
const ollamaHealth = ref(false)
const checkingOllama = ref(false)
const editingModel = ref<Model | null>(null)

// ==================== 工具函数 ====================

/**
 * 获取模型状态对应的标签类型
 * @param status 模型状态
 * @returns 标签类型
 */
const getModelStatusType = (status: string) => {
  switch (status) {
    case 'active':
    case 'available':
      return 'success'
    case 'inactive':
    case 'unavailable':
      return 'error'
    case 'downloading':
      return 'warning'
    default:
      return 'default'
  }
}

/**
 * 获取模型状态对应的显示文本
 * @param status 模型状态
 * @returns 显示文本
 */
const getModelStatusText = (status: string) => {
  switch (status) {
    case 'active':
    case 'available':
      return '可用'
    case 'inactive':
    case 'unavailable':
      return '不可用'
    case 'downloading':
      return '下载中'
    default:
      return status
  }
}

/**
 * 获取模型类型对应的显示文本
 * @param type 模型类型
 * @returns 显示文本
 */
const getModelTypeText = (type: string) => {
  switch (type) {
    case 'llm':
      return '大语言模型'
    case 'embedding':
      return '嵌入模型'
    case 'image':
      return '图像模型'
    case 'speech':
      return '语音模型'
    default:
      return type
  }
}

/**
 * 获取提供商对应的显示文本
 * @param provider 提供商
 * @returns 显示文本
 */
const getProviderText = (provider: string) => {
  switch (provider) {
    case 'ollama':
      return 'Ollama'
    case 'openai':
      return 'OpenAI'
    case 'local':
      return '本地模型'
    case 'huggingface':
      return 'Hugging Face'
    default:
      return provider
  }
}

/**
 * 格式化模型参数显示
 * @param parameters 参数对象
 * @returns 格式化后的参数字符串
 */
const formatParameters = (parameters: Record<string, any> | undefined) => {
  if (!parameters || Object.keys(parameters).length === 0) {
    return '无'
  }
  return Object.entries(parameters)
    .map(([key, value]) => `${key}: ${value}`)
    .join(', ')
}

// ==================== Ollama相关功能 ====================

/**
 * 加载Ollama可用模型
 */
const loadOllamaModels = async () => {
  try {
    loadingOllamaModels.value = true
    console.log('🔍 开始加载Ollama模型...')
    
    const serverUrl = createForm.serverUrl || ollamaConfig.serverUrl
    console.log('📋 使用服务器地址:', serverUrl)
    
    const response = await api.models.getOllamaModels(serverUrl)
    
    console.log('📊 API响应:', response)
    
    if (response.data.success) {
      const ollamaModels = response.data.data || []
      console.log('📋 原始模型数据:', ollamaModels)
      
      availableOllamaModels.value = ollamaModels.map((model: string) => ({
        label: model,
        value: model
      }))
      console.log('✅ Ollama模型加载成功，共', availableOllamaModels.value.length, '个模型')
      
      if (availableOllamaModels.value.length === 0) {
        message.warning('未发现可用的Ollama模型，请确保Ollama服务器正在运行并已安装模型')
      }
    } else {
      console.error('❌ 加载Ollama模型失败:', response.data.message)
      message.error(response.data.message || '加载Ollama模型失败')
      availableOllamaModels.value = []
    }
  } catch (error: any) {
    console.error('❌ 加载Ollama模型失败:', error)
    console.error('❌ 错误详情:', error.response?.data)
    message.error('加载Ollama模型失败，请检查Ollama服务器连接')
    availableOllamaModels.value = []
  } finally {
    loadingOllamaModels.value = false
  }
}

/**
 * 测试Ollama连接
 */
const testOllamaConnection = async () => {
  try {
    checkingOllama.value = true
    console.log('🔍 开始测试Ollama连接...')
    
    const serverUrl = createForm.serverUrl || ollamaConfig.serverUrl
    console.log('📋 使用服务器地址:', serverUrl)
    
    const response = await api.models.checkOllamaHealth(serverUrl)
    
    console.log('📊 健康检查响应:', response)
    
    if (response.data.success && response.data.data.healthy) {
      message.success('Ollama服务器连接成功')
      ollamaHealth.value = true
      
      // 连接成功后加载可用模型
      await loadOllamaModels()
      
      if (availableOllamaModels.value.length > 0) {
        message.success(`发现 ${availableOllamaModels.value.length} 个可用模型`)
        console.log('📋 可用模型列表:', availableOllamaModels.value.map(m => m.label))
      } else {
        message.warning('未发现可用模型，请确保Ollama已安装模型')
      }
    } else {
      message.error('Ollama服务器连接失败')
      ollamaHealth.value = false
      availableOllamaModels.value = []
    }
  } catch (error: any) {
    console.error('❌ 测试Ollama连接失败:', error)
    console.error('❌ 错误详情:', error.response?.data)
    message.error('Ollama服务器连接失败，请检查服务器地址和网络连接')
    ollamaHealth.value = false
    availableOllamaModels.value = []
  } finally {
    checkingOllama.value = false
  }
}

/**
 * 处理模型名称变化
 * @param modelName 选择的模型名称
 */
const handleModelNameChange = (modelName: string) => {
  console.log('🔄 模型名称变化:', modelName)
  if (modelName) {
    // 如果选择了Ollama模型，自动设置描述
    const selectedModel = availableOllamaModels.value.find(m => m.value === modelName)
    if (selectedModel && !createForm.description) {
      createForm.description = `${selectedModel.label} 模型`
    }
    
    // 自动设置默认参数
    if (createForm.provider === 'ollama' && createForm.parametersText === '{}') {
      createForm.parametersText = JSON.stringify({
        temperature: 0.7,
        max_tokens: 1000,
        top_p: 1.0,
        frequency_penalty: 0.0,
        presence_penalty: 0.0
      }, null, 2)
    }
  }
}

/**
 * 处理提供商变化
 * @param provider 选择的提供商
 */
const handleProviderChange = async (provider: string) => {
  console.log('🔄 提供商变化:', provider)
  
  // 清空当前选择
  createForm.name = ''
  createForm.description = ''
  availableOllamaModels.value = []
  
  if (provider === 'ollama') {
    // 当选择Ollama时，自动测试连接并加载可用模型
    message.info('正在连接Ollama服务器...')
    await testOllamaConnection()
  } else {
    // 其他提供商时清空Ollama模型列表
    availableOllamaModels.value = []
  }
}

/**
 * 快速连接Ollama
 */
const quickConnectOllama = async () => {
  try {
    checkingOllama.value = true
    message.info('正在快速连接Ollama服务器...')
    
    const serverUrl = createForm.serverUrl || ollamaConfig.serverUrl
    const response = await api.models.checkOllamaHealth(serverUrl)
    
    if (response.data.success && response.data.data.healthy) {
      message.success('Ollama服务器连接成功')
      ollamaHealth.value = true
      
      // 连接成功后加载可用模型
      await loadOllamaModels()
      
      if (availableOllamaModels.value.length > 0) {
        message.success(`发现 ${availableOllamaModels.value.length} 个可用模型`)
        console.log('📋 可用模型列表:', availableOllamaModels.value.map(m => m.label))
      } else {
        message.warning('未发现可用模型，请确保Ollama已安装模型')
      }
    } else {
      message.error('Ollama服务器连接失败')
      ollamaHealth.value = false
    }
  } catch (error: any) {
    console.error('快速连接Ollama失败:', error)
    message.error('Ollama服务器连接失败，请检查服务器地址和网络连接')
    ollamaHealth.value = false
  } finally {
    checkingOllama.value = false
  }
}

/**
 * 保存Ollama配置
 */
const saveOllamaConfig = () => {
  ollamaConfigFormRef.value?.validate(async (errors: any) => {
    if (!errors) {
      // 保存到localStorage
      localStorage.setItem('ollama_server_url', ollamaConfig.serverUrl)
      
      // 更新创建表单中的服务器地址
      createForm.serverUrl = ollamaConfig.serverUrl
      
      // 更新ollamaConfig对象，确保响应式更新
      ollamaConfig.serverUrl = ollamaConfig.serverUrl
      
      message.success('Ollama配置已保存')
      showOllamaConfigModal.value = false
    } else {
      message.error('请检查Ollama服务器地址格式')
    }
  })
}

/**
 * 打开Ollama配置对话框
 */
const openOllamaConfigModal = () => {
  // 从localStorage读取保存的配置
  const savedUrl = localStorage.getItem('ollama_server_url')
  if (savedUrl) {
    ollamaConfig.serverUrl = savedUrl
  } else {
    ollamaConfig.serverUrl = 'http://localhost:11434'
  }
  showOllamaConfigModal.value = true
}

/**
 * 检查Ollama健康状态
 */
const checkOllamaHealth = async () => {
  try {
    checkingOllama.value = true
    const response = await api.models.checkOllamaHealth(createForm.serverUrl)
    if (response.data.success) {
      ollamaHealth.value = response.data.data.healthy
      if (ollamaHealth.value) {
        message.success('Ollama服务器连接成功')
      } else {
        message.error('Ollama服务器连接失败')
      }
    } else {
      message.error(response.data.message || '检查Ollama服务器状态失败')
    }
  } catch (error: any) {
    console.error('检查Ollama健康状态失败:', error)
    message.error('检查Ollama服务器状态失败，请检查服务器地址')
    ollamaHealth.value = false
  } finally {
    checkingOllama.value = false
  }
}

// ==================== 模型管理功能 ====================

/**
 * 加载模型列表
 */
const loadModels = async () => {
  try {
    loading.value = true
    console.log('🔍 开始加载模型列表...')
    const response = await api.models.list()
    console.log('📊 模型列表响应:', response)
    
    if (response.data.success) {
      // 处理不同的响应格式
      let modelData = response.data.data
      if (Array.isArray(modelData)) {
        models.value = modelData
      } else if (modelData && Array.isArray(modelData.data)) {
        models.value = modelData.data
      } else if (modelData && Array.isArray(modelData.items)) {
        models.value = modelData.items
      } else {
        models.value = []
      }
      console.log('✅ 模型列表加载成功，共', models.value.length, '个模型')
    } else {
      console.error('❌ API返回错误:', response.data.message)
      message.error(response.data.message || '加载模型列表失败')
      models.value = []
    }
  } catch (error: any) {
    console.error('❌ 加载模型列表失败:', error)
    
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
      message.error(`加载模型列表失败: ${error.message || '未知错误'}`)
    }
    
    // 清空数据，不使用模拟数据
    models.value = [
      {
        id: '1',
        name: 'llama2',
        description: 'Meta的Llama 2模型',
        type: 'llm',
        provider: 'ollama',
        status: 'active',
        server_url: 'http://localhost:11434',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: '2',
        name: 'gpt-3.5-turbo',
        description: 'OpenAI的GPT-3.5模型',
        type: 'llm',
        provider: 'openai',
        status: 'active',
        server_url: 'https://api.openai.com',
        created_at: new Date(Date.now() - 86400000).toISOString(),
        updated_at: new Date(Date.now() - 86400000).toISOString()
      }
    ]
  } finally {
    loading.value = false
  }
}

/**
 * 刷新模型列表
 */
const refreshModels = () => {
  loadModels()
}

/**
 * 编辑模型
 * @param model 要编辑的模型
 */
const editModel = async (model: Model) => {
  try {
    createForm.name = model.name
    createForm.description = model.description || ''
    createForm.type = model.type || 'llm'
    createForm.provider = model.provider
    createForm.serverUrl = model.server_url || 'http://localhost:11434'
    createForm.parametersText = JSON.stringify(model.parameters || {}, null, 2)
    
    editingModel.value = model
    showCreateModal.value = true
    
    // 如果是Ollama模型，加载可用模型列表
    if (model.provider === 'ollama') {
      await loadOllamaModels()
    }
  } catch (error: any) {
    console.error('编辑模型失败:', error)
    message.error('编辑模型失败')
  }
}

/**
 * 测试模型
 * @param model 要测试的模型
 */
const testModel = async (model: Model) => {
  try {
    message.info(`测试模型 ${model.name}...`)
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
    console.error('测试模型失败:', error)
    message.error('模型测试失败，请检查模型配置')
  }
}

/**
 * 删除模型
 * @param model 要删除的模型
 */
const deleteModel = async (model: Model) => {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除模型 "${model.name}" 吗？此操作不可撤销。`,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        const response = await api.models.delete(model.id)
        if (response.data.success) {
          message.success('模型删除成功')
          await loadModels()
        } else {
          message.error(response.data.message || '删除失败')
        }
      } catch (error: any) {
        console.error('删除模型失败:', error)
        message.error('删除模型失败，请稍后重试')
      }
    }
  })
}

/**
 * 创建或更新模型
 */
const createModel = async () => {
  createFormRef.value?.validate(async (errors: any) => {
    if (!errors) {
      try {
        creating.value = true
        
        // 验证JSON格式
        let parameters = {}
        try {
          parameters = JSON.parse(createForm.parametersText)
        } catch (e) {
          message.error('参数配置JSON格式错误')
          return
        }
        
        // 对于Ollama模型，验证是否选择了可用模型
        if (createForm.provider === 'ollama') {
          const isAvailableModel = availableOllamaModels.value.some(m => m.value === createForm.name)
          if (!isAvailableModel && availableOllamaModels.value.length > 0) {
            message.warning('建议从可用模型列表中选择，以确保模型可用')
          }
        }
        
        const modelData = {
          name: createForm.name,
          description: createForm.description,
          type: createForm.type,
          provider: createForm.provider,
          server_url: createForm.serverUrl,
          parameters: parameters
        }
        
        console.log('📝 创建模型数据:', modelData)
        
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
          resetCreateForm()
        } else {
          message.error(response.data.message || (editingModel.value ? '更新失败' : '创建失败'))
        }
      } catch (error: any) {
        console.error('创建/更新模型失败:', error)
        console.error('错误详情:', error.response?.data)
        message.error(error.response?.data?.message || (editingModel.value ? '更新失败' : '创建失败'))
      } finally {
        creating.value = false
      }
    } else {
      message.error('请检查模型信息')
    }
  })
}

/**
 * 取消创建
 */
const cancelCreate = () => {
  showCreateModal.value = false
  resetCreateForm()
}

/**
 * 重置创建表单
 */
const resetCreateForm = () => {
  createForm.name = ''
  createForm.description = ''
  createForm.type = 'llm'
  createForm.provider = 'ollama'
  createForm.parametersText = '{}'
  // 从localStorage读取保存的Ollama服务器地址
  const savedUrl = localStorage.getItem('ollama_server_url')
  createForm.serverUrl = savedUrl || 'http://localhost:11434'
  editingModel.value = null
  
  // 清空Ollama模型列表
  availableOllamaModels.value = []
}

// ==================== 监听器 ====================

// 监听配置变化
watch(() => ollamaConfig.serverUrl, (newUrl) => {
  if (newUrl && newUrl !== createForm.serverUrl) {
    createForm.serverUrl = newUrl
    // 同时保存到localStorage
    localStorage.setItem('ollama_server_url', newUrl)
  }
})

// 监听创建对话框显示状态
watch(showCreateModal, async (isVisible) => {
  if (isVisible && !editingModel.value) {
    // 新建模型时，如果是Ollama提供商，自动连接并加载可用模型
    if (createForm.provider === 'ollama') {
      console.log('🔄 新建模型对话框打开，自动连接Ollama...')
      message.info('正在连接Ollama服务器并加载可用模型...')
      await testOllamaConnection()
    }
  } else if (isVisible && editingModel.value) {
    // 编辑模型时，如果是Ollama模型，加载可用模型列表
    if (editingModel.value.provider === 'ollama') {
      console.log('🔄 编辑Ollama模型，加载可用模型列表...')
      await loadOllamaModels()
    }
  }
})

// ==================== 调试和工具函数 ====================

/**
 * 显示当前Ollama配置
 */
const showCurrentOllamaConfig = () => {
  const savedUrl = localStorage.getItem('ollama_server_url')
  console.log('🔧 当前Ollama配置:')
  console.log('  - localStorage中的URL:', savedUrl)
  console.log('  - ollamaConfig.serverUrl:', ollamaConfig.serverUrl)
  console.log('  - createForm.serverUrl:', createForm.serverUrl)
  
  if (savedUrl) {
    message.info(`当前Ollama服务器地址: ${savedUrl}`)
  } else {
    message.info('未配置Ollama服务器地址，使用默认值: http://localhost:11434')
  }
}

/**
 * 初始化Ollama配置
 */
const initOllamaConfig = () => {
  const savedUrl = localStorage.getItem('ollama_server_url')
  if (savedUrl) {
    ollamaConfig.serverUrl = savedUrl
    createForm.serverUrl = savedUrl
    console.log('✅ 已加载保存的Ollama配置:', savedUrl)
  } else {
    console.log('ℹ️ 使用默认Ollama配置: http://localhost:11434')
  }
}

// ==================== 生命周期钩子 ====================

/**
 * 组件挂载时的初始化
 */
onMounted(() => {
  console.log('🔧 检查localStorage中的token:', localStorage.getItem('token'))
  console.log('🔧 开发环境:', import.meta.env.DEV)
  
  // 初始化Ollama配置
  initOllamaConfig()
  
  // 加载模型列表
  loadModels()
})
</script>

<style scoped>
/* 模型管理页面容器样式 */
.models-container {
  min-height: 100vh;
}

/* 模型卡片样式 */
.model-card {
  transition: all 0.3s ease;
  height: 100%;
  border: 1px solid var(--n-border-color);
}

/* 模型卡片悬停效果 */
.model-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: var(--n-primary-color);
}

/* 模型卡片内容布局 */
.model-card-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 模型头部样式 */
.model-header {
  flex: 1;
}

/* 模型元信息样式 */
.model-meta {
  flex: 1;
}

/* 模型操作按钮样式 */
.model-actions {
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid var(--n-border-color);
}

/* 空状态样式 */
.empty-state {
  color: var(--n-text-color-3);
}

/* 加载状态样式 */
.loading-state {
  color: var(--n-text-color-3);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .models-container {
    padding: 16px;
  }
  
  .actions {
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .models-container {
    padding: 12px;
  }
  
  .page-header {
    margin-bottom: 16px;
  }
  
  .actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .model-card-content {
    padding: 8px;
  }
  
  .model-header h3 {
    font-size: 16px;
  }
  
  .model-meta {
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .models-container {
    padding: 8px;
  }
  
  .page-header h1 {
    font-size: 20px;
  }
  
  .actions {
    gap: 6px;
  }
}

/* 深色模式适配 */
:deep(.dark) .model-card {
  background-color: var(--n-color);
  border-color: var(--n-border-color);
}

:deep(.dark) .model-card:hover {
  border-color: var(--n-primary-color);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

/* 模态框优化 */
:deep(.n-modal) {
  background: var(--n-color);
}

:deep(.n-modal .n-card) {
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
}

:deep(.n-modal .n-dialog) {
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
}

/* 响应式模态框 */
@media (max-width: 768px) {
  :deep(.n-modal .n-card),
  :deep(.n-modal .n-dialog) {
    max-width: 95vw;
    margin: 10px;
  }
}
</style> 