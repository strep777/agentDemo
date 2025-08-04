<template>
  <div class="workflow-editor">
    <!-- 工具栏 -->
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <n-button size="small" @click="addNode('trigger')">
          <template #icon>
            <n-icon>
              <PlayOutline />
            </n-icon>
          </template>
          触发器
        </n-button>
        <n-button size="small" @click="addNode('action')">
          <template #icon>
            <n-icon>
              <SettingsOutline />
            </n-icon>
          </template>
          动作
        </n-button>
        <n-button size="small" @click="addNode('condition')">
          <template #icon>
            <n-icon>
              <GitBranchOutline />
            </n-icon>
          </template>
          条件
        </n-button>
        <n-button size="small" @click="addNode('api')">
          <template #icon>
            <n-icon>
              <GlobeOutline />
            </n-icon>
          </template>
          API调用
        </n-button>
        <n-button size="small" @click="addNode('llm')">
          <template #icon>
            <n-icon>
              <ChatbubblesOutline />
            </n-icon>
          </template>
          AI模型
        </n-button>
      </div>
      <div class="toolbar-right">
        <n-button size="small" @click="validateWorkflow">验证</n-button>
        <n-button size="small" @click="saveWorkflow" type="primary">保存</n-button>
        <n-button size="small" @click="testWorkflow">测试</n-button>
        <n-button size="small" @click="publishWorkflow">发布</n-button>
      </div>
    </div>

    <!-- 画布区域 -->
    <div class="editor-canvas" ref="canvasRef">
      <div class="canvas-container">
        <!-- 节点 -->
        <div
          v-for="node in workflowNodes"
          :key="node.id"
          class="workflow-node"
          :class="[`node-${node.type}`, { selected: selectedNode?.id === node.id }]"
          :style="{
            left: node.x + 'px',
            top: node.y + 'px'
          }"
          @click="selectNode(node)"
          @mousedown="startDrag(node, $event)"
        >
          <div class="node-header">
            <n-icon size="16">
              <component :is="getNodeIcon(node.type)" />
            </n-icon>
            <span class="node-title">{{ node.title }}</span>
            <n-button size="tiny" circle @click.stop="deleteNode(node)">
              <template #icon>
                <n-icon>
                  <CloseOutline />
                </n-icon>
              </template>
            </n-button>
          </div>
          <div class="node-content">
            <div class="node-description">{{ node.description }}</div>
            <div v-if="node.config" class="node-config">
              <n-button size="tiny" @click.stop="editNodeConfig(node)">
                配置
              </n-button>
            </div>
          </div>
          <div class="node-ports">
            <div class="port port-input" @click="addConnection(node, 'input')"></div>
            <div class="port port-output" @click="addConnection(node, 'output')"></div>
          </div>
        </div>

        <!-- 连接线 -->
        <svg class="connections-layer">
          <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" 
              refX="9" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="#666" />
            </marker>
          </defs>
          <g>
            <line
              v-for="connection in workflowConnections"
              :key="connection.id"
              :x1="connection.startX"
              :y1="connection.startY"
              :x2="connection.endX"
              :y2="connection.endY"
              stroke="#666"
              stroke-width="2"
              marker-end="url(#arrowhead)"
            />
          </g>
        </svg>
      </div>
    </div>

    <!-- 属性面板 -->
    <div class="editor-panel">
      <div class="panel-header">
        <h3>属性</h3>
      </div>
      <div class="panel-content" v-if="selectedNode">
        <n-form label-placement="left" label-width="auto">
          <n-form-item label="标题">
            <n-input v-model:value="selectedNode.title" />
          </n-form-item>
          <n-form-item label="描述">
            <n-input v-model:value="selectedNode.description" type="textarea" />
          </n-form-item>
          <n-form-item label="类型">
            <n-tag>{{ selectedNode.type }}</n-tag>
          </n-form-item>
          <n-form-item label="配置">
            <n-button size="small" @click="editNodeConfig(selectedNode)">
              编辑配置
            </n-button>
          </n-form-item>
        </n-form>
      </div>
      <div v-else class="panel-empty">
        <n-icon size="48" color="#d9d9d9">
          <InformationCircleOutline />
        </n-icon>
        <p>选择一个节点来编辑属性</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useMessage } from 'naive-ui'
