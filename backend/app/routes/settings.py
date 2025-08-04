"""
设置路由
提供系统配置、通知设置、数据管理等功能
"""

from flask import Blueprint, request, jsonify, send_file
from app.services.database import get_db
from app.utils.auth import token_required
from app.utils.response import ApiResponse, handle_exception, validate_required_fields, sanitize_data
from datetime import datetime, timedelta
from bson import ObjectId
import json
import os

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/system', methods=['GET'])
@token_required
@handle_exception
def get_system_config(current_user):
    """获取系统配置"""
    try:
        db = get_db()
        
        # 从数据库获取用户配置
        user_config = db.users.find_one({'_id': ObjectId(current_user['id'])})
        
        config = {
            'apiBaseUrl': user_config.get('api_base_url', 'http://localhost:5000/api'),
            'ollamaUrl': user_config.get('ollama_url', 'http://localhost:11434'),
            'defaultModel': user_config.get('default_model', 'llama2'),
            'theme': user_config.get('theme', 'light'),
            'language': user_config.get('language', 'zh-CN')
        }
        
        return jsonify(ApiResponse.success(config, "获取系统配置成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@settings_bp.route('/system', methods=['POST'])
@token_required
@handle_exception
def save_system_config(current_user):
    """保存系统配置"""
    try:
        data = request.get_json()
        db = get_db()
        
        # 更新用户配置
        update_data = {}
        if 'apiBaseUrl' in data:
            update_data['api_base_url'] = data['apiBaseUrl']
        if 'ollamaUrl' in data:
            update_data['ollama_url'] = data['ollamaUrl']
        if 'defaultModel' in data:
            update_data['default_model'] = data['defaultModel']
        if 'theme' in data:
            update_data['theme'] = data['theme']
        if 'language' in data:
            update_data['language'] = data['language']
        
        if update_data:
            update_data['updated_at'] = datetime.now()
            db.users.update_one(
                {'_id': ObjectId(current_user['id'])},
                {'$set': update_data}
            )
        
        return jsonify(ApiResponse.success(None, "系统配置保存成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@settings_bp.route('/notifications', methods=['GET'])
@token_required
@handle_exception
def get_notification_settings(current_user):
    """获取通知设置"""
    try:
        db = get_db()
        
        user_config = db.users.find_one({'_id': ObjectId(current_user['id'])})
        
        settings = {
            'emailEnabled': user_config.get('email_notifications', False),
            'emailAddress': user_config.get('email_address', ''),
            'systemNotifications': user_config.get('system_notifications', True),
            'trainingComplete': user_config.get('training_notifications', True),
            'workflowComplete': user_config.get('workflow_notifications', True)
        }
        
        return jsonify(ApiResponse.success(settings, "获取通知设置成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@settings_bp.route('/notifications', methods=['POST'])
@token_required
@handle_exception
def save_notification_settings(current_user):
    """保存通知设置"""
    try:
        data = request.get_json()
        db = get_db()
        
        # 更新通知设置
        update_data = {}
        if 'emailEnabled' in data:
            update_data['email_notifications'] = data['emailEnabled']
        if 'emailAddress' in data:
            update_data['email_address'] = data['emailAddress']
        if 'systemNotifications' in data:
            update_data['system_notifications'] = data['systemNotifications']
        if 'trainingComplete' in data:
            update_data['training_notifications'] = data['trainingComplete']
        if 'workflowComplete' in data:
            update_data['workflow_notifications'] = data['workflowComplete']
        
        if update_data:
            update_data['updated_at'] = datetime.now()
            db.users.update_one(
                {'_id': ObjectId(current_user['id'])},
                {'$set': update_data}
            )
        
        return jsonify(ApiResponse.success(None, "通知设置保存成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@settings_bp.route('/export/<data_type>', methods=['GET'])
@token_required
@handle_exception
def export_data(current_user, data_type):
    """导出数据"""
    try:
        db = get_db()
        
        if data_type not in ['conversations', 'agents', 'workflows', 'plugins']:
            return jsonify(ApiResponse.error('不支持的数据类型')), 400
        
        # 获取数据
        if data_type == 'conversations':
            data = list(db.conversations.find({'user_id': current_user['id']}))
        elif data_type == 'agents':
            data = list(db.agents.find({'user_id': current_user['id']}))
        elif data_type == 'workflows':
            data = list(db.workflows.find({'user_id': current_user['id']}))
        elif data_type == 'plugins':
            data = list(db.plugins.find({'user_id': current_user['id']}))
        
        # 格式化数据
        for item in data:
            item['id'] = str(item['_id'])
            if item.get('created_at'):
                item['created_at'] = item['created_at'].isoformat()
            if item.get('updated_at'):
                item['updated_at'] = item['updated_at'].isoformat()
            del item['_id']
        
        # 创建导出文件
        filename = f"{data_type}_{current_user['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join('output', filename)
        
        os.makedirs('output', exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@settings_bp.route('/clear/<data_type>', methods=['DELETE'])
@token_required
@handle_exception
def clear_data(current_user, data_type):
    """清除数据"""
    try:
        db = get_db()
        
        if data_type not in ['conversations', 'agents', 'workflows', 'plugins']:
            return jsonify(ApiResponse.error('不支持的数据类型')), 400
        
        # 清除数据
        if data_type == 'conversations':
            # 删除对话和相关消息
            conversations = list(db.conversations.find({'user_id': current_user['id']}))
            for conv in conversations:
                db.messages.delete_many({'conversation_id': str(conv['_id'])})
            db.conversations.delete_many({'user_id': current_user['id']})
        elif data_type == 'agents':
            db.agents.delete_many({'user_id': current_user['id']})
        elif data_type == 'workflows':
            db.workflows.delete_many({'user_id': current_user['id']})
        elif data_type == 'plugins':
            db.plugins.delete_many({'user_id': current_user['id']})
        
        return jsonify(ApiResponse.success(None, f"{data_type}数据清除成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@settings_bp.route('/clear/all', methods=['DELETE'])
@token_required
@handle_exception
def clear_all_data(current_user):
    """清除所有数据"""
    try:
        db = get_db()
        
        # 清除所有用户数据
        conversations = list(db.conversations.find({'user_id': current_user['id']}))
        for conv in conversations:
            db.messages.delete_many({'conversation_id': str(conv['_id'])})
        
        db.conversations.delete_many({'user_id': current_user['id']})
        db.agents.delete_many({'user_id': current_user['id']})
        db.workflows.delete_many({'user_id': current_user['id']})
        db.plugins.delete_many({'user_id': current_user['id']})
        db.knowledge_bases.delete_many({'user_id': current_user['id']})
        db.documents.delete_many({'user_id': current_user['id']})
        
        return jsonify(ApiResponse.success(None, "所有数据清除成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@settings_bp.route('/analytics', methods=['GET'])
@token_required
@handle_exception
def get_analytics_data(current_user):
    """获取分析数据"""
    try:
        db = get_db()
        
        # 获取时间范围
        days = int(request.args.get('days', 30))
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 统计对话数据
        conversations_count = db.conversations.count_documents({
            'user_id': current_user['id'],
            'created_at': {'$gte': start_date, '$lte': end_date}
        })
        
        # 统计消息数据
        messages_count = db.messages.count_documents({
            'user_id': current_user['id'],
            'created_at': {'$gte': start_date, '$lte': end_date}
        })
        
        # 统计智能体数据
        agents_count = db.agents.count_documents({
            'user_id': current_user['id'],
            'created_at': {'$gte': start_date, '$lte': end_date}
        })
        
        # 统计工作流数据
        workflows_count = db.workflows.count_documents({
            'user_id': current_user['id'],
            'created_at': {'$gte': start_date, '$lte': end_date}
        })
        
        # 统计插件数据
        plugins_count = db.plugins.count_documents({
            'user_id': current_user['id'],
            'created_at': {'$gte': start_date, '$lte': end_date}
        })
        
        # 统计知识库数据
        knowledge_bases_count = db.knowledge_bases.count_documents({
            'user_id': current_user['id'],
            'created_at': {'$gte': start_date, '$lte': end_date}
        })
        
        # 按日期统计对话
        daily_conversations = []
        current_date = start_date
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            count = db.conversations.count_documents({
                'user_id': current_user['id'],
                'created_at': {'$gte': current_date, '$lt': next_date}
            })
            daily_conversations.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'count': count
            })
            current_date = next_date
        
        # 按日期统计消息
        daily_messages = []
        current_date = start_date
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            count = db.messages.count_documents({
                'user_id': current_user['id'],
                'created_at': {'$gte': current_date, '$lt': next_date}
            })
            daily_messages.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'count': count
            })
            current_date = next_date
        
        analytics_data = {
            'summary': {
                'conversations': conversations_count,
                'messages': messages_count,
                'agents': agents_count,
                'workflows': workflows_count,
                'plugins': plugins_count,
                'knowledge_bases': knowledge_bases_count
            },
            'daily_conversations': daily_conversations,
            'daily_messages': daily_messages,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            }
        }
        
        return jsonify(ApiResponse.success(analytics_data, "获取分析数据成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@settings_bp.route('/table-data', methods=['GET'])
@token_required
@handle_exception
def get_table_data(current_user):
    """获取表格数据"""
    try:
        db = get_db()
        
        # 获取查询参数
        data_type = request.args.get('type', 'conversations')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        search = request.args.get('search', '')
        
        if data_type not in ['conversations', 'agents', 'workflows', 'plugins', 'knowledge_bases']:
            return jsonify(ApiResponse.error('不支持的数据类型')), 400
        
        # 构建查询条件
        query = {'user_id': current_user['id']}
        if search:
            if data_type == 'conversations':
                query['title'] = {'$regex': search, '$options': 'i'}
            elif data_type == 'agents':
                query['name'] = {'$regex': search, '$options': 'i'}
            elif data_type == 'workflows':
                query['name'] = {'$regex': search, '$options': 'i'}
            elif data_type == 'plugins':
                query['name'] = {'$regex': search, '$options': 'i'}
            elif data_type == 'knowledge_bases':
                query['name'] = {'$regex': search, '$options': 'i'}
        
        # 获取数据
        collection = getattr(db, data_type)
        total = collection.count_documents(query)
        
        skip = (page - 1) * limit
        data = list(collection.find(query)
                   .skip(skip)
                   .limit(limit)
                   .sort('created_at', -1))
        
        # 格式化数据
        for item in data:
            item['id'] = str(item['_id'])
            if item.get('created_at'):
                item['created_at'] = item['created_at'].isoformat()
            if item.get('updated_at'):
                item['updated_at'] = item['updated_at'].isoformat()
            del item['_id']
        
        return jsonify(ApiResponse.success({
            'data': data,
            'total': total,
            'page': page,
            'page_size': limit
        }, f"获取{data_type}数据成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400 