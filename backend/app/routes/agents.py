from flask import Blueprint, request, jsonify
from app.models.agent import Agent
from app.services.database import get_db
from app.utils.auth import token_required
from app.utils.response import ApiResponse, handle_exception, validate_required_fields, serialize_mongo_data
from bson import ObjectId
from datetime import datetime
import os

agents_bp = Blueprint('agents', __name__)

# 获取所有智能体
@agents_bp.route('', methods=['GET'])
@agents_bp.route('/', methods=['GET'])
@token_required
@handle_exception
def get_agents(current_user):
    try:
        print(f"🔍 获取智能体列表 - 用户: {current_user['username']}")
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        search = request.args.get('search', '')
        status_filter = request.args.get('status', '')
        type_filter = request.args.get('type', '')
        
        db = get_db()
        
        # 构建查询条件
        query = {}
        
        if search:
            query['$or'] = [
                {'name': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}}
            ]
        
        if status_filter:
            query['status'] = status_filter
        
        if type_filter:
            query['type'] = type_filter
        
        # 计算总数
        total = db.agents.count_documents(query)
        
        # 获取分页数据
        skip = (page - 1) * page_size
        agents = list(db.agents.find(query).skip(skip).limit(page_size))
        
        # 格式化数据
        for agent in agents:
            agent['id'] = str(agent['_id'])
            agent['created_at'] = agent['created_at'].isoformat() if agent.get('created_at') else None
            agent['updated_at'] = agent['updated_at'].isoformat() if agent.get('updated_at') else None
            
            # 确保所有ObjectId都转换为字符串
            if 'model_id' in agent and isinstance(agent['model_id'], ObjectId):
                agent['model_id'] = str(agent['model_id'])
            
            # 确保状态字段是字符串
            if 'status' in agent:
                if isinstance(agent['status'], bool):
                    agent['status'] = 'active' if agent['status'] else 'inactive'
                elif agent['status'] not in ['active', 'inactive']:
                    agent['status'] = 'active'
            
            # 确保model_name字段存在
            if 'model_name' not in agent and 'model' in agent:
                agent['model_name'] = agent['model']
            elif 'model_name' not in agent:
                agent['model_name'] = 'llama2'
            
            # 确保type字段是有效的AgentType
            if 'type' in agent and agent['type'] not in ['chat', 'assistant', 'specialist', 'creative']:
                agent['type'] = 'chat'  # 默认类型
            
            del agent['_id']
        
        print(f"✅ 获取到 {len(agents)} 个智能体")
        
        # 序列化数据以处理 ObjectId 和 datetime
        serialized_agents = serialize_mongo_data(agents)
        
        return jsonify(ApiResponse.success({
            'data': serialized_agents,
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size
        }, "获取智能体列表成功"))
        
    except Exception as e:
        print(f"❌ 获取智能体列表失败: {str(e)}")
        return jsonify(ApiResponse.error(f"获取智能体列表失败: {str(e)}")), 400

# 获取单个智能体
@agents_bp.route('/<agent_id>', methods=['GET'])
@token_required
@handle_exception
def get_agent(current_user, agent_id):
    try:
        # 验证ID格式
        if not ObjectId.is_valid(agent_id):
            return jsonify(ApiResponse.error('无效的智能体ID')), 400
        
        db = get_db()
        agent = db.agents.find_one({'_id': ObjectId(agent_id)})
        
        if not agent:
            return jsonify(ApiResponse.error('智能体不存在')), 404
        
        # 格式化数据
        agent['id'] = str(agent['_id'])
        agent['created_at'] = agent['created_at'].isoformat() if agent.get('created_at') else None
        agent['updated_at'] = agent['updated_at'].isoformat() if agent.get('updated_at') else None
        
        # 确保状态字段是字符串
        if 'status' in agent:
            if isinstance(agent['status'], bool):
                agent['status'] = 'active' if agent['status'] else 'inactive'
            elif agent['status'] not in ['active', 'inactive']:
                agent['status'] = 'active'
        
        # 确保model_name字段存在
        if 'model_name' not in agent and 'model' in agent:
            agent['model_name'] = agent['model']
        elif 'model_name' not in agent:
            agent['model_name'] = 'llama2'
        
        # 确保type字段是有效的AgentType
        if 'type' in agent and agent['type'] not in ['chat', 'assistant', 'specialist', 'creative']:
            agent['type'] = 'chat'  # 默认类型
        
        del agent['_id']
        
        # 序列化数据以处理 ObjectId 和 datetime
        serialized_agent = serialize_mongo_data(agent)
        
        return jsonify(ApiResponse.success(serialized_agent, "获取智能体详情成功"))
        
    except Exception as e:
        print(f"❌ 获取智能体详情失败: {str(e)}")
        return jsonify(ApiResponse.error(f"获取智能体详情失败: {str(e)}")), 400

