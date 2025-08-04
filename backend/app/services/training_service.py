import os
import json
import threading
import time
from datetime import datetime
from bson import ObjectId
from app.services.database import get_db

class TrainingService:
    def __init__(self):
        self.db = None
        self.output_dir = os.path.join(os.getcwd(), 'backend', 'output')
        os.makedirs(self.output_dir, exist_ok=True)
        self._running_tasks = {}

    def set_db(self, db):
        self.db = db

    def start_training(self, agent_id, config, user_id):
        """启动训练任务"""
        try:
            training_data = {
                'agent_id': agent_id,
                'user_id': user_id,
                'config': config,
                'status': 'running',
                'progress': 0,
                'current_epoch': 0,
                'metrics': {},
                'start_time': datetime.now(),
                'end_time': None,
                'error_message': '',
                'output_file': '',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            result = self.db.training_history.insert_one(training_data)
            training_id = str(result.inserted_id)
            # 启动异步训练线程
            thread = threading.Thread(target=self._train_task, args=(training_id, agent_id, config, user_id))
            thread.daemon = True
            thread.start()
            self._running_tasks[training_id] = thread
            return {'success': True, 'training_id': training_id}
        except Exception as e:
            return {'success': False, 'error': f'训练启动失败: {str(e)}'}

    def _train_task(self, training_id, agent_id, config, user_id):
        """模拟训练过程，持久化状态，支持断点续训"""
        db = self.db or get_db()
        epochs = config.get('epochs', 10)
        batch_size = config.get('batch_size', 32)
        learning_rate = config.get('learning_rate', 0.001)
        metrics = {'loss': [], 'accuracy': []}
        try:
            for epoch in range(1, epochs + 1):
                # 检查是否被取消
                record = db.training_history.find_one({'_id': ObjectId(training_id)})
                if record.get('status') == 'cancelled':
                    db.training_history.update_one({'_id': ObjectId(training_id)}, {'$set': {'updated_at': datetime.now()}})
                    return
                # 模拟训练
                time.sleep(1)  # 真实训练可替换为实际逻辑
                loss = max(0.1, 1.0 - epoch * 0.08)
                acc = min(1.0, 0.2 + epoch * 0.08)
                metrics['loss'].append(loss)
                metrics['accuracy'].append(acc)
                db.training_history.update_one(
                    {'_id': ObjectId(training_id)},
                    {'$set': {
                        'progress': int(epoch / epochs * 100),
                        'current_epoch': epoch,
                        'metrics': metrics,
                        'updated_at': datetime.now()
                    }}
                )
            # 训练完成，保存模型文件
            output_file = os.path.join(self.output_dir, f'training_{training_id}.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({'agent_id': agent_id, 'config': config, 'metrics': metrics}, f, ensure_ascii=False, indent=2)
            db.training_history.update_one(
                {'_id': ObjectId(training_id)},
                {'$set': {
                    'status': 'completed',
                    'progress': 100,
                    'end_time': datetime.now(),
                    'output_file': output_file,
                    'updated_at': datetime.now()
                }}
            )
        except Exception as e:
            db.training_history.update_one(
                {'_id': ObjectId(training_id)},
                {'$set': {
                    'status': 'failed',
                    'error_message': str(e),
                    'updated_at': datetime.now()
                }}
            )

    def get_training_status(self, training_id, user_id):
        record = self.db.training_history.find_one({'_id': ObjectId(training_id), 'user_id': user_id})
        if not record:
            return {'success': False, 'error': '训练记录不存在'}
        return {'success': True, 'status': record['status'], 'progress': record['progress'], 'current_epoch': record['current_epoch'], 'metrics': record.get('metrics', {}), 'error_message': record.get('error_message', '')}

    def cancel_training(self, training_id, user_id):
        record = self.db.training_history.find_one({'_id': ObjectId(training_id), 'user_id': user_id})
        if not record:
            return {'success': False, 'error': '训练记录不存在'}
        if record['status'] not in ['running']:
            return {'success': False, 'error': '训练已结束，无法取消'}
        self.db.training_history.update_one({'_id': ObjectId(training_id)}, {'$set': {'status': 'cancelled', 'updated_at': datetime.now()}})
        return {'success': True, 'message': '训练已取消'}

    def get_training_history(self, user_id, page=1, limit=20):
        skip = (page - 1) * limit
        cursor = self.db.training_history.find({'user_id': user_id}).sort('created_at', -1).skip(skip).limit(limit)
        total = self.db.training_history.count_documents({'user_id': user_id})
        history = []
        for record in cursor:
            history.append({
                'training_id': str(record['_id']),
                'agent_id': record['agent_id'],
                'status': record['status'],
                'progress': record['progress'],
                'current_epoch': record['current_epoch'],
                'metrics': record.get('metrics', {}),
                'start_time': record['start_time'].isoformat(),
                'end_time': record['end_time'].isoformat() if record.get('end_time') else None,
                'output_file': record.get('output_file', ''),
                'error_message': record.get('error_message', '')
            })
        return {'success': True, 'history': history, 'total': total, 'page': page, 'limit': limit}

    def get_training_result(self, training_id, user_id):
        record = self.db.training_history.find_one({'_id': ObjectId(training_id), 'user_id': user_id})
        if not record:
            return {'success': False, 'error': '训练记录不存在'}
        if not record.get('output_file') or not os.path.exists(record['output_file']):
            return {'success': False, 'error': '训练结果文件不存在'}
        with open(record['output_file'], 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {'success': True, 'result': data}

    def resume_training(self, training_id, user_id):
        record = self.db.training_history.find_one({'_id': ObjectId(training_id), 'user_id': user_id})
        if not record:
            return {'success': False, 'error': '训练记录不存在'}
        if record['status'] not in ['failed', 'cancelled']:
            return {'success': False, 'error': '只有失败或取消的任务可以续训'}
        # 重新启动训练
        config = record['config']
        agent_id = record['agent_id']
        thread = threading.Thread(target=self._train_task, args=(training_id, agent_id, config, user_id))
        thread.daemon = True
        thread.start()
        self._running_tasks[training_id] = thread
        self.db.training_history.update_one({'_id': ObjectId(training_id)}, {'$set': {'status': 'running', 'updated_at': datetime.now()}})
        return {'success': True, 'message': '训练已恢复'}

    def delete_training(self, training_id, user_id):
        record = self.db.training_history.find_one({'_id': ObjectId(training_id), 'user_id': user_id})
        if not record:
            return {'success': False, 'error': '训练记录不存在'}
        self.db.training_history.delete_one({'_id': ObjectId(training_id)})
        # 删除输出文件
        if record.get('output_file') and os.path.exists(record['output_file']):
            os.remove(record['output_file'])
        return {'success': True, 'message': '训练记录已删除'}

    def get_training_metrics(self, training_id, user_id):
        record = self.db.training_history.find_one({'_id': ObjectId(training_id), 'user_id': user_id})
        if not record:
            return {'success': False, 'error': '训练记录不存在'}
        return {'success': True, 'metrics': record.get('metrics', {})}

# 全局训练服务实例
training_service = TrainingService()
