// 统一配置文件
export const config = {
  // 后端服务配置
  backend: {
    // 开发环境后端地址
    dev: {
      host: 'localhost',
      port: 3000,
      protocol: 'http'
    },
    // 生产环境后端地址
    prod: {
      host: 'localhost',
      port: 5000,
      protocol: 'http'
    }
  },
  
  // 前端服务配置
  frontend: {
    host: 'localhost',
    port: 5173,
    protocol: 'http'
  },
  
  // API配置
  api: {
    baseURL: '/api',
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json'
    }
  },
  
  // 文件上传配置
  upload: {
    maxSize: 10 * 1024 * 1024, // 10MB
    allowedTypes: [
      '.txt', '.md', '.pdf', '.doc', '.docx',
      '.jpg', '.jpeg', '.png', '.gif'
    ]
  },
  
  // 聊天配置
  chat: {
    streamingTimeout: 60000,
    maxMessageLength: 4000
  }
}

// 获取当前环境的后端地址
export const getBackendURL = () => {
  const isDev = import.meta.env.DEV
  const backend = isDev ? config.backend.dev : config.backend.prod
  return `${backend.protocol}://${backend.host}:${backend.port}`
}

// 获取API完整地址
export const getAPIURL = () => {
  return `${getBackendURL()}${config.api.baseURL}`
}

// 获取WebSocket地址
export const getWebSocketURL = () => {
  const backend = config.backend.dev // 开发环境
  return `${backend.protocol}://${backend.host}:${backend.port}`
}

export default config 