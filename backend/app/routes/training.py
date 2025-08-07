from flask import Blueprint, request, jsonify
from app.models.training import Training
from app.services.database import get_db
from app.utils.auth import token_required
from app.utils.response import ApiResponse, handle_exception, validate_required_fields
from datetime import datetime
import os

training_bp = Blueprint('training', __name__)

# 获取所有训练任务
@training_bp.route('/training', methods=['GET'])
@token_required
@handle_exception
def get_training(current_user):
    try:
        db = get_db()
        training = list(db.training.find({'user_id': current_user['id']}))
        # 转换ObjectId为字符串
        for item in training:
            item['id'] = str(item['_id'])
            del item['_id']
        return jsonify({
            'success': True,
            'data': training,
            'message': '获取训练任务列表成功'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 获取单个训练任务
@training_bp.route('/training/<training_id>', methods=['GET'])
@token_required
@handle_exception
def get_training_item(current_user, training_id):
    try:
        db = get_db()
        from bson import ObjectId
        
        # 验证ID格式
        if not ObjectId.is_valid(training_id):
            return jsonify(ApiResponse.error('无效的训练任务ID')), 400
        
        training = db.training.find_one({
            '_id': ObjectId(training_id),
            'user_id': current_user['id']
        })
        
        if training:
            training['id'] = str(training['_id'])
            del training['_id']
            return jsonify(ApiResponse.success(training, '获取训练任务详情成功'))
        else:
            return jsonify(ApiResponse.error('训练任务不存在')), 404
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 500

# 创建训练任务
@training_bp.route('/training', methods=['POST'])
@token_required
@handle_exception
def create_training(current_user):
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['name', 'type', 'agent_id']
        validate_required_fields(data, required_fields)
        
        # 添加用户ID和时间戳
        data['user_id'] = current_user['id']
        data['status'] = 'pending'
        data['progress'] = 0
        data['created_at'] = datetime.utcnow()
        
        db = get_db()
        result = db.training.insert_one(data)
        data['id'] = str(result.inserted_id)
        
        return jsonify(ApiResponse.success(data, '创建训练任务成功')), 201
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 500

# 更新训练任务
@training_bp.route('/training/<training_id>', methods=['PUT'])
@token_required
@handle_exception
def update_training(current_user, training_id):
    try:
        data = request.get_json()
        
        # 验证ID格式
        from bson import ObjectId
        if not ObjectId.is_valid(training_id):
            return jsonify(ApiResponse.error('无效的训练任务ID')), 400
        
        # 添加更新时间戳
        data['updated_at'] = datetime.utcnow()
        
        db = get_db()
        result = db.training.update_one(
            {
                '_id': ObjectId(training_id),
                'user_id': current_user['id']
            },
            {'$set': data}
        )
        
        if result.modified_count:
            return jsonify(ApiResponse.success(None, '更新训练任务成功'))
        else:
            return jsonify(ApiResponse.error('训练任务不存在')), 404
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 500

# 删除训练任务
@training_bp.route('/training/<training_id>', methods=['DELETE'])
@token_required
@handle_exception
def delete_training(current_user, training_id):
    try:
        # 验证ID格式
        from bson import ObjectId
        if not ObjectId.is_valid(training_id):
            return jsonify(ApiResponse.error('无效的训练任务ID')), 400
        
        db = get_db()
        result = db.training.delete_one({
            '_id': ObjectId(training_id),
            'user_id': current_user['id']
        })
        
        if result.deleted_count:
            return jsonify(ApiResponse.success(None, '删除训练任务成功'))
        else:
            return jsonify(ApiResponse.error('训练任务不存在')), 404
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 500

# 启动训练
@training_bp.route('/training/<training_id>/start', methods=['POST'])
@token_required
@handle_exception
def start_training(current_user, training_id):
    try:
        # 验证ID格式
        from bson import ObjectId
        if not ObjectId.is_valid(training_id):
            return jsonify(ApiResponse.error('无效的训练任务ID')), 400
        
        db = get_db()
        
        # 检查训练任务是否存在且属于当前用户
        training = db.training.find_one({
            '_id': ObjectId(training_id),
            'user_id': current_user['id']
        })
        
        if not training:
            return jsonify(ApiResponse.error('训练任务不存在')), 404
        
        # 检查训练任务状态
        if training['status'] == 'running':
            return jsonify(ApiResponse.error('训练任务已在运行中')), 400
        
        # 更新训练任务状态
        update_data = {
            'status': 'running',
            'started_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = db.training.update_one(
            {'_id': ObjectId(training_id)},
            {'$set': update_data}
        )
        
        if result.modified_count:
            return jsonify(ApiResponse.success(update_data, '训练启动成功'))
        else:
            return jsonify(ApiResponse.error('启动训练失败')), 500
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 500

# 停止训练
@training_bp.route('/training/<training_id>/stop', methods=['POST'])
@token_required
@handle_exception
def stop_training(current_user, training_id):
    try:
        # 验证ID格式
        from bson import ObjectId
        if not ObjectId.is_valid(training_id):
            return jsonify(ApiResponse.error('无效的训练任务ID')), 400
        
        db = get_db()
        
        # 检查训练任务是否存在且属于当前用户
        training = db.training.find_one({
            '_id': ObjectId(training_id),
            'user_id': current_user['id']
        })
        
        if not training:
            return jsonify(ApiResponse.error('训练任务不存在')), 404
        
        # 检查训练任务状态
        if training['status'] != 'running':
            return jsonify(ApiResponse.error('训练任务未在运行中')), 400
        
        # 更新训练任务状态
        update_data = {
            'status': 'stopped',
            'stopped_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = db.training.update_one(
            {'_id': ObjectId(training_id)},
            {'$set': update_data}
        )
        
        if result.modified_count:
            return jsonify(ApiResponse.success(update_data, '训练停止成功'))
        else:
            return jsonify(ApiResponse.error('停止训练失败')), 500
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 500

# 获取训练日志
@training_bp.route('/training/<training_id>/logs', methods=['GET'])
@token_required
@handle_exception
def get_training_logs(current_user, training_id):
    try:
        # 验证ID格式
        from bson import ObjectId
        if not ObjectId.is_valid(training_id):
            return jsonify(ApiResponse.error('无效的训练任务ID')), 400
        
        db = get_db()
        
        # 检查训练任务是否存在且属于当前用户
        training = db.training.find_one({
            '_id': ObjectId(training_id),
            'user_id': current_user['id']
        })
        
        if not training:
            return jsonify(ApiResponse.error('训练任务不存在')), 404
        
        # 获取训练日志（这里可以根据实际需求实现）
        logs = training.get('logs', [])
        
        return jsonify(ApiResponse.success(logs, '获取训练日志成功'))
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 500

# 获取训练指标
@training_bp.route('/training/<training_id>/metrics', methods=['GET'])
@token_required
@handle_exception
def get_training_metrics(current_user, training_id):
    try:
        # 验证ID格式
        from bson import ObjectId
        if not ObjectId.is_valid(training_id):
            return jsonify(ApiResponse.error('无效的训练任务ID')), 400
        
        db = get_db()
        
        # 检查训练任务是否存在且属于当前用户
        training = db.training.find_one({
            '_id': ObjectId(training_id),
            'user_id': current_user['id']
        })
        
        if not training:
            return jsonify(ApiResponse.error('训练任务不存在')), 404
        
        # 获取训练指标（这里可以根据实际需求实现）
        metrics = training.get('metrics', {})
        
        return jsonify(ApiResponse.success(metrics, '获取训练指标成功'))
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 500 