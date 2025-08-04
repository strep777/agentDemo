# Agent Demo

一个基于Vue3 + Flask的智能体管理系统

## 🚀 快速开始

### 后端启动

```bash
cd backend

# 方式1: 使用app.py启动（推荐）
python app.py

# 方式2: 使用开发脚本启动
python start_dev.py

# 方式3: 使用模块方式启动
python -m app
```

**注意**: 已修复启动时的多重输出问题，现在启动更加简洁。

### 前端启动

```bash
cd front
npm install
npm run dev
```

## 🔧 开发环境配置

### 认证配置

开发环境下，系统使用默认token进行认证：
- Token: `dev-token-12345`
- 用户角色: `admin`

### 环境变量

确保以下环境变量已设置：
- `FLASK_ENV=development`
- `FLASK_DEBUG=1`
- `USE_MOCK_DATA=true` (使用模拟数据，避免数据库依赖)

### 端口配置

- 后端服务: `http://localhost:3000`
- 前端服务: `http://localhost:5173`
- 前端代理: `/api` -> `http://localhost:3000/api`

## 🐛 已修复的问题

### 后端修复
1. **Flask应用入口**: 创建了完整的Flask应用配置 (`backend/app/__init__.py`)
2. **数据库服务**: 修复了数据库初始化和模拟数据支持
3. **WebSocket服务**: 修复了WebSocket初始化函数
4. **认证系统**: 完善了开发环境认证绕过机制
5. **聊天路由**: 修复了流式聊天和消息处理
6. **API响应**: 统一了API响应格式和错误处理

### 前端修复
1. **API配置**: 修复了API请求配置和错误处理
2. **代理设置**: 完善了Vite代理配置
3. **Store管理**: 修复了聊天和智能体store
4. **类型定义**: 完善了TypeScript类型定义
5. **路由配置**: 修复了前端路由配置

### 通信修复
1. **HTTP请求**: 修复了所有API端点的HTTP请求
2. **流式响应**: 修复了聊天流式响应处理
3. **错误处理**: 完善了前后端错误处理机制
4. **调试信息**: 添加了详细的调试日志

## 📋 功能特性

- 🤖 **智能体管理**: 创建、编辑、删除智能体
- 💬 **聊天对话**: 实时对话界面，支持流式响应
- 📚 **知识库管理**: 文档上传和处理
- 🔧 **工作流管理**: 自动化工作流定义
- 🔌 **插件系统**: 插件安装和管理
- 🎯 **模型配置**: 多模型提供商支持
- 📊 **数据分析**: 使用统计和分析
- ⚙️ **系统设置**: 系统配置管理

## 🧪 测试

### API测试
```bash
cd backend
python test_api.py
```

### 功能测试
1. 启动后端服务
2. 启动前端服务
3. 访问 `http://localhost:5173`
4. 测试各个功能模块

## 🔍 调试信息

### 后端调试
- 所有API请求都有详细的日志输出
- 错误信息包含完整的堆栈跟踪
- 开发环境支持热重载

### 前端调试
- 浏览器控制台显示详细的API请求信息
- 网络面板可以查看所有HTTP请求
- Vue DevTools支持状态调试

## 📁 项目结构

```
agentDemo/
├── backend/                 # 后端服务
│   ├── app/                # Flask应用
│   │   ├── routes/         # API路由
│   │   ├── services/       # 业务服务
│   │   ├── utils/          # 工具函数
│   │   └── models/         # 数据模型
│   ├── start_dev.py        # 开发启动脚本
│   └── test_api.py         # API测试脚本
├── front/                  # 前端应用
│   ├── src/
│   │   ├── api/           # API接口
│   │   ├── stores/        # 状态管理
│   │   ├── views/         # 页面组件
│   │   ├── types/         # 类型定义
│   │   └── router/        # 路由配置
│   └── vite.config.ts     # Vite配置
└── README.md              # 项目文档
```

## 🚨 常见问题

### 认证问题
如果遇到"未提供有效认证token"错误：
1. 确保使用开发脚本启动后端：`python start_dev.py`
2. 检查前端控制台是否有token相关错误
3. 清除浏览器缓存并重新登录

### 模型配置问题
如果模型创建失败：
1. 检查用户权限（需要admin角色）
2. 确保Ollama服务器正常运行
3. 查看后端日志获取详细错误信息

### 数据库问题
如果遇到数据库连接问题：
1. 系统默认使用模拟数据模式
2. 检查 `USE_MOCK_DATA=true` 环境变量
3. 如需真实数据库，配置MongoDB连接

### 端口冲突
如果遇到端口占用问题：
1. 检查3000端口是否被占用
2. 检查5173端口是否被占用
3. 修改配置文件中的端口设置

## 🛠️ 技术栈

### 前端
- Vue 3 + TypeScript
- Naive UI 组件库
- Pinia 状态管理
- Vite 构建工具
- Axios HTTP客户端

### 后端
- Flask Web框架
- MongoDB 数据库（支持模拟数据）
- SocketIO 实时通信
- JWT 认证机制
- CORS 跨域支持

## 📝 开发说明

### 代码规范
- 使用TypeScript进行类型检查
- 遵循ESLint代码规范
- 使用Prettier格式化代码
- 添加详细的注释和文档

### 提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试相关
- chore: 构建过程或辅助工具的变动

## 📄 许可证

MIT License 