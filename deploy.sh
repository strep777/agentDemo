#!/bin/bash

# AI智能体管理系统快速部署脚本

set -e

echo "🤖 AI智能体管理系统部署脚本"
echo "================================"

# 检查Docker和Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

echo "✅ Docker环境检查通过"

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p uploads
mkdir -p logs

# 创建环境配置文件
if [ ! -f .env ]; then
    echo "📝 创建环境配置文件..."
    cat > .env << EOF
# AI智能体管理系统环境配置
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=True
MONGO_URI=mongodb://root:qwbt123@mongodb:27017/
DB_NAME=agent_system
OLLAMA_BASE_URL=http://ollama:11434
EOF
    echo "✅ 环境配置文件已创建"
fi

# 创建MongoDB初始化脚本
if [ ! -f init-mongo.js ]; then
    echo "📝 创建MongoDB初始化脚本..."
    cat > init-mongo.js << EOF
// MongoDB初始化脚本
db = db.getSiblingDB('agent_system');

// 创建用户
db.createUser({
    user: 'agent_user',
    pwd: 'agent_password',
    roles: [
        {
            role: 'readWrite',
            db: 'agent_system'
        }
    ]
});

// 创建集合
db.createCollection('users');
db.createCollection('agents');
db.createCollection('conversations');
db.createCollection('plugins');
db.createCollection('workflows');
db.createCollection('models');

print('MongoDB初始化完成');
EOF
    echo "✅ MongoDB初始化脚本已创建"
fi

# 创建Nginx配置文件
if [ ! -f nginx.conf ]; then
    echo "📝 创建Nginx配置文件..."
    cat > nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:5000;
    }

    upstream frontend {
        server frontend:5173;
    }

    server {
        listen 80;
        server_name localhost;

        # 前端静态文件
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # 后端API
        location /api {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # WebSocket支持
        location /socket.io {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
}
EOF
    echo "✅ Nginx配置文件已创建"
fi

# 构建和启动服务
echo "🚀 构建和启动服务..."

# 选择部署模式
echo "请选择部署模式："
echo "1) 基础模式 (MongoDB + Backend + Frontend)"
echo "2) 完整模式 (包含Ollama)"
echo "3) 生产模式 (包含Nginx代理)"
read -p "请输入选择 (1-3): " choice

case $choice in
    1)
        echo "📦 启动基础模式..."
        docker-compose up -d mongodb backend frontend
        ;;
    2)
        echo "📦 启动完整模式..."
        docker-compose --profile ollama up -d
        ;;
    3)
        echo "📦 启动生产模式..."
        docker-compose --profile ollama --profile proxy up -d
        ;;
    *)
        echo "❌ 无效选择，使用基础模式"
        docker-compose up -d mongodb backend frontend
        ;;
esac

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 显示访问信息
echo ""
echo "🎉 部署完成！"
echo "================================"
echo "📱 前端地址: http://localhost:5173"
echo "🔧 后端地址: http://localhost:5000"
echo "📊 API健康检查: http://localhost:5000/api/health"
echo "🗄️  MongoDB: localhost:27017"
echo ""
echo "📋 常用命令："
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo "  更新服务: docker-compose pull && docker-compose up -d"
echo ""

# 检查服务健康状态
echo "🔍 检查服务健康状态..."
if curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "✅ 后端服务运行正常"
else
    echo "⚠️  后端服务可能未完全启动，请稍等片刻"
fi

if curl -f http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ 前端服务运行正常"
else
    echo "⚠️  前端服务可能未完全启动，请稍等片刻"
fi

echo ""
echo "🎯 现在可以访问 http://localhost:5173 开始使用系统！" 