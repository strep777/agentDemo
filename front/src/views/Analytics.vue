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
import { ref, onMounted, nextTick } from 'vue'
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
const conversationData = ref([])
const agentData = ref([])
const messageData = ref([])

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
    const response = await api.get(`/dashboard/analytics?time_range=${timeRange.value}`)
    
    if (response.data.success) {
      const data = response.data.data
      
      // 更新统计数据
      stats.value[0].value = data.total_conversations
      stats.value[1].value = data.active_agents
      stats.value[2].value = data.total_messages
      stats.value[3].value = `${data.avg_response_time}s`
      
      // 更新图表
      updateCharts(data)
      
      // 更新表格数据
      conversationData.value = data.conversations || []
      agentData.value = data.agents || []
      messageData.value = data.messages || []
    }
  } catch (error: any) {
    // message.error(error.response?.data?.error || '加载数据失败') // Removed useMessage
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
        smooth: true
      }]
    })
  }
  
  // 智能体使用统计
  if (agentChart) {
    agentChart.setOption({
      title: { text: '智能体使用统计' },
      tooltip: { trigger: 'item' },
      series: [{
        name: '使用次数',
        type: 'pie',
        radius: '50%',
        data: data.agent_usage || []
      }]
    })
  }
  
  // 消息类型分布
  if (messageChart) {
    messageChart.setOption({
      title: { text: '消息类型分布' },
      tooltip: { trigger: 'item' },
      series: [{
        name: '消息数',
        type: 'pie',
        radius: '50%',
        data: data.message_types || []
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
        data: data.response_times?.counts || []
      }]
    })
  }
}

// 加载表格数据
const loadTableData = async () => {
  try {
    loading.value = true
    const response = await api.get(`/dashboard/table-data`, {
      params: {
        tab: activeTab.value,
        page: pagination.value.page,
        page_size: pagination.value.pageSize,
        time_range: timeRange.value
      }
    })
    
    if (response.data.success) {
      const data = response.data.data
      if (activeTab.value === 'conversations') {
        conversationData.value = data.items || []
        pagination.value.itemCount = data.total || 0
      } else if (activeTab.value === 'agents') {
        agentData.value = data.items || []
        pagination.value.itemCount = data.total || 0
      } else if (activeTab.value === 'messages') {
        messageData.value = data.items || []
        pagination.value.itemCount = data.total || 0
      }
    }
  } catch (error: any) {
    // message.error(error.response?.data?.error || '加载表格数据失败') // Removed useMessage
  } finally {
    loading.value = false
  }
}

// 监听标签页切换
const handleTabChange = () => {
  pagination.value.page = 1
  loadTableData()
}

onMounted(() => {
  initCharts()
  loadAnalytics()
  loadTableData()
})
</script>

<style scoped>
.analytics-page {
  padding: 20px;
}
</style> 