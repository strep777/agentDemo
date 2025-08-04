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
    models.value.filter(model => model.status === 'available')
  )

  // 获取模型列表
  const getModels = async () => {
    try {
      loading.value = true
      const response = await api.models.list()
      
      if (response.data.success) {
        // 修复：正确处理嵌套的data字段
        models.value = response.data.data.data || response.data.data
        console.log('✅ 获取模型列表成功:', models.value.length, '个模型')
      } else {
        console.error('❌ 获取模型列表失败:', response.data)
        models.value = []
      }
    } catch (error: any) {
      console.error('❌ 获取模型列表异常:', error)
      models.value = []
    } finally {
      loading.value = false
    }
  }

  // 获取单个模型
  const getModel = async (id: string): Promise<Model | null> => {
    try {
      const response = await api.models.get(id)
      if (response.data.success) {
        return response.data.data
      }
      return null
    } catch (error: any) {
      console.error('获取模型失败:', error)
      return null
    }
  }

  // 创建模型
  const createModel = async (data: Partial<Model>): Promise<Model | null> => {
    try {
      const response = await api.models.create(data)
      if (response.data.success) {
        await getModels() // 重新加载列表
        return response.data.data
      }
      return null
    } catch (error: any) {
      console.error('创建模型失败:', error)
      return null
    }
  }

  // 更新模型
  const updateModel = async (id: string, data: Partial<Model>): Promise<Model | null> => {
    try {
      const response = await api.models.update(id, data)
      if (response.data.success) {
        await getModels() // 重新加载列表
        return response.data.data
      }
      return null
    } catch (error: any) {
      console.error('更新模型失败:', error)
      return null
    }
  }

  // 删除模型
  const deleteModel = async (id: string): Promise<boolean> => {
    try {
      const response = await api.models.delete(id)
      if (response.data.success) {
        await getModels() // 重新加载列表
        return true
      }
      return false
    } catch (error: any) {
      console.error('删除模型失败:', error)
      return false
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
    reset
  }
}) 