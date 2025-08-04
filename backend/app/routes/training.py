from flask import Blueprint, request, jsonify
from app.models.training import Training
from app.services.database import get_db
import os

training_bp = Blueprint('training', __name__)

# 获取所有训练任务
@training_bp.route('/training', methods=['GET'])
def get_training():
    try:
        if os.environ.get('USE_MOCK_DATA') == 'true':
            # 返回模拟数据
            mock_training = [
                {
                    'id': '1',
                    'name': '客服助手训练',
                    'description': '训练客服助手模型',
                    'type': 'supervised',
                    'status': 'running',
                    'progress': 65,
                    'created_at': '2024-01-15T10:30:00Z',
                    'started_at': '2024-01-15T09:30:00Z',
                    'estimated_completion': '2024-01-15T11:00:00Z',
                    'metrics': {
                        'accuracy': 85.6,
                        'loss': 0.12,
                        'epochs': 15
                    },
                    'logs': 'Epoch 15/20 - Loss: 0.12 - Accuracy: 85.6%'
                },
                {
                    'id': '2',
                    'name': '数据分析师训练',
                    'description': '训练数据分析模型',
                    'type': 'fine_tuning',
                    'status': 'completed',
                    'progress': 100,
                    'created_at': '2024-01-14T10:30:00Z',
                    'started_at': '2024-01-14T09:30:00Z',
                    'estimated_completion': '2024-01-14T11:00:00Z',
                    'metrics': {
                        'accuracy': 92.3,
                        'loss': 0.08,
                        'epochs': 20
                    },
                    'logs': 'Training completed successfully'
                },
                {
                    'id': '3',
                    'name': '任务执行器训练',
                    'description': '训练任务执行模型',
                    'type': 'reinforcement',
                    'status': 'stopped',
                    'progress': 30,
                    'created_at': '2024-01-13T10:30:00Z',
                    'started_at': '2024-01-13T09:30:00Z',
                    'estimated_completion': None,
                    'metrics': {
                        'accuracy': 45.2,
                        'loss': 0.35,
                        'epochs': 8
                    },
                    'logs': 'Training stopped by user'
                }
            ]
            return jsonify({
                'success': True,
                'data': mock_training,
                'message': '获取训练任务列表成功'
            })
        
        db = get_db()
        training = list(db.training.find())
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
def get_training_item(training_id):
    try:
        if os.environ.get('USE_MOCK_DATA') == 'true':
            # 返回模拟数据
            mock_training = {
                'id': training_id,
                'name': '客服助手训练',
                'description': '训练客服助手模型',
                'type': 'supervised',
                'status': 'running',
                'progress': 65,
                'created_at': '2024-01-15T10:30:00Z',
                'started_at': '2024-01-15T09:30:00Z',
                'estimated_completion': '2024-01-15T11:00:00Z',
                'metrics': {
                    'accuracy': 85.6,
                    'loss': 0.12,
                    'epochs': 15
                },
                'logs': 'Epoch 15/20 - Loss: 0.12 - Accuracy: 85.6%',
                'config': {
                    'learning_rate': 0.001,
                    'batch_size': 32,
                    'epochs': 20
                }
            }
            return jsonify({
                'success': True,
                'data': mock_training,
                'message': '获取训练任务详情成功'
            })
        
        db = get_db()
        from bson import ObjectId
        training = db.training.find_one({'_id': ObjectId(training_id)})
        if training:
            training['id'] = str(training['_id'])
            del training['_id']
            return jsonify({
                'success': True,
                'data': training,
                'message': '获取训练任务详情成功'
            })
        else:
            return jsonify({'error': 'Training not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 创建训练任务
@training_bp.route('/training', methods=['POST'])
def create_training():
    try:
        data = request.get_json()
        
        if os.environ.get('USE_MOCK_DATA') == 'true':
            # 返回模拟数据
            new_training = {
                'id': str(len(data) + 1),
                'name': data.get('name'),
                'description': data.get('description'),
                'type': data.get('type'),
                'agent_id': data.get('agent_id'),
                'status': 'pending',
                'progress': 0,
                'created_at': '2024-01-15T10:30:00Z',
                'training_data': data.get('training_data', {}),
                'parameters': data.get('parameters', {})
            }
            return jsonify({
                'success': True,
                'data': new_training,
                'message': '创建训练任务成功'
            }), 201
        
        db = get_db()
        training = Training(**data)
        result = db.training.insert_one(training.to_dict())
        training_data = training.to_dict()
        training_data['id'] = str(result.inserted_id)
        return jsonify({
            'success': True,
            'data': training_data,
            'message': '创建训练任务成功'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 更新训练任务
@training_bp.route('/training/<training_id>', methods=['PUT'])
def update_training(training_id):
    try:
        data = request.get_json()
        
        if os.environ.get('USE_MOCK_DATA') == 'true':
            # 返回模拟数据
            updated_training = {
                'id': training_id,
                'name': data.get('name'),
                'description': data.get('description'),
                'type': data.get('type'),
                'status': data.get('status', 'pending'),
                'updated_at': '2024-01-15T10:30:00Z'
            }
            return jsonify({
                'success': True,
                'data': updated_training,
                'message': '更新训练任务成功'
            })
        
        db = get_db()
        from bson import ObjectId
        result = db.training.update_one(
            {'_id': ObjectId(training_id)},
            {'$set': data}
        )
        if result.modified_count:
            return jsonify({
                'success': True,
                'message': '更新训练任务成功'
            })
        else:
            return jsonify({'error': 'Training not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 删除训练任务
@training_bp.route('/training/<training_id>', methods=['DELETE'])
def delete_training(training_id):
    try:
        if os.environ.get('USE_MOCK_DATA') == 'true':
            # 返回模拟数据
            return jsonify({
                'success': True,
                'message': '删除训练任务成功'
            })
        
        db = get_db()
        from bson import ObjectId
        result = db.training.delete_one({'_id': ObjectId(training_id)})
        if result.deleted_count:
            return jsonify({
                'success': True,
                'message': '删除训练任务成功'
            })
        else:
            return jsonify({'error': 'Training not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 启动训练
@training_bp.route('/training/<training_id>/start', methods=['POST'])
def start_training(training_id):
    try:
        if os.environ.get('USE_MOCK_DATA') == 'true':
            # 返回模拟数据
            return jsonify({
                'success': True,
                'data': {
                    'status': 'running',
                    'started_at': '2024-01-15T10:30:00Z'
                },
                'message': '训练启动成功'
            })
        
        # 这里应该实现启动训练的逻辑
        # 1. 验证训练任务状态
        # 2. 准备训练环境
        # 3. 启动训练进程
        # 4. 更新任务状态
        
        return jsonify({
            'success': True,
            'message': '训练启动成功'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 停止训练
@training_bp.route('/training/<training_id>/stop', methods=['POST'])
def stop_training(training_id):
    try:
        if os.environ.get('USE_MOCK_DATA') == 'true':
            # 返回模拟数据
            return jsonify({
                'success': True,
                'data': {
                    'status': 'stopped',
                    'stopped_at': '2024-01-15T10:30:00Z'
                },
                'message': '训练停止成功'
            })
        
        # 这里应该实现停止训练的逻辑
        # 1. 验证训练任务状态
        # 2. 停止训练进程
        # 3. 保存训练状态
        # 4. 更新任务状态
        
        return jsonify({
            'success': True,
            'message': '训练停止成功'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 获取训练日志
@training_bp.route('/training/<training_id>/logs', methods=['GET'])
def get_training_logs(training_id):
    try:
        if os.environ.get('USE_MOCK_DATA') == 'true':
            # 返回模拟数据
            mock_logs = [
                {'timestamp': '2024-01-15T10:30:00Z', 'level': 'INFO', 'message': 'Training started'},
                {'timestamp': '2024-01-15T10:31:00Z', 'level': 'INFO', 'message': 'Epoch 1/20 - Loss: 0.25 - Accuracy: 45.2%'},
                {'timestamp': '2024-01-15T10:32:00Z', 'level': 'INFO', 'message': 'Epoch 2/20 - Loss: 0.18 - Accuracy: 52.8%'},
                {'timestamp': '2024-01-15T10:33:00Z', 'level': 'INFO', 'message': 'Epoch 3/20 - Loss: 0.15 - Accuracy: 58.9%'}
            ]
            return jsonify(mock_logs)
        
        # 这里应该实现获取训练日志的逻辑
        
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 获取训练指标
@training_bp.route('/training/<training_id>/metrics', methods=['GET'])
def get_training_metrics(training_id):
    try:
        if os.environ.get('USE_MOCK_DATA') == 'true':
            # 返回模拟数据
            mock_metrics = {
                'accuracy': [45.2, 52.8, 58.9, 65.4, 72.1, 78.5, 82.3, 85.6],
                'loss': [0.25, 0.18, 0.15, 0.12, 0.10, 0.08, 0.09, 0.12],
                'epochs': list(range(1, 9))
            }
            return jsonify(mock_metrics)
        
        # 这里应该实现获取训练指标的逻辑
        
        return jsonify({})
    except Exception as e:
        return jsonify({'error': str(e)}), 500 