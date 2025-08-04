import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api'
import type { 
  Agent, 
  PaginationParams,
  PaginatedResponse,
  ApiResponse 
} from '@/types'

export const useAgentsStore = defineStore('agents', () => {
  // 状态
  const agents = ref<Agent[]>([])
  const loading = ref(false)
  const pagination = ref({
    page: 1,
    page_size: 20,
    total: 0,
    pages: 0
  })

  // 计算属性
  const activeAgents = computed(() => 
    agents.value.filter(agent => agent.status === 'active')
  )

  const inactiveAgents = computed(() => 
    agents.value.filter(agent => agent.status === 'inactive')
  )

  // 获取智能体列表
  const getAgents = async (params: PaginationParams = {}) => {
    try {
      loading.value = true
      const response = await api.agents.list()
      
      if (response.data.success) {
        // 修复：正确处理嵌套的data字段
        agents.value = response.data.data.data || response.data.data
        pagination.value = {
          page: response.data.data.page || 1,
          page_size: response.data.data.page_size || 20,
          total: response.data.data.total || agents.value.length,
          pages: response.data.data.pages || 1
        }
        console.log('✅ 获取智能体列表成功:', agents.value.length, '个智能体')
      } else {
        console.error('❌ 获取智能体列表失败:', response.data)
        agents.value = []
      }
    } catch (error: any) {
      console.error('❌ 获取智能体列表异常:', error)
      agents.value = []
    } finally {
      loading.value = false
    }
  }

  // 获取智能体详情
  const getAgent = async (agentId: string): Promise<Agent | null> => {
    try {
      loading.value = true
      const response = await api.agents.get(agentId)
      
      if (response.data.success) {
        return response.data.data
      } else {
        return null
      }
    } catch (error: any) {
      return null
    } finally {
      loading.value = false
    }
  }

  // 创建智能体
  const createAgent = async (data: Partial<Agent>): Promise<Agent | null> => {
    try {
      loading.value = true
      const response = await api.agents.create(data)
      
      if (response.data.success) {
        await getAgents() // 刷新列表
        return response.data.data
      } else {
        return null
      }
    } catch (error: any) {
      return null
    } finally {
      loading.value = false
    }
  }

  // 更新智能体
  const updateAgent = async (agentId: string, data: Partial<Agent>): Promise<Agent | null> => {
    try {
      loading.value = true
      const response = await api.agents.update(agentId, data)
      
      if (response.data.success) {
        await getAgents() // 刷新列表
        return response.data.data
      } else {
        return null
      }
    } catch (error: any) {
      return null
    } finally {
      loading.value = false
    }
  }

  // 删除智能体
  const deleteAgent = async (agentId: string): Promise<boolean> => {
    try {
      loading.value = true
      const response = await api.agents.delete(agentId)
      
      if (response.data.success) {
        await getAgents() // 刷新列表
        return true
      } else {
        return false
      }
    } catch (error: any) {
      return false
    } finally {
      loading.value = false
    }
  }

  // 重置状态
  const reset = () => {
    agents.value = []
    loading.value = false
    pagination.value = {
      page: 1,
      page_size: 20,
      total: 0,
      pages: 0
    }
  }

  return {
    // 状态
    agents,
    loading,
    pagination,
    
    // 计算属性
    activeAgents,
    inactiveAgents,
    
    // 方法
    getAgents,
    getAgent,
    createAgent,
    updateAgent,
    deleteAgent,
    reset
  }
}) 