import {
  NButton,
  NIcon,
  NForm,
  NFormItem,
  NInput,
  NTag
} from 'naive-ui'
import {
  PlayOutline,
  SettingsOutline,
  GitBranchOutline,
  GlobeOutline,
  ChatbubblesOutline,
  CloseOutline,
  InformationCircleOutline
} from '@vicons/ionicons5'
import { api } from '@/api'

const message = useMessage()

// Props
const props = defineProps<{
  workflowId?: string
  initialData?: any
}>()

// Emits
const emit = defineEmits<{
  save: [data: any]
  test: [data: any]
  publish: [data: any]
}>()

// 响应式数据
const workflowNodes = ref<any[]>([])
const workflowConnections = ref<any[]>([])
const selectedNode = ref<any>(null)
const canvasRef = ref<HTMLElement>()
let isDragging = false
let dragNode: any = null
let dragOffset = { x: 0, y: 0 }

// 初始化数据
const initData = () => {
  if (props.initialData) {
    workflowNodes.value = props.initialData.nodes || []
    workflowConnections.value = props.initialData.connections || []
  }
}

// 添加节点
const addNode = (type: string) => {
  const node = {
    id: `node_${Date.now()}`,
    type,
    title: getNodeTitle(type),
    description: getNodeDescription(type),
    x: 100,
    y: 100,
    config: getDefaultConfig(type)
  }
  workflowNodes.value.push(node)
}

// 获取节点标题
const getNodeTitle = (type: string) => {
  const titles: Record<string, string> = {
    trigger: '触发器',
    action: '动作',
    condition: '条件',
    api: 'API调用',
    llm: 'AI模型'
  }
  return titles[type] || type
}

// 获取节点描述
const getNodeDescription = (type: string) => {
  const descriptions: Record<string, string> = {
    trigger: '工作流的触发点',
    action: '执行具体操作',
    condition: '判断条件分支',
    api: '调用外部API',
    llm: '调用AI模型'
  }
  return descriptions[type] || ''
}

// 获取默认配置
const getDefaultConfig = (type: string) => {
  const configs: Record<string, any> = {
    trigger: { triggerType: 'manual', condition: '' },
    action: { actionType: 'send_message', parameters: '{}' },
    condition: { condition: '' },
    api: { url: '', method: 'GET', headers: '{}' },
    llm: { model: 'gpt-3.5-turbo', prompt: '', parameters: '{}' }
  }
  return configs[type] || {}
}

// 获取节点图标
const getNodeIcon = (type: string) => {
  const icons: Record<string, any> = {
    trigger: PlayOutline,
    action: SettingsOutline,
    condition: GitBranchOutline,
    api: GlobeOutline,
    llm: ChatbubblesOutline
  }
  return icons[type] || InformationCircleOutline
}

// 选择节点
const selectNode = (node: any) => {
  selectedNode.value = node
}

// 删除节点
const deleteNode = (node: any) => {
  const index = workflowNodes.value.findIndex(n => n.id === node.id)
  if (index > -1) {
    workflowNodes.value.splice(index, 1)
  }
  // 删除相关连接
  workflowConnections.value = workflowConnections.value.filter(
    conn => conn.sourceId !== node.id && conn.targetId !== node.id
  )
}

// 编辑节点配置
const editNodeConfig = (node: any) => {
  // 这里可以打开配置模态框
  console.log('编辑节点配置', node)
}

// 添加连接
const addConnection = (node: any, portType: string) => {
  // 实现连接逻辑
  console.log('添加连接', node, portType)
}

