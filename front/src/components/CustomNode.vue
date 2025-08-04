<template>
  <div
    :class="[
      'custom-node',
      `node-${data.type}`,
      selected ? 'selected' : ''
    ]"
  >
    <!-- 节点头部 -->
    <div class="node-header">
      <div class="node-icon">
        <n-icon :component="getNodeIcon(data.type)" />
      </div>
      <div class="node-title">
        {{ data.label || getNodeTitle(data.type) }}
      </div>
      <div class="node-actions">
        <n-button
          type="text"
          size="tiny"
          @click="handleDelete"
        >
          <n-icon><CloseOutline /></n-icon>
        </n-button>
      </div>
    </div>

    <!-- 节点内容 -->
    <div class="node-content">
      <!-- LLM节点 -->
      <div v-if="data.type === 'llm'" class="node-details">
        <div class="detail-item">
          <span class="label">模型:</span>
          <span class="value">{{ data.model || 'llama2' }}</span>
        </div>
        <div class="detail-item">
          <span class="label">温度:</span>
          <span class="value">{{ data.temperature || 0.7 }}</span>
        </div>
      </div>

      <!-- 插件节点 -->
      <div v-else-if="data.type === 'plugin'" class="node-details">
        <div class="detail-item">
          <span class="label">插件:</span>
          <span class="value">{{ getPluginName(data.pluginId) }}</span>
        </div>
      </div>

      <!-- 条件节点 -->
      <div v-else-if="data.type === 'condition'" class="node-details">
        <div class="detail-item">
          <span class="label">条件:</span>
          <span class="value">{{ data.condition || '未设置' }}</span>
        </div>
      </div>

      <!-- 转换节点 -->
      <div v-else-if="data.type === 'transform'" class="node-details">
        <div class="detail-item">
          <span class="label">转换:</span>
          <span class="value">{{ data.transform || '未设置' }}</span>
        </div>
      </div>

      <!-- 知识库节点 -->
      <div v-else-if="data.type === 'knowledge'" class="node-details">
        <div class="detail-item">
          <span class="label">知识库:</span>
          <span class="value">{{ getKnowledgeName(data.knowledgeId) }}</span>
        </div>
        <div class="detail-item">
          <span class="label">相似度:</span>
          <span class="value">{{ data.similarity || 0.8 }}</span>
        </div>
      </div>
    </div>

    <!-- 连接点 -->
    <div class="node-handles">
      <div class="handle handle-top" data-handleid="top" />
      <div class="handle handle-bottom" data-handleid="bottom" />
      <div class="handle handle-left" data-handleid="left" />
      <div class="handle handle-right" data-handleid="right" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  CloseOutline,
  ChatbubbleOutline,
  ExtensionPuzzleOutline,
  GitCompareOutline,
  SwapHorizontalOutline,
  BookOutline
} from '@vicons/ionicons5'
import type { WorkflowNodeData } from '../types'

// Props
const props = defineProps<{
  id: string
  type: string
  data: WorkflowNodeData
  selected: boolean
}>()

// 方法
const getNodeIcon = (type: string) => {
  const iconMap: Record<string, any> = {
    llm: ChatbubbleOutline,
    plugin: ExtensionPuzzleOutline,
    condition: GitCompareOutline,
    transform: SwapHorizontalOutline,
    knowledge: BookOutline
  }
  return iconMap[type] || ChatbubbleOutline
}

const getNodeTitle = (type: string) => {
  const titleMap: Record<string, string> = {
    llm: 'LLM节点',
    plugin: '插件节点',
    condition: '条件节点',
    transform: '转换节点',
    knowledge: '知识库节点'
  }
  return titleMap[type] || '未知节点'
}

const getPluginName = (pluginId: string) => {
  const pluginMap: Record<string, string> = {
    http_plugin: 'HTTP请求插件',
    file_plugin: '文件处理插件',
    data_plugin: '数据分析插件'
  }
  return pluginMap[pluginId] || '未知插件'
}

const getKnowledgeName = (knowledgeId: string) => {
  const knowledgeMap: Record<string, string> = {
    tech_docs: '技术文档库',
    product_docs: '产品手册库',
    faq_docs: 'FAQ库'
  }
  return knowledgeMap[knowledgeId] || '未知知识库'
}

const handleDelete = () => {
  // message.success('节点删除功能') // Removed as per edit hint
}
</script>

<style scoped>
.custom-node {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  min-width: 150px;
  position: relative;
  transition: all 0.2s ease;
}

.custom-node:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.custom-node.selected {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.node-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.node-icon {
  color: #6b7280;
  font-size: 16px;
}

.node-title {
  font-weight: 600;
  font-size: 14px;
  color: #374151;
  flex: 1;
}

.node-actions {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.custom-node:hover .node-actions {
  opacity: 1;
}

.node-content {
  margin-bottom: 8px;
}

.node-details {
  font-size: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.detail-item .label {
  color: #6b7280;
}

.detail-item .value {
  color: #374151;
  font-weight: 500;
}

.node-handles {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: none;
}

.handle {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border: 2px solid white;
  border-radius: 50%;
  pointer-events: all;
  cursor: crosshair;
}

.handle-top {
  top: -4px;
  left: 50%;
  transform: translateX(-50%);
}

.handle-bottom {
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
}

.handle-left {
  left: -4px;
  top: 50%;
  transform: translateY(-50%);
}

.handle-right {
  right: -4px;
  top: 50%;
  transform: translateY(-50%);
}

/* 节点类型特定样式 */
.node-llm {
  border-color: #10b981;
}

.node-llm .node-icon {
  color: #10b981;
}

.node-plugin {
  border-color: #f59e0b;
}

.node-plugin .node-icon {
  color: #f59e0b;
}

.node-condition {
  border-color: #8b5cf6;
}

.node-condition .node-icon {
  color: #8b5cf6;
}

.node-transform {
  border-color: #06b6d4;
}

.node-transform .node-icon {
  color: #06b6d4;
}

.node-knowledge {
  border-color: #ef4444;
}

.node-knowledge .node-icon {
  color: #ef4444;
}
</style> 