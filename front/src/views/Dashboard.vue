<template>
  <div class="dashboard">
    <div v-if="loading" class="loading">
      <n-spin size="large">
        <template #description>
          加载仪表盘数据...
        </template>
      </n-spin>
    </div>
    
    <div v-else class="dashboard-content">
      <!-- 统计卡片 -->
      <div class="stats-grid">
        <n-card class="stat-card" hoverable>
          <div class="stat-content">
            <div class="stat-icon">
              <n-icon size="32" color="#18a058">
                <ServerOutline />
              </n-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalAgents || 0 }}</div>
              <div class="stat-label">智能体总数</div>
            </div>
          </div>
        </n-card>

        <n-card class="stat-card" hoverable>
          <div class="stat-content">
            <div class="stat-icon">
              <n-icon size="32" color="#2080f0">
                <ChatbubblesOutline />
              </n-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalConversations || 0 }}</div>
              <div class="stat-label">对话总数</div>
            </div>
          </div>
        </n-card>

        <n-card class="stat-card" hoverable>
          <div class="stat-content">
            <div class="stat-icon">
              <n-icon size="32" color="#f0a020">
                <BookOutline />
              </n-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalKnowledge || 0 }}</div>
              <div class="stat-label">知识库数量</div>
            </div>
          </div>
        </n-card>

        <n-card class="stat-card" hoverable>
          <div class="stat-content">
            <div class="stat-icon">
              <n-icon size="32" color="#d03050">
                <ExtensionPuzzleOutline />
              </n-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalPlugins || 0 }}</div>
              <div class="stat-label">插件数量</div>
            </div>
          </div>
        </n-card>
      </div>

      <!-- 图表区域 -->
      <div class="charts-grid">
        <n-card title="对话趋势" class="chart-card" hoverable>
          <div ref="conversationChart" class="chart-container"></div>
        </n-card>

        <n-card title="智能体性能" class="chart-card" hoverable>
          <div ref="agentPerformanceChart" class="chart-container"></div>
        </n-card>
      </div>

      <!-- 最近活动 -->
      <n-card title="最近活动" class="activities-card" hoverable>
        <div v-if="recentActivities.length === 0" class="empty-activities">
          <n-icon size="48" color="#d9d9d9">
            <TimeOutline />
          </n-icon>
          <p>暂无活动记录</p>
        </div>
        <div v-else class="activities-list">
          <div
            v-for="activity in recentActivities"
            :key="activity.id"
            class="activity-item"
          >
            <div class="activity-avatar">
              <n-avatar round size="small" :color="getActivityColor(activity.type)">
                <template #icon>
                  <n-icon>
                    <component :is="getActivityIcon(activity.type)" />
                  </n-icon>
                </template>
              </n-avatar>
            </div>
            <div class="activity-content">
              <div class="activity-title">{{ activity.title }}</div>
              <div class="activity-description">{{ activity.description }}</div>
              <div class="activity-time">
                {{ formatTime(activity.timestamp) }}
              </div>
            </div>
          </div>
        </div>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { NCard, NIcon, NAvatar, NSpin } from 'naive-ui'
import {
  ServerOutline,
  ChatbubblesOutline,
  BookOutline,
  ExtensionPuzzleOutline,
  TimeOutline,
  InformationCircleOutline
} from '@vicons/ionicons5'
import * as echarts from 'echarts'
import { api } from '@/api'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import { useMessage } from 'naive-ui'

// 配置dayjs插件
dayjs.extend(relativeTime)

const message = useMessage()

// 响应式数据
const loading = ref(true)
const stats = ref({
  totalAgents: 0,
  totalConversations: 0,
  totalKnowledge: 0,
  totalPlugins: 0
})

const recentActivities = ref<any[]>([])

// 图表引用
const conversationChart = ref<HTMLElement>()
const agentPerformanceChart = ref<HTMLElement>()
let conversationChartInstance: echarts.ECharts | null = null
let agentPerformanceChartInstance: echarts.ECharts | null = null

