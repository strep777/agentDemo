<template>
  <div class="analytics-page">
    <n-card title="数据分析" class="mb-6">
      <n-space vertical size="large">
        <!-- 时间范围选择 -->
        <n-space align="center">
          <span class="text-sm text-gray-600">时间范围：</span>
          <n-select
            v-model:value="timeRange"
            :options="timeRangeOptions"
            style="width: 200px"
            @update:value="loadAnalytics"
          />
        </n-space>
        
        <!-- 统计卡片 -->
        <n-grid :cols="4" :x-gap="16">
          <n-grid-item v-for="stat in stats" :key="stat.key">
            <n-card size="small">
              <n-space vertical align="center">
                <n-icon size="32" :color="stat.color">
                  <component :is="stat.icon" />
                </n-icon>
                <div class="text-center">
                  <div class="text-2xl font-bold">{{ stat.value }}</div>
                  <div class="text-sm text-gray-500">{{ stat.label }}</div>
                </div>
              </n-space>
            </n-card>
          </n-grid-item>
        </n-grid>
      </n-space>
    </n-card>

    <!-- 图表区域 -->
    <n-grid :cols="2" :x-gap="16" :y-gap="16">
      <!-- 对话趋势图 -->
      <n-grid-item>
        <n-card title="对话趋势">
          <div ref="conversationChartRef" style="height: 300px;"></div>
        </n-card>
      </n-grid-item>

      <!-- 智能体使用统计 -->
      <n-grid-item>
        <n-card title="智能体使用统计">
          <div ref="agentChartRef" style="height: 300px;"></div>
        </n-card>
      </n-grid-item>

      <!-- 消息类型分布 -->
      <n-grid-item>
        <n-card title="消息类型分布">
          <div ref="messageChartRef" style="height: 300px;"></div>
        </n-card>
      </n-grid-item>

      <!-- 响应时间分析 -->
      <n-grid-item>
        <n-card title="响应时间分析">
          <div ref="responseChartRef" style="height: 300px;"></div>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 详细数据表格 -->
    <n-card title="详细数据" class="mt-6">
      <n-tabs v-model:value="activeTab" type="line">
        <n-tab-pane name="conversations" tab="对话数据">
          <n-data-table
            :columns="conversationColumns"
            :data="conversationData"
            :pagination="pagination"
            :loading="loading"
          />
        </n-tab-pane>
        
        <n-tab-pane name="agents" tab="智能体数据">
          <n-data-table
            :columns="agentColumns"
            :data="agentData"
            :pagination="pagination"
            :loading="loading"
          />
        </n-tab-pane>
        
        <n-tab-pane name="messages" tab="消息数据">
          <n-data-table
            :columns="messageColumns"
            :data="messageData"
            :pagination="pagination"
            :loading="loading"
          />
        </n-tab-pane>
      </n-tabs>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { 
  NCard, NGrid, NGridItem, NSpace, NSelect, NDataTable, NTabs, NTabPane, NIcon 
} from 'naive-ui'
import { 
  ChatbubbleOutline, 
  PeopleOutline, 
  TimeOutline, 
  TrendingUpOutline 
} from '@vicons/ionicons5'
import * as echarts from 'echarts'
import { api } from '@/api'
import { useMessage } from 'naive-ui'

const message = useMessage()

// 响应式数据
const timeRange = ref('7d')
const loading = ref(false)
const activeTab = ref('conversations')

// 图表引用
const conversationChartRef = ref()
const agentChartRef = ref()
const messageChartRef = ref()
const responseChartRef = ref()

// 图表实例
let conversationChart: echarts.ECharts | null = null
let agentChart: echarts.ECharts | null = null
let messageChart: echarts.ECharts | null = null
let responseChart: echarts.ECharts | null = null

// 时间范围选项
const timeRangeOptions = [
  { label: '最近7天', value: '7d' },
  { label: '最近30天', value: '30d' },
  { label: '最近90天', value: '90d' },
  { label: '最近一年', value: '1y' }
]

// 统计数据
const stats = ref([
  { key: 'conversations', label: '总对话数', value: 0, icon: ChatbubbleOutline, color: '#18a058' },
  { key: 'agents', label: '活跃智能体', value: 0, icon: PeopleOutline, color: '#2080f0' },
  { key: 'messages', label: '总消息数', value: 0, icon: TrendingUpOutline, color: '#f0a020' },
  { key: 'avgResponse', label: '平均响应时间', value: '0s', icon: TimeOutline, color: '#d03050' }
])

// 表格数据
const conversationData = ref<any[]>([])
const agentData = ref<any[]>([])
const messageData = ref<any[]>([])

