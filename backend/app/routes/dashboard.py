from flask import Blueprint, jsonify, request
from app.services.database import get_db
from app.utils.auth import token_required
from app.utils.response import ApiResponse, handle_exception
from datetime import datetime, timedelta
from bson import ObjectId

dashboard_bp = Blueprint('dashboard', __name__)

# 获取仪表盘统计数据
@dashboard_bp.route('/stats', methods=['GET'])
@token_required
@handle_exception
def get_dashboard_stats(current_user):
    """获取仪表板统计数据"""
    try:
        print(f"📊 获取仪表板统计数据 - 用户: {current_user['username']}")
        
        db = get_db()
        
        # 获取真实统计数据
        total_agents = db.agents.count_documents({'user_id': current_user['id']})
        total_conversations = db.conversations.count_documents({'user_id': current_user['id']})
        total_knowledge_bases = db.knowledge_bases.count_documents({'user_id': current_user['id']})
        total_plugins = db.plugins.count_documents({'user_id': current_user['id']})
        
        # 获取最近7天的对话数量
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_conversations = db.conversations.count_documents({
            'user_id': current_user['id'],
            'created_at': {'$gte': seven_days_ago}
        })
        
        # 获取活跃智能体数量
        active_agents = db.agents.count_documents({
            'user_id': current_user['id'],
            'status': 'active'
        })
        
        stats = {
            'totalAgents': total_agents,
            'totalConversations': total_conversations,
            'totalKnowledge': total_knowledge_bases,
            'totalPlugins': total_plugins,
            'recent_conversations': recent_conversations,
            'active_agents': active_agents
        }
        
        print(f"✅ 统计数据获取成功: {stats}")
        
        return jsonify(ApiResponse.success(stats, "获取统计数据成功"))
        
    except Exception as e:
        print(f"❌ 获取统计数据失败: {str(e)}")
        return jsonify(ApiResponse.error(f"获取统计数据失败: {str(e)}")), 400

# 获取仪表盘分析数据
@dashboard_bp.route('/analytics', methods=['GET'])
@token_required
@handle_exception
def get_dashboard_analytics(current_user):
    """获取仪表板分析数据"""
    try:
        print(f"📈 获取仪表板分析数据 - 用户: {current_user['username']}")
        
        db = get_db()
        
        # 获取时间范围参数
        time_range = request.args.get('time_range', '7d')
        days = 7
        if time_range == '30d':
            days = 30
        elif time_range == '90d':
            days = 90
        elif time_range == '1y':
            days = 365
        
        # 获取指定时间范围内的对话
        start_date = datetime.now() - timedelta(days=days)
        conversations = list(db.conversations.find({
            'user_id': current_user['id'],
            'created_at': {'$gte': start_date}
        }).sort('created_at', 1))
        
        # 按日期分组统计对话趋势
        daily_stats = {}
        for conv in conversations:
            date = conv['created_at'].strftime('%Y-%m-%d')
            if date not in daily_stats:
                daily_stats[date] = 0
            daily_stats[date] += 1
        
        # 生成日期序列
        dates = []
        values = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-1-i)).strftime('%Y-%m-%d')
            dates.append(date)
            values.append(daily_stats.get(date, 0))
        
        # 获取智能体使用统计
        agent_stats = {}
        for conv in conversations:
            if conv.get('agent_id'):
                agent = db.agents.find_one({'_id': conv['agent_id']})
                agent_name = agent['name'] if agent else '未知智能体'
                if agent_name not in agent_stats:
                    agent_stats[agent_name] = 0
                agent_stats[agent_name] += 1
        
        # 转换为图表数据格式
        agent_usage = []
        for name, count in agent_stats.items():
            agent_usage.append({'name': name, 'value': count})
        
        # 获取消息统计
        total_messages = 0
        for conv in conversations:
            total_messages += conv.get('message_count', 0)
        
        # 消息类型分布（模拟数据）
        message_types = [
            {'name': '用户消息', 'value': int(total_messages * 0.6)},
            {'name': 'AI回复', 'value': int(total_messages * 0.4)}
        ]
        
        # 响应时间分析（模拟数据）
        response_times = {
            'ranges': ['0-1s', '1-2s', '2-3s', '3-5s', '5s+'],
            'counts': [45, 30, 15, 8, 2]
        }
        
        analytics = {
            'total_conversations': len(conversations),
            'active_agents': len(agent_stats),
            'total_messages': total_messages,
            'avg_response_time': 2.3,
            'conversation_trend': {
                'dates': dates,
                'values': values
            },
            'agent_usage': agent_usage,
            'message_types': message_types,
            'response_times': response_times,
            'conversations': conversations[:10],  # 最近10个对话
            'agents': list(db.agents.find({'user_id': current_user['id']}).limit(10)),
            'messages': []  # 这里可以添加消息数据
        }
        
        print(f"✅ 分析数据获取成功")
        
        return jsonify(ApiResponse.success(analytics, "获取分析数据成功"))
        
    except Exception as e:
        print(f"❌ 获取分析数据失败: {str(e)}")
        return jsonify(ApiResponse.error(f"获取分析数据失败: {str(e)}")), 400