// 获取统计数据
const fetchStats = async () => {
  try {
    const response = await api.dashboard.stats()
    if (response.data && response.data.success) {
      stats.value = response.data.data
    } else {
      // 使用模拟数据
      stats.value = {
        totalAgents: 12,
        totalConversations: 156,
        totalKnowledge: 8,
        totalPlugins: 15
      }
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    message.error('获取统计数据失败')
    // 使用模拟数据
    stats.value = {
      totalAgents: 12,
      totalConversations: 156,
      totalKnowledge: 8,
      totalPlugins: 15
    }
  }
}

// 获取最近活动
const fetchRecentActivities = async () => {
  try {
    const response = await api.dashboard.recent()
    if (response.data && response.data.success) {
      recentActivities.value = response.data.data
    } else {
      // 使用模拟数据
      recentActivities.value = [
        {
          id: 1,
          type: 'conversation',
          title: '新对话开始',
          description: '用户与智能体Agent-001开始对话',
          timestamp: new Date()
        },
        {
          id: 2,
          type: 'agent',
          title: '智能体创建',
          description: '创建了新的智能体Agent-002',
          timestamp: new Date(Date.now() - 3600000)
        },
        {
          id: 3,
          type: 'knowledge',
          title: '知识库更新',
          description: '更新了知识库"产品文档"',
          timestamp: new Date(Date.now() - 7200000)
        },
        {
          id: 4,
          type: 'plugin',
          title: '插件安装',
          description: '安装了插件"数据分析工具"',
          timestamp: new Date(Date.now() - 10800000)
        }
      ]
    }
  } catch (error) {
    console.error('获取最近活动失败:', error)
    message.error('获取最近活动失败')
    recentActivities.value = []
  }
}

// 初始化对话趋势图表
const initConversationChart = () => {
  if (!conversationChart.value) return

  if (conversationChartInstance) {
    conversationChartInstance.dispose()
  }

  conversationChartInstance = echarts.init(conversationChart.value)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['对话数量', '活跃用户']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '对话数量',
        type: 'line',
        data: [120, 132, 101, 134, 90, 230, 210],
        smooth: true,
        lineStyle: {
          color: '#2080f0'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(32, 128, 240, 0.3)' },
              { offset: 1, color: 'rgba(32, 128, 240, 0.1)' }
            ]
          }
        }
      },
      {
        name: '活跃用户',
        type: 'line',
        data: [220, 182, 191, 234, 290, 330, 310],
        smooth: true,
        lineStyle: {
          color: '#18a058'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(24, 160, 88, 0.3)' },
              { offset: 1, color: 'rgba(24, 160, 88, 0.1)' }
            ]
          }
        }
      }
    ]
  }
  
  conversationChartInstance.setOption(option)
}

// 初始化智能体性能图表
const initAgentPerformanceChart = () => {
  if (!agentPerformanceChart.value) return

  if (agentPerformanceChartInstance) {
    agentPerformanceChartInstance.dispose()
  }

  agentPerformanceChartInstance = echarts.init(agentPerformanceChart.value)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle'
    },
    series: [
      {
        name: '智能体性能',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        data: [
          { value: 35, name: 'Agent-001' },
          { value: 25, name: 'Agent-002' },
          { value: 20, name: 'Agent-003' },
          { value: 15, name: 'Agent-004' },
          { value: 5, name: '其他' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  agentPerformanceChartInstance.setOption(option)
}

// 获取活动图标
const getActivityIcon = (type: string) => {
  const iconMap: Record<string, any> = {
    conversation: ChatbubblesOutline,
    agent: ServerOutline,
    knowledge: BookOutline,
    plugin: ExtensionPuzzleOutline,
    default: InformationCircleOutline
  }
  return iconMap[type] || iconMap.default
}

// 获取活动颜色
const getActivityColor = (type: string) => {
  const colorMap: Record<string, string> = {
    conversation: '#2080f0',
    agent: '#18a058',
    knowledge: '#f0a020',
    plugin: '#d03050',
    default: '#666666'
  }
  return colorMap[type] || colorMap.default
}

// 格式化时间
const formatTime = (timestamp: Date) => {
  return dayjs(timestamp).fromNow()
}

// 处理窗口大小变化
const handleResize = () => {
  if (conversationChartInstance) {
    conversationChartInstance.resize()
  }
  if (agentPerformanceChartInstance) {
    agentPerformanceChartInstance.resize()
  }
}

// 组件挂载
onMounted(async () => {
  try {
    loading.value = true
    await Promise.all([
      fetchStats(),
      fetchRecentActivities()
    ])
    
    // 初始化图表
    await nextTick()
    setTimeout(() => {
      initConversationChart()
      initAgentPerformanceChart()
    }, 100)
  } catch (error) {
    console.error('初始化仪表盘失败:', error)
    message.error('初始化仪表盘失败')
  } finally {
    loading.value = false
  }
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

// 组件卸载
onUnmounted(() => {
  if (conversationChartInstance) {
    conversationChartInstance.dispose()
  }
  if (agentPerformanceChartInstance) {
    agentPerformanceChartInstance.dispose()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.dashboard {
  padding: 24px;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.stat-card {
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: rgba(24, 160, 88, 0.1);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: var(--n-text-color);
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: var(--n-text-color-3);
  margin-top: 4px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
}

.chart-card {
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  transition: all 0.3s ease;
}

.chart-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.chart-container {
  height: 350px;
  width: 100%;
}

.activities-card {
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  transition: all 0.3s ease;
}

.activities-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.empty-activities {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--n-text-color-3);
}

.empty-activities p {
  margin-top: 12px;
  font-size: 14px;
}

.activities-list {
  max-height: 400px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--n-border-color);
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--n-text-color);
  margin-bottom: 4px;
}

.activity-description {
  font-size: 12px;
  color: var(--n-text-color-3);
  margin-bottom: 4px;
  line-height: 1.4;
}

.activity-time {
  font-size: 11px;
  color: var(--n-text-color-4);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard {
    padding: 16px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    height: 250px;
  }
}

@media (max-width: 480px) {
  .dashboard {
    padding: 12px;
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  .chart-container {
    height: 200px;
  }
}

/* 滚动条样式 */
.activities-list::-webkit-scrollbar {
  width: 4px;
}

.activities-list::-webkit-scrollbar-track {
  background: transparent;
}

.activities-list::-webkit-scrollbar-thumb {
  background: var(--n-border-color);
  border-radius: 2px;
}

.activities-list::-webkit-scrollbar-thumb:hover {
  background: var(--n-text-color-3);
}
</style> 