// 拖拽相关
const startDrag = (node: any, event: MouseEvent) => {
  isDragging = true
  dragNode = node
  const rect = (event.target as HTMLElement).getBoundingClientRect()
  dragOffset.x = event.clientX - rect.left
  dragOffset.y = event.clientY - rect.top
  
  document.addEventListener('mousemove', handleDrag)
  document.addEventListener('mouseup', stopDrag)
}

const handleDrag = (event: MouseEvent) => {
  if (!isDragging || !dragNode) return
  
  const canvasRect = canvasRef.value?.getBoundingClientRect()
  if (canvasRect) {
    dragNode.x = event.clientX - canvasRect.left - dragOffset.x
    dragNode.y = event.clientY - canvasRect.top - dragOffset.y
  }
}

const stopDrag = () => {
  isDragging = false
  dragNode = null
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
}

// 验证工作流
const validateWorkflow = async () => {
  try {
    const definition = {
      nodes: workflowNodes.value,
      edges: workflowConnections.value
    }
    
    const response = await api.workflows.validate({ definition })
    if (response.data && response.data.success) {
      message.success('工作流验证通过')
    } else {
      message.error('工作流验证失败')
    }
  } catch (error) {
    console.error('验证工作流失败:', error)
    message.error('验证失败')
  }
}

// 保存工作流
const saveWorkflow = () => {
  const data = {
    nodes: workflowNodes.value,
    connections: workflowConnections.value
  }
  emit('save', data)
}

// 测试工作流
const testWorkflow = () => {
  const data = {
    nodes: workflowNodes.value,
    connections: workflowConnections.value
  }
  emit('test', data)
}

// 发布工作流
const publishWorkflow = () => {
  const data = {
    nodes: workflowNodes.value,
    connections: workflowConnections.value
  }
  emit('publish', data)
}

// 组件挂载
onMounted(() => {
  initData()
})

// 组件卸载
onUnmounted(() => {
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
})
</script>

<style scoped>
.workflow-editor {
  display: flex;
  height: 100%;
  gap: 0;
}

.editor-toolbar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10;
  background: var(--n-color);
  border-bottom: 1px solid var(--n-border-color);
  padding: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 8px;
}

.editor-canvas {
  flex: 1;
  position: relative;
  background: #f5f5f5;
  overflow: hidden;
}

.canvas-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 600px;
}

.workflow-node {
  position: absolute;
  width: 200px;
  background: var(--n-color);
  border: 2px solid var(--n-border-color);
  border-radius: 8px;
  cursor: move;
  user-select: none;
  z-index: 1;
}

.workflow-node.selected {
  border-color: #2080f0;
  box-shadow: 0 0 0 2px rgba(32, 128, 240, 0.2);
}

.node-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--n-border-color);
  background: var(--n-hover-color);
}

.node-title {
  flex: 1;
  font-weight: 500;
  font-size: 14px;
}

.node-content {
  padding: 12px;
}

.node-description {
  font-size: 12px;
  color: var(--n-text-color-3);
  margin-bottom: 8px;
}

.node-config {
  display: flex;
  justify-content: flex-end;
}

.node-ports {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 100%;
  pointer-events: none;
}

.port {
  position: absolute;
  width: 12px;
  height: 12px;
  background: #666;
  border-radius: 50%;
  pointer-events: all;
  cursor: pointer;
}

.port-input {
  left: -6px;
}

.port-output {
  right: -6px;
}

.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.editor-panel {
  width: 300px;
  background: var(--n-color);
  border-left: 1px solid var(--n-border-color);
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid var(--n-border-color);
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.panel-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.panel-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--n-text-color-3);
}

.panel-empty p {
  margin-top: 12px;
  font-size: 14px;
}

/* 节点类型样式 */
.node-trigger {
  border-color: #18a058;
}

.node-action {
  border-color: #2080f0;
}

.node-condition {
  border-color: #f0a020;
}

.node-api {
  border-color: #d03050;
}

.node-llm {
  border-color: #8a2be2;
}
</style> 