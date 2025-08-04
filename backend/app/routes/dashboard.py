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
            'total_agents': total_agents,
            'total_conversations': total_conversations,
            'total_knowledge_bases': total_knowledge_bases,
            'total_plugins': total_plugins,
            'recent_conversations': recent_conversations,
            'active_agents': active_agents
        }
        
        print(f"✅ 统计数据获取成功: {stats}")
        
        return jsonify(ApiResponse.success({
            'data': stats
        }, "获取统计数据成功"))
        
    except Exception as e:
        print(f"❌ 获取统计数据失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

# 获取仪表盘分析数据
@dashboard_bp.route('/analytics', methods=['GET'])
@token_required
@handle_exception
def get_dashboard_analytics(current_user):
    """获取仪表板分析数据"""
    try:
        print(f"📈 获取仪表板分析数据 - 用户: {current_user['username']}")
        
        db = get_db()
        
        # 获取最近30天的对话趋势
        thirty_days_ago = datetime.now() - timedelta(days=30)
        conversations = list(db.conversations.find({
            'user_id': current_user['id'],
            'created_at': {'$gte': thirty_days_ago}
        }).sort('created_at', 1))
        
        # 按日期分组统计
        daily_stats = {}
        for conv in conversations:
            date = conv['created_at'].strftime('%Y-%m-%d')
            if date not in daily_stats:
                daily_stats[date] = 0
            daily_stats[date] += 1
        
        # 获取智能体使用统计
        agent_stats = {}
        for conv in conversations:
            if conv.get('agent_id'):
                agent = db.agents.find_one({'_id': conv['agent_id']})
                agent_name = agent['name'] if agent else '未知智能体'
                if agent_name not in agent_stats:
                    agent_stats[agent_name] = 0
                agent_stats[agent_name] += 1
        
        analytics = {
            'daily_conversations': daily_stats,
            'agent_usage': agent_stats,
            'total_conversations': len(conversations)
        }
        
        print(f"✅ 分析数据获取成功")
        
        return jsonify(ApiResponse.success({
            'data': analytics
        }, "获取分析数据成功"))
        
    except Exception as e:
        print(f"❌ 获取分析数据失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

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
        
        return jsonify(ApiResponse.success({
            'data': health_status
        }, "获取系统健康状态成功"))
        
    except Exception as e:
        print(f"❌ 获取系统健康状态失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

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
        return jsonify(ApiResponse.error(str(e))), 400 