// 表格列定义
const conversationColumns = [
  { title: '对话ID', key: 'id', width: 120 },
  { title: '智能体', key: 'agent_name', width: 150 },
  { title: '消息数', key: 'message_count', width: 100 },
  { title: '创建时间', key: 'created_at', width: 180 },
  { title: '最后活跃', key: 'updated_at', width: 180 }
]

const agentColumns = [
  { title: '智能体名称', key: 'name', width: 200 },
  { title: '对话数', key: 'conversation_count', width: 100 },
  { title: '消息数', key: 'message_count', width: 100 },
  { title: '平均响应时间', key: 'avg_response_time', width: 150 },
  { title: '状态', key: 'status', width: 100 }
]

const messageColumns = [
  { title: '消息ID', key: 'id', width: 120 },
  { title: '类型', key: 'type', width: 100 },
  { title: '内容', key: 'content', width: 300 },
  { title: '响应时间', key: 'response_time', width: 120 },
  { title: '时间', key: 'created_at', width: 180 }
]

const pagination = ref({
  page: 1,
  pageSize: 20,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100],
  itemCount: 0,
  onChange: (page: number) => {
    pagination.value.page = page
    loadTableData()
  },
  onUpdatePageSize: (pageSize: number) => {
    pagination.value.pageSize = pageSize
    pagination.value.page = 1
    loadTableData()
  }
})

// 统一的错误处理函数
const handleError = (error: any): string => {
  console.error('API错误:', error)
  
  if (error.code === 'ECONNABORTED') {
    return '请求超时，请检查后端服务是否正常运行'
  } else if (error.code === 'ERR_NETWORK') {
    return '网络连接失败，请检查网络连接'
  } else if (error.response?.status === 500) {
    return '服务器内部错误，请稍后重试'
  } else if (error.response?.status === 404) {
    return 'API端点不存在，请检查后端配置'
  } else if (error.response?.status === 401) {
    return '认证失败，请重新登录'
  } else if (error.response?.status === 403) {
    return '权限不足，无法访问此资源'
  } else if (error.response?.status === 422) {
    return '请求参数错误，请检查输入数据'
  } else {
    return `请求失败: ${error.message || '未知错误'}`
  }
}

// 初始化图表
const initCharts = () => {
  nextTick(() => {
    if (conversationChartRef.value) {
      conversationChart = echarts.init(conversationChartRef.value)
    }
    if (agentChartRef.value) {
      agentChart = echarts.init(agentChartRef.value)
    }
    if (messageChartRef.value) {
      messageChart = echarts.init(messageChartRef.value)
    }
    if (responseChartRef.value) {
      responseChart = echarts.init(responseChartRef.value)
    }
  })
}

// 加载分析数据
const loadAnalytics = async () => {
  try {
    loading.value = true
    console.log('🔍 开始加载分析数据...')
    
    const response = await api.dashboard.analytics()
    
    if (response.data.success) {
      const data = response.data.data
      console.log('📊 分析数据:', data)
      
      // 更新统计数据
      stats.value[0].value = data.total_conversations || 0
      stats.value[1].value = data.active_agents || 0
      stats.value[2].value = data.total_messages || 0
      stats.value[3].value = `${data.avg_response_time || 0}s`
      
      // 更新图表
      updateCharts(data)
      
      // 更新表格数据
      conversationData.value = data.conversations || []
      agentData.value = data.agents || []
      messageData.value = data.messages || []
      
      console.log('✅ 分析数据加载成功')
    } else {
      console.error('❌ API返回错误:', response.data.message)
      message.error(response.data.message || '加载数据失败')
    }
  } catch (error: any) {
    console.error('❌ 加载分析数据失败:', error)
    message.error(handleError(error))
    
    // 清空数据，不使用模拟数据
    stats.value[0].value = 0
    stats.value[1].value = 0
    stats.value[2].value = 0
    stats.value[3].value = '0s'
    
    // 清空图表数据
    updateCharts({
      conversation_trend: {
        dates: [],
        values: []
      },
      agent_usage: [],
      message_types: [],
      response_times: {
        ranges: [],
        counts: []
      }
    })
  } finally {
    loading.value = false
  }
}