# 创建智能体
@agents_bp.route('', methods=['POST'])
@agents_bp.route('/', methods=['POST'])
@token_required
@handle_exception
def create_agent(current_user):
    try:
        data = request.get_json()
        print(f"📝 创建智能体数据: {data}")
        
        # 验证必需字段
        required_fields = ['name', 'type']
        validate_required_fields(data, required_fields)
        
        db = get_db()
        
        # 检查名称是否已存在
        existing_agent = db.agents.find_one({'name': data['name']})
        if existing_agent:
            return jsonify(ApiResponse.error('智能体名称已存在')), 400
        
        # 处理状态字段
        status = data.get('status', 'active')
        if isinstance(status, bool):
            status = 'active' if status else 'inactive'
        elif status not in ['active', 'inactive']:
            status = 'active'
        
        # 处理模型名称
        model_name = data.get('model_name', 'llama2')
        if 'model' in data and not model_name:
            model_name = data['model']
        
        # 创建智能体数据
        agent_data = {
            'name': data['name'],
            'description': data.get('description', ''),
            'type': data['type'],
            'status': status,
            'model_name': model_name,
            'config': data.get('config', {}),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        print(f"💾 保存智能体数据: {agent_data}")
        
        result = db.agents.insert_one(agent_data)
        agent_data['id'] = str(result.inserted_id)
        
        # 格式化时间
        agent_data['created_at'] = agent_data['created_at'].isoformat()
        agent_data['updated_at'] = agent_data['updated_at'].isoformat()
        
        print(f"✅ 智能体创建成功: {agent_data['name']}")
        
        # 序列化数据以处理 ObjectId 和 datetime
        serialized_agent_data = serialize_mongo_data(agent_data)
        
        return jsonify(ApiResponse.success(serialized_agent_data, "智能体创建成功")), 201
        
    except Exception as e:
        print(f"❌ 创建智能体失败: {str(e)}")
        return jsonify(ApiResponse.error(f"创建智能体失败: {str(e)}")), 400

# 更新智能体
@agents_bp.route('/<agent_id>', methods=['PUT'])
@token_required
@handle_exception
def update_agent(current_user, agent_id):
    try:
        # 验证ID格式
        if not ObjectId.is_valid(agent_id):
            return jsonify(ApiResponse.error('无效的智能体ID')), 400
        
        data = request.get_json()
        print(f"📝 更新智能体数据: {data}")
        
        db = get_db()
        
        # 检查智能体是否存在
        agent = db.agents.find_one({'_id': ObjectId(agent_id)})
        if not agent:
            return jsonify(ApiResponse.error('智能体不存在')), 404
        
        # 检查名称是否重复
        if 'name' in data and data['name'] != agent['name']:
            existing_agent = db.agents.find_one({
                'name': data['name'],
                '_id': {'$ne': ObjectId(agent_id)}
            })
            if existing_agent:
                return jsonify(ApiResponse.error('智能体名称已存在')), 400
        
        # 处理状态字段
        status = data.get('status', agent.get('status', 'active'))
        if isinstance(status, bool):
            status = 'active' if status else 'inactive'
        elif isinstance(status, str) and status not in ['active', 'inactive']:
            status = 'active'
        else:
            status = 'active'
        
        print(f"🔄 智能体状态更新: {agent.get('status', 'unknown')} -> {status}")
        
        # 处理模型名称
        model_name = data.get('model_name', agent.get('model_name', 'llama2'))
        if 'model' in data and not model_name:
            model_name = data['model']
        
        # 更新数据
        update_data = {
            'updated_at': datetime.now()
        }
        
        # 处理其他字段
        allowed_fields = ['name', 'description', 'type', 'model_name', 'config']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        # 处理状态字段
        if 'status' in data:
            update_data['status'] = status
        
        print(f"💾 更新智能体数据: {update_data}")
        
        db.agents.update_one(
            {'_id': ObjectId(agent_id)},
            {'$set': update_data}
        )
        
        print(f"✅ 智能体更新成功: {agent_id}")
        
        return jsonify(ApiResponse.success(None, "智能体更新成功"))
        
    except Exception as e:
        print(f"❌ 更新智能体失败: {str(e)}")
        return jsonify(ApiResponse.error(f"更新智能体失败: {str(e)}")), 400

# 删除智能体
@agents_bp.route('/<agent_id>', methods=['DELETE'])
@token_required
@handle_exception
def delete_agent(current_user, agent_id):
    try:
        # 验证ID格式
        if not ObjectId.is_valid(agent_id):
            return jsonify(ApiResponse.error('无效的智能体ID')), 400
        
        db = get_db()
        
        # 检查智能体是否存在
        agent = db.agents.find_one({'_id': ObjectId(agent_id)})
        if not agent:
            return jsonify(ApiResponse.error('智能体不存在')), 404
        
        print(f"🗑️ 删除智能体: {agent.get('name', '未知')}")
        
        # 删除智能体
        result = db.agents.delete_one({'_id': ObjectId(agent_id)})
        
        print(f"✅ 智能体删除成功: {agent_id}")
        
        return jsonify(ApiResponse.success(None, "智能体删除成功"))
        
    except Exception as e:
        print(f"❌ 删除智能体失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

# 获取智能体统计信息
@agents_bp.route('/<agent_id>/stats', methods=['GET'])
@token_required
@handle_exception
def get_agent_stats(current_user, agent_id):
    try:
        # 验证ID格式
        if not ObjectId.is_valid(agent_id):
            return jsonify(ApiResponse.error('无效的智能体ID')), 400
        
        db = get_db()
        
        # 检查智能体是否存在
        agent = db.agents.find_one({'_id': ObjectId(agent_id)})
        if not agent:
            return jsonify(ApiResponse.error('智能体不存在')), 404
        
        # 获取智能体相关的对话统计
        conversations_count = db.conversations.count_documents({
            'agent_id': ObjectId(agent_id)
        })
        
        # 获取消息统计
        messages_count = db.messages.count_documents({
            'conversation_id': {'$in': list(db.conversations.find({'agent_id': ObjectId(agent_id)}, {'_id': 1}))}
        })
        
        # 模拟统计数据
        stats = {
            'total_conversations': conversations_count,
            'total_messages': messages_count,
            'total_tokens': messages_count * 100,  # 模拟令牌数
            'total_time': conversations_count * 60  # 模拟用时（秒）
        }
        
        return jsonify(ApiResponse.success(stats, "获取智能体统计成功"))
        
    except Exception as e:
        print(f"❌ 获取智能体统计失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

# 获取智能体对话历史
@agents_bp.route('/<agent_id>/conversations', methods=['GET'])
@token_required
@handle_exception
def get_agent_conversations(current_user, agent_id):
    try:
        # 验证ID格式
        if not ObjectId.is_valid(agent_id):
            return jsonify(ApiResponse.error('无效的智能体ID')), 400
        
        db = get_db()
        
        # 检查智能体是否存在
        agent = db.agents.find_one({'_id': ObjectId(agent_id)})
        if not agent:
            return jsonify(ApiResponse.error('智能体不存在')), 404
        
        # 获取智能体相关的对话
        conversations = list(db.conversations.find({
            'agent_id': ObjectId(agent_id)
        }).sort('updated_at', -1).limit(10))
        
        # 格式化对话数据
        for conv in conversations:
            conv['id'] = str(conv['_id'])
            conv['created_at'] = conv['created_at'].isoformat() if conv.get('created_at') else None
            conv['updated_at'] = conv['updated_at'].isoformat() if conv.get('updated_at') else None
            
            # 获取消息数量
            conv['message_count'] = db.messages.count_documents({
                'conversation_id': conv['_id']
            })
            
            del conv['_id']
        
        return jsonify(ApiResponse.success(conversations, "获取智能体对话历史成功"))
        
    except Exception as e:
        print(f"❌ 获取智能体对话历史失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400 