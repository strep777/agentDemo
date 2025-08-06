// 智能体类型
export type AgentType = 'chat' | 'assistant' | 'specialist' | 'creative'

// 智能体状态
export type AgentStatus = 'active' | 'inactive'

// 智能体配置
export interface AgentConfig {
  temperature?: number
  max_tokens?: number
  top_p?: number
  frequency_penalty?: number
  presence_penalty?: number
  system_prompt?: string
  plugins?: string[]
  knowledge_bases?: string[]
  [key: string]: any
}

// 智能体模型
export interface Agent {
  id: string
  name: string
  description: string
  type: AgentType
  model_name: string
  status: AgentStatus
  config?: AgentConfig
  knowledge_base_ids?: string[]
  plugin_ids?: string[]
  created_at: string
  updated_at: string
}

// 智能体创建参数
export interface CreateAgentParams {
  name: string
  description: string
  type: AgentType
  model_name: string
  status?: AgentStatus
  config?: AgentConfig
  knowledge_base_ids?: string[]
  plugin_ids?: string[]
}

// 智能体更新参数
export interface UpdateAgentParams extends Partial<CreateAgentParams> {}

// 智能体列表查询参数
export interface AgentListParams {
  page?: number
  limit?: number
  search?: string
  status?: string
  type?: string
}

// 智能体列表响应
export interface AgentListResponse {
  agents: Agent[]
  total: number
  page: number
  limit: number
  pages: number
}

// 智能体类型选项
export interface AgentTypeOption {
  value: AgentType
  label: string
  description: string
}

// 智能体统计
export interface AgentStats {
  total: number
  active: number
  inactive: number
  type_stats: Array<{
    _id: string
    count: number
  }>
  model_stats: Array<{
    _id: string
    count: number
  }>
}

// 智能体对话记录
export interface AgentConversation {
  id: string
  title: string
  message_count: number
  created_at: string
  updated_at: string
}

// 智能体训练记录
export interface AgentTrainingRecord {
  id: string
  training_id: string
  status: 'running' | 'completed' | 'failed' | 'cancelled' | 'paused'
  progress: number
  current_epoch?: number
  total_epochs?: number
  start_time: string
  end_time?: string
  config: any
  model_path?: string
  error?: string
  created_at: string
}

// 智能体评估结果
export interface AgentEvaluation {
  agent_id: string
  total_questions: number
  correct_answers: number
  accuracy: number
  score: number
}

// 智能体模型
export interface AgentModel {
  id: string
  name: string
  description: string
  type: string
  agent_id: string
  training_id: string
  model_path: string
  config: any
  status: string
  created_at: string
} 