// 更新图表
const updateCharts = (data: any) => {
  // 对话趋势图
  if (conversationChart) {
    conversationChart.setOption({
      title: { text: '对话趋势' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: data.conversation_trend?.dates || [] },
      yAxis: { type: 'value' },
      series: [{
        name: '对话数',
        type: 'line',
        data: data.conversation_trend?.values || [],
        smooth: true,
        lineStyle: { color: '#2080f0' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(32, 128, 240, 0.3)' },
              { offset: 1, color: 'rgba(32, 128, 240, 0.1)' }
            ]
          }
        }
      }]
    })
  }
  
  // 智能体使用统计
  if (agentChart) {
    agentChart.setOption({
      title: { text: '智能体使用统计' },
      tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: {c} ({d}%)' },
      legend: { orient: 'vertical', left: 'left', top: 'middle' },
      series: [{
        name: '使用次数',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        data: data.agent_usage || [],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    })
  }
  
  // 消息类型分布
  if (messageChart) {
    messageChart.setOption({
      title: { text: '消息类型分布' },
      tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: {c} ({d}%)' },
      legend: { orient: 'vertical', left: 'left', top: 'middle' },
      series: [{
        name: '消息数',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        data: data.message_types || [],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    })
  }
  
  // 响应时间分析
  if (responseChart) {
    responseChart.setOption({
      title: { text: '响应时间分析' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: data.response_times?.ranges || [] },
      yAxis: { type: 'value' },
      series: [{
        name: '消息数',
        type: 'bar',
        data: data.response_times?.counts || [],
        itemStyle: { color: '#18a058' }
      }]
    })
  }
}

// 加载表格数据
const loadTableData = async () => {
  try {
    loading.value = true
    console.log('🔍 开始加载表格数据...')
    
    const response = await api.dashboard.analytics()
    
    if (response.data.success) {
      const data = response.data.data
      console.log('📊 表格数据:', data)
      
      if (activeTab.value === 'conversations') {
        conversationData.value = data.conversations || []
        pagination.value.itemCount = data.total_conversations || 0
      } else if (activeTab.value === 'agents') {
        agentData.value = data.agents || []
        pagination.value.itemCount = data.active_agents || 0
      } else if (activeTab.value === 'messages') {
        messageData.value = data.messages || []
        pagination.value.itemCount = data.total_messages || 0
      }
      
      console.log('✅ 表格数据加载成功')
    } else {
      console.error('❌ API返回错误:', response.data.message)
      message.error(response.data.message || '加载表格数据失败')
    }
  } catch (error: any) {
    console.error('❌ 加载表格数据失败:', error)
    message.error(handleError(error))
    
    // 清空数据，不使用模拟数据
    if (activeTab.value === 'conversations') {
      conversationData.value = []
    } else if (activeTab.value === 'agents') {
      agentData.value = []
    } else if (activeTab.value === 'messages') {
      messageData.value = []
    }
  } finally {
    loading.value = false
  }
}

// 监听标签页切换
watch(activeTab, () => {
  pagination.value.page = 1
  loadTableData()
})

// 处理窗口大小变化
const handleResize = () => {
  if (conversationChart) {
    conversationChart.resize()
  }
  if (agentChart) {
    agentChart.resize()
  }
  if (messageChart) {
    messageChart.resize()
  }
  if (responseChart) {
    responseChart.resize()
  }
}

onMounted(() => {
  console.log('🔧 初始化分析页面...')
  initCharts()
  loadAnalytics()
  loadTableData()
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

// 组件卸载时清理
import { onUnmounted } from 'vue'
onUnmounted(() => {
  if (conversationChart) {
    conversationChart.dispose()
  }
  if (agentChart) {
    agentChart.dispose()
  }
  if (messageChart) {
    messageChart.dispose()
  }
  if (responseChart) {
    responseChart.dispose()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.analytics-page {
  padding: 20px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .analytics-page {
    padding: 16px;
  }
  
  .n-grid {
    grid-template-columns: repeat(2, 1fr) !important;
  }
}

@media (max-width: 1024px) {
  .analytics-page {
    padding: 16px;
  }
  
  .n-grid {
    grid-template-columns: 1fr !important;
  }
  
  .n-card {
    margin-bottom: 16px;
  }
}

@media (max-width: 768px) {
  .analytics-page {
    padding: 12px;
  }
  
  .n-grid {
    grid-template-columns: 1fr !important;
  }
  
  .n-card {
    margin-bottom: 12px;
    padding: 12px;
  }
  
  .n-data-table {
    font-size: 12px;
  }
  
  .n-tabs :deep(.n-tabs-tab) {
    padding: 8px 12px;
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .analytics-page {
    padding: 8px;
  }
  
  .n-card {
    padding: 8px;
    margin-bottom: 8px;
  }
  
  .n-data-table {
    font-size: 11px;
  }
  
  .n-tabs :deep(.n-tabs-tab) {
    padding: 6px 8px;
    font-size: 11px;
  }
  
  .text-2xl {
    font-size: 18px !important;
  }
  
  .text-sm {
    font-size: 10px !important;
  }
}

/* 图表容器样式 */
.n-card :deep(.n-card__content) {
  padding: 16px;
}

/* 表格样式优化 */
.n-data-table :deep(.n-data-table) {
  border-radius: 8px;
  overflow: hidden;
}

/* 标签页样式 */
.n-tabs :deep(.n-tabs-tab) {
  padding: 12px 16px;
}

.n-tabs :deep(.n-tabs-tab--active) {
  color: var(--n-primary-color);
  border-bottom-color: var(--n-primary-color);
}
</style> 