# 获取最近活动
@dashboard_bp.route('/recent', methods=['GET'])
@token_required
@handle_exception
def get_recent_activities(current_user):
    """获取最近活动"""
    try:
        print(f"📋 获取最近活动 - 用户: {current_user['username']}")
        
        db = get_db()
        
        # 获取最近的对话
        recent_conversations = list(db.conversations.find({
            'user_id': current_user['id']
        }).sort('created_at', -1).limit(5))
        
        # 获取最近的智能体创建
        recent_agents = list(db.agents.find({
            'user_id': current_user['id']
        }).sort('created_at', -1).limit(5))
        
        # 获取最近的知识库更新
        recent_knowledge = list(db.knowledge_bases.find({
            'user_id': current_user['id']
        }).sort('updated_at', -1).limit(5))
        
        # 获取最近的插件安装
        recent_plugins = list(db.plugins.find({
            'user_id': current_user['id']
        }).sort('created_at', -1).limit(5))
        
        # 合并所有活动并按时间排序
        activities = []
        
        for conv in recent_conversations:
            activities.append({
                'id': str(conv['_id']),
                'type': 'conversation',
                'title': '新对话开始',
                'description': f'用户与智能体{conv.get("agent_name", "未知")}开始对话',
                'timestamp': conv['created_at']
            })
        
        for agent in recent_agents:
            activities.append({
                'id': str(agent['_id']),
                'type': 'agent',
                'title': '智能体创建',
                'description': f'创建了新的智能体{agent["name"]}',
                'timestamp': agent['created_at']
            })
        
        for kb in recent_knowledge:
            activities.append({
                'id': str(kb['_id']),
                'type': 'knowledge',
                'title': '知识库更新',
                'description': f'更新了知识库"{kb["name"]}"',
                'timestamp': kb['updated_at']
            })
        
        for plugin in recent_plugins:
            activities.append({
                'id': str(plugin['_id']),
                'type': 'plugin',
                'title': '插件安装',
                'description': f'安装了插件"{plugin["name"]}"',
                'timestamp': plugin['created_at']
            })
        
        # 按时间排序
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        print(f"✅ 最近活动获取成功，共{len(activities)}个活动")
        
        return jsonify(ApiResponse.success(activities, "获取最近活动成功"))
        
    except Exception as e:
        print(f"❌ 获取最近活动失败: {str(e)}")
        return jsonify(ApiResponse.error(f"获取最近活动失败: {str(e)}")), 400

# 获取系统健康状态
@dashboard_bp.route('/health', methods=['GET'])
@token_required
@handle_exception
def get_system_health(current_user):
    """获取系统健康状态"""
    try:
        print(f"🏥 获取系统健康状态 - 用户: {current_user['username']}")
        
        db = get_db()
        
        # 检查数据库连接
        try:
            db.command('ping')
            db_status = 'healthy'
        except Exception as e:
            db_status = 'unhealthy'
            print(f"❌ 数据库健康检查失败: {e}")
        
        # 检查Ollama服务 - 只在用户主动请求时才检查
        ollama_status = 'unknown'  # 默认状态为未知，避免启动时检测
        
        health_status = {
            'database': db_status,
            'ollama': ollama_status,
            'overall': 'healthy' if db_status == 'healthy' and ollama_status == 'healthy' else 'unhealthy'
        }
        
        print(f"✅ 系统健康状态: {health_status}")
        
        return jsonify(ApiResponse.success(health_status, "获取系统健康状态成功"))
        
    except Exception as e:
        print(f"❌ 获取系统健康状态失败: {str(e)}")
        return jsonify(ApiResponse.error(f"获取系统健康状态失败: {str(e)}")), 400

# 检查Ollama服务状态
@dashboard_bp.route('/ollama-health', methods=['GET'])
@token_required
@handle_exception
def check_ollama_health(current_user):
    """检查Ollama服务状态"""
    try:
        print(f"🏥 检查Ollama服务状态 - 用户: {current_user['username']}")
        
        # 获取用户配置中的Ollama地址
        db = get_db()
        default_ollama_url = 'http://localhost:11434'
        
        # 只有在用户ID是有效的ObjectId时才查询数据库
        if current_user['id'] and current_user['id'] != 'dev-user-12345':
            try:
                user_config = db.users.find_one({'_id': ObjectId(current_user['id'])})
                if user_config:
                    default_ollama_url = user_config.get('ollama_url', 'http://localhost:11434')
            except Exception as e:
                print(f"⚠️ 获取用户配置失败: {e}")
                # 使用默认地址
        
        # 获取Ollama服务器地址，优先使用请求参数，否则使用用户配置
        server_url = request.args.get('server_url', default_ollama_url)
        
        from app.services.ollama import OllamaService
        ollama_service = OllamaService(server_url)
        ollama_status = 'healthy' if ollama_service.health_check() else 'unhealthy'
        
        print(f"✅ Ollama服务状态: {ollama_status}")
        
        return jsonify(ApiResponse.success({
            'status': ollama_status,
            'message': 'Ollama服务正常' if ollama_status == 'healthy' else 'Ollama服务不可用'
        }, "Ollama服务状态检查完成"))
        
    except Exception as e:
        print(f"❌ 检查Ollama服务状态失败: {str(e)}")
        return jsonify(ApiResponse.error(f"检查Ollama服务状态失败: {str(e)}")), 400 