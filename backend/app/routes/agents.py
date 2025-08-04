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
        
        db = get_db()
        agents = list(db.agents.find())
        
        # 格式化数据
        for agent in agents:
            agent['id'] = str(agent['_id'])
            agent['created_at'] = agent['created_at'].isoformat() if agent.get('created_at') else None
            agent['updated_at'] = agent['updated_at'].isoformat() if agent.get('updated_at') else None
            
            # 确保所有ObjectId都转换为字符串
            if 'model_id' in agent and isinstance(agent['model_id'], ObjectId):
                agent['model_id'] = str(agent['model_id'])
            
            del agent['_id']
        
        print(f"✅ 获取到 {len(agents)} 个智能体")
        
        # 序列化数据以处理 ObjectId 和 datetime
        serialized_agents = serialize_mongo_data(agents)
        
        return jsonify(ApiResponse.success({
            'data': serialized_agents,
            'total': len(agents),
            'page': 1,
            'page_size': len(agents)
        }, "获取智能体列表成功"))
        
    except Exception as e:
        print(f"❌ 获取智能体列表失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

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
        del agent['_id']
        
        # 序列化数据以处理 ObjectId 和 datetime
        serialized_agent = serialize_mongo_data(agent)
        
        return jsonify(ApiResponse.success(serialized_agent, "获取智能体详情成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

# 创建智能体
@agents_bp.route('', methods=['POST'])
@agents_bp.route('/', methods=['POST'])
@token_required
@handle_exception
def create_agent(current_user):
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['name', 'type']
        validate_required_fields(data, required_fields)
        
        db = get_db()
        
        # 检查名称是否已存在
        existing_agent = db.agents.find_one({'name': data['name']})
        if existing_agent:
            return jsonify(ApiResponse.error('智能体名称已存在')), 400
        
        # 创建智能体数据
        agent_data = {
            'name': data['name'],
            'description': data.get('description', ''),
            'type': data['type'],
            'status': data.get('status', 'active'),
            'model_name': data.get('model_name', 'llama2'),
            'config': data.get('config', {}),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        result = db.agents.insert_one(agent_data)
        agent_data['id'] = str(result.inserted_id)
        
        # 序列化数据以处理 ObjectId 和 datetime
        serialized_agent_data = serialize_mongo_data(agent_data)
        
        return jsonify(ApiResponse.success(serialized_agent_data, "智能体创建成功")), 201
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

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
        
        # 更新数据
        update_data = {
            'updated_at': datetime.now()
        }
        
        allowed_fields = ['name', 'description', 'type', 'status', 'model_name', 'config']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        db.agents.update_one(
            {'_id': ObjectId(agent_id)},
            {'$set': update_data}
        )
        
        return jsonify(ApiResponse.success(None, "智能体更新成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

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
        
        # 删除智能体
        result = db.agents.delete_one({'_id': ObjectId(agent_id)})
        
        return jsonify(ApiResponse.success(None, "智能体删除成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400 