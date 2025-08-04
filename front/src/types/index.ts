// 通用类型定义

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message: string
}

// 分页参数
export interface PaginationParams {
  page?: number
  page_size?: number
  limit?: number
}

// 分页响应
export interface PaginatedResponse<T = any> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

// 对话类型
export interface Conversation {
  id: string
  user_id: string
  type: 'agent' | 'model' // 对话类型：智能体或模型
  agent_id?: string
  model_id?: string
  title: string
  status: string
  created_at: string
  updated_at: string
  agent_name?: string
  model_name?: string
}

// 消息类型
export interface Message {
  id: string
  conversation_id: string
  content: string
  type: 'user' | 'assistant'
  thinking?: string // 思考过程
  attachments: any[]
  metadata: any
  user_id: string
  created_at: string
}

// 智能体类型
export interface Agent {
  id: string
  name: string
  description: string
  type: string
  status: string
  model_id?: string
  model_name?: string
  config?: any
  created_at: string
  updated_at: string
}

// 知识库类型
export interface Knowledge {
  id: string
  name: string
  description: string
  type: string
  status: boolean
  config?: any
  document_count: number
  created_at: string
  updated_at: string
}

// 工作流类型
export interface Workflow {
  id: string
  name: string
  description: string
  type: string
  status: string
  config?: any
  created_at: string
  updated_at: string
}

// 训练类型
export interface Training {
  id: string
  name: string
  description: string
  type: string
  agent_id: string
  status: string
  progress: number
  training_data?: any
  parameters?: any
  metrics?: any
  logs?: string
  created_at: string
  started_at?: string
  completed_at?: string
}

// 插件类型
export interface Plugin {
  id: string
  name: string
  description: string
  version: string
  author: string
  status: string
  config?: any
  created_at: string
  updated_at: string
}

// 模型类型
export interface Model {
  id: string
  name: string
  description: string
  type: string
  status: string
  provider: string
  parameters?: Record<string, any>
  config?: any
  created_at: string
  updated_at: string
} 