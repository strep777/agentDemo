import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api'
import type { Model, ApiResponse } from '@/types'

export const useModelsStore = defineStore('models', () => {
  // 状态
  const models = ref<Model[]>([])
  const loading = ref(false)

  // 计算属性
  const activeModels = computed(() => 
    models.value.filter(model => 
      model.status === 'active' || 
      model.status === 'available' || 
      (typeof model.status === 'boolean' && model.status === true)
    )
  )

  // 获取模型列表
  const getModels = async () => {
    try {
      loading.value = true
      console.log('🔍 开始获取模型列表...')
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
        
        // 确保模型数据的一致性
        models.value = models.value.filter(model => 
          model && model.id && model.name && 
          (model.status === 'active' || model.status === 'available' || 
           (typeof model.status === 'boolean' && model.status === true))
        )
        
        console.log('✅ 获取模型列表成功:', models.value.length, '个模型')
        models.value.forEach(model => {
          console.log(`  - ${model.name} (${model.id}) - 状态: ${model.status}`)
        })
      } else {
        console.error('❌ 获取模型列表失败:', response.data)
        models.value = []
      }
    } catch (error: any) {
      console.error('❌ 获取模型列表异常:', error)
      
      // 根据错误类型显示不同的错误信息
      if (error.code === 'ECONNABORTED') {
        console.error('请求超时，请检查后端服务是否正常运行')
      } else if (error.code === 'ERR_NETWORK') {
        console.error('网络连接失败，请检查网络连接')
      } else if (error.response?.status === 500) {
        console.error('服务器内部错误，请稍后重试')
      } else if (error.response?.status === 404) {
        console.error('API端点不存在，请检查后端配置')
      } else if (error.response?.status === 401) {
        console.error('认证失败，请重新登录')
      } else {
        console.error(`获取模型列表失败: ${error.message || '未知错误'}`)
      }
      
      models.value = []
    } finally {
      loading.value = false
    }
  }

  // 获取单个模型
  const getModel = async (id: string): Promise<Model | null> => {
    try {
      console.log('🔍 获取单个模型:', id)
      const response = await api.models.get(id)
      if (response.data.success) {
        console.log('✅ 获取模型成功:', response.data.data.name)
        return response.data.data
      } else {
        console.error('❌ 获取模型失败:', response.data.message)
        return null
      }
    } catch (error: any) {
      console.error('❌ 获取模型异常:', error)
      return null
    }
  }

  // 创建模型
  const createModel = async (data: Partial<Model>): Promise<Model | null> => {
    try {
      console.log('🔍 创建模型:', data)
      const response = await api.models.create(data)
      if (response.data.success) {
        console.log('✅ 创建模型成功:', response.data.data.name)
        await getModels() // 重新加载列表
        return response.data.data
      } else {
        console.error('❌ 创建模型失败:', response.data.message)
        return null
      }
    } catch (error: any) {
      console.error('❌ 创建模型异常:', error)
      return null
    }
  }

  // 更新模型
  const updateModel = async (id: string, data: Partial<Model>): Promise<Model | null> => {
    try {
      console.log('🔍 更新模型:', id, data)
      const response = await api.models.update(id, data)
      if (response.data.success) {
        console.log('✅ 更新模型成功:', response.data.data.name)
        await getModels() // 重新加载列表
        return response.data.data
      } else {
        console.error('❌ 更新模型失败:', response.data.message)
        return null
      }
    } catch (error: any) {
      console.error('❌ 更新模型异常:', error)
      return null
    }
  }

  // 删除模型
  const deleteModel = async (id: string): Promise<boolean> => {
    try {
      console.log('🔍 删除模型:', id)
      const response = await api.models.delete(id)
      if (response.data.success) {
        console.log('✅ 删除模型成功')
        await getModels() // 重新加载列表
        return true
      } else {
        console.error('❌ 删除模型失败:', response.data.message)
        return false
      }
    } catch (error: any) {
      console.error('❌ 删除模型异常:', error)
      return false
    }
  }

  // 测试模型
  const testModel = async (id: string, testData: any): Promise<boolean> => {
    try {
      console.log('🔍 测试模型:', id, testData)
      const response = await api.models.test(id, testData)
      if (response.data.success) {
        console.log('✅ 模型测试成功')
        return true
      } else {
        console.error('❌ 模型测试失败:', response.data.message)
        return false
      }
    } catch (error: any) {
      console.error('❌ 模型测试异常:', error)
      return false
    }
  }

  // 检查Ollama健康状态
  const checkOllamaHealth = async (serverUrl?: string): Promise<boolean> => {
    try {
      console.log('🔍 检查Ollama健康状态:', serverUrl)
      const response = await api.models.checkOllamaHealth(serverUrl)
      if (response.data.success) {
        const isHealthy = response.data.data.healthy
        console.log('✅ Ollama健康检查完成:', isHealthy)
        return isHealthy
      } else {
        console.error('❌ Ollama健康检查失败:', response.data.message)
        return false
      }
    } catch (error: any) {
      console.error('❌ Ollama健康检查异常:', error)
      return false
    }
  }

  // 获取Ollama模型列表
  const getOllamaModels = async (serverUrl?: string): Promise<string[]> => {
    try {
      console.log('🔍 获取Ollama模型列表:', serverUrl)
      const response = await api.models.getOllamaModels(serverUrl)
      if (response.data.success) {
        const models = response.data.data.models || []
        console.log('✅ 获取Ollama模型列表成功:', models.length, '个模型')
        return models
      } else {
        console.error('❌ 获取Ollama模型列表失败:', response.data.message)
        return []
      }
    } catch (error: any) {
      console.error('❌ 获取Ollama模型列表异常:', error)
      return []
    }
  }

  // 重置状态
  const reset = () => {
    models.value = []
    loading.value = false
  }

  return {
    // 状态
    models,
    loading,
    
    // 计算属性
    activeModels,
    
    // 方法
    getModels,
    getModel,
    createModel,
    updateModel,
    deleteModel,
    testModel,
    checkOllamaHealth,
    getOllamaModels,
    reset
  }
}) 