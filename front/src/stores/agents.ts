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
      console.log('🔍 开始获取智能体列表...')
      const response = await api.agents.list()
      console.log('📊 智能体列表响应:', response)
      
      if (response.data.success) {
        // 处理不同的响应格式
        let agentData = response.data.data
        if (Array.isArray(agentData)) {
          agents.value = agentData
        } else if (agentData && Array.isArray(agentData.data)) {
          agents.value = agentData.data
        } else if (agentData && Array.isArray(agentData.items)) {
          agents.value = agentData.items
        } else {
          agents.value = []
        }
        
        // 确保智能体数据的一致性
        agents.value = agents.value.filter(agent => 
          agent && agent.id && agent.name && 
          (agent.status === 'active' || agent.status === 'available')
        )
        
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
        console.error(`获取智能体列表失败: ${error.message || '未知错误'}`)
      }
      
      agents.value = []
    } finally {
      loading.value = false
    }
  }

  // 获取智能体详情
  const getAgent = async (agentId: string): Promise<Agent | null> => {
    try {
      console.log('🔍 获取智能体详情:', agentId)
      loading.value = true
      const response = await api.agents.get(agentId)
      
      if (response.data.success) {
        console.log('✅ 获取智能体详情成功:', response.data.data.name)
        return response.data.data
      } else {
        console.error('❌ 获取智能体详情失败:', response.data.message)
        return null
      }
    } catch (error: any) {
      console.error('❌ 获取智能体详情异常:', error)
      return null
    } finally {
      loading.value = false
    }
  }

  // 创建智能体
  const createAgent = async (data: Partial<Agent>): Promise<Agent | null> => {
    try {
      console.log('🔍 创建智能体:', data)
      loading.value = true
      const response = await api.agents.create(data)
      
      if (response.data.success) {
        console.log('✅ 创建智能体成功:', response.data.data.name)
        await getAgents() // 刷新列表
        return response.data.data
      } else {
        console.error('❌ 创建智能体失败:', response.data.message)
        return null
      }
    } catch (error: any) {
      console.error('❌ 创建智能体异常:', error)
      return null
    } finally {
      loading.value = false
    }
  }

  // 更新智能体
  const updateAgent = async (agentId: string, data: Partial<Agent>): Promise<Agent | null> => {
    try {
      console.log('🔍 更新智能体:', agentId, data)
      loading.value = true
      const response = await api.agents.update(agentId, data)
      
      if (response.data.success) {
        console.log('✅ 更新智能体成功:', response.data.data.name)
        await getAgents() // 刷新列表
        return response.data.data
      } else {
        console.error('❌ 更新智能体失败:', response.data.message)
        return null
      }
    } catch (error: any) {
      console.error('❌ 更新智能体异常:', error)
      return null
    } finally {
      loading.value = false
    }
  }

  // 删除智能体
  const deleteAgent = async (agentId: string): Promise<boolean> => {
    try {
      console.log('🔍 删除智能体:', agentId)
      loading.value = true
      const response = await api.agents.delete(agentId)
      
      if (response.data.success) {
        console.log('✅ 删除智能体成功')
        await getAgents() // 刷新列表
        return true
      } else {
        console.error('❌ 删除智能体失败:', response.data.message)
        return false
      }
    } catch (error: any) {
      console.error('❌ 删除智能体异常:', error)
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