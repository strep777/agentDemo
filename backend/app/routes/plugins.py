"""
插件管理路由
提供插件的CRUD操作和配置管理
"""

from flask import Blueprint, request, jsonify, send_file
from app.services.database import get_db
from app.services.plugin_executor import plugin_executor
from app.utils.auth import token_required
from app.utils.response import ApiResponse, handle_exception, validate_pagination, validate_required_fields, sanitize_data, serialize_mongo_data
from bson import ObjectId
from datetime import datetime
import os
import json
import tempfile
import zipfile
import shutil

plugins_bp = Blueprint('plugins', __name__)

@plugins_bp.route('/', methods=['GET'])
@token_required
@handle_exception
def get_plugins(current_user):
    """获取插件列表"""
    try:
        db = get_db()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        status = request.args.get('status')
        search = request.args.get('search', '')
        
        page, limit = validate_pagination(page, limit)
        
        # 构建查询条件
        query = {'user_id': current_user['id']}
        if status:
            query['status'] = status
        if search:
            query['name'] = {'$regex': search, '$options': 'i'}
        
        # 获取总数
        total = db.plugins.count_documents(query)
        
        # 获取分页数据
        skip = (page - 1) * limit
        plugins = list(db.plugins.find(query, {
            '_id': 1,
            'name': 1,
            'description': 1,
            'type': 1,
            'status': 1,
            'version': 1,
            'author': 1,
            'created_at': 1,
            'updated_at': 1
        }).sort('created_at', -1).skip(skip).limit(limit))
        
        # 格式化数据
        for plugin in plugins:
            plugin['id'] = str(plugin['_id'])
            plugin['created_at'] = plugin['created_at'].isoformat()
            plugin['updated_at'] = plugin['updated_at'].isoformat()
            del plugin['_id']
        
        return jsonify(ApiResponse.success({
            'data': plugins,
            'total': total,
            'page': page,
            'page_size': limit
        }, "获取插件列表成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@plugins_bp.route('/<plugin_id>', methods=['GET'])
@token_required
@handle_exception
def get_plugin(current_user, plugin_id):
    """获取插件详情"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(plugin_id):
            return jsonify(ApiResponse.error('无效的插件ID')), 400
        
        db = get_db()
        
        plugin = db.plugins.find_one({
            '_id': ObjectId(plugin_id),
            'user_id': current_user['id']
        })
        
        if not plugin:
            return jsonify(ApiResponse.error('插件不存在')), 404
        
        plugin['id'] = str(plugin['_id'])
        plugin['created_at'] = plugin['created_at'].isoformat()
        plugin['updated_at'] = plugin['updated_at'].isoformat()
        del plugin['_id']
        
        return jsonify(ApiResponse.success(plugin, "获取插件详情成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@plugins_bp.route('/', methods=['POST'])
@token_required
@handle_exception
def create_plugin(current_user):
    """创建插件"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['name', 'type']
        validate_required_fields(data, required_fields)
        
        db = get_db()
        
        # 检查插件名称是否已存在
        existing_plugin = db.plugins.find_one({
            'name': data['name'],
            'user_id': current_user['id']
        })
        
        if existing_plugin:
            return jsonify(ApiResponse.error('插件名称已存在')), 400
        
        # 创建插件
        plugin_data = {
            'name': data['name'],
            'description': data.get('description', ''),
            'type': data['type'],
            'version': data.get('version', '1.0.0'),
            'author': data.get('author', current_user['username']),
            'status': data.get('status', 'inactive'),
            'config': data.get('config', {}),
            'metadata': data.get('metadata', {}),
            'user_id': current_user['id'],
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        result = db.plugins.insert_one(plugin_data)
        plugin_data['id'] = str(result.inserted_id)
        
        # 序列化数据以处理 ObjectId 和 datetime
        serialized_plugin_data = serialize_mongo_data(plugin_data)
        
        return jsonify(ApiResponse.success(serialized_plugin_data, "插件创建成功")), 201
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@plugins_bp.route('/<plugin_id>', methods=['PUT'])
@token_required
@handle_exception
def update_plugin(current_user, plugin_id):
    """更新插件"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(plugin_id):
            return jsonify(ApiResponse.error('无效的插件ID')), 400
        
        data = request.get_json()
        db = get_db()
        
        # 检查插件是否存在
        plugin = db.plugins.find_one({
            '_id': ObjectId(plugin_id),
            'user_id': current_user['id']
        })
        
        if not plugin:
            return jsonify(ApiResponse.error('插件不存在')), 404
        
        # 更新数据
        update_data = {
            'updated_at': datetime.now()
        }
        
        allowed_fields = ['name', 'description', 'version', 'author', 'status', 'config', 'metadata']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        # 更新数据库
        db.plugins.update_one(
            {'_id': ObjectId(plugin_id)},
            {'$set': update_data}
        )
        
        return jsonify(ApiResponse.success(None, "插件更新成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@plugins_bp.route('/<plugin_id>', methods=['DELETE'])
@token_required
@handle_exception
def delete_plugin(current_user, plugin_id):
    """删除插件"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(plugin_id):
            return jsonify(ApiResponse.error('无效的插件ID')), 400
        
        db = get_db()
        
        # 检查插件是否存在
        plugin = db.plugins.find_one({
            '_id': ObjectId(plugin_id),
            'user_id': current_user['id']
        })
        
        if not plugin:
            return jsonify(ApiResponse.error('插件不存在')), 404
        
        # 删除插件文件
        if plugin.get('file_path'):
            try:
                os.remove(plugin['file_path'])
            except:
                pass
        
        # 删除数据库记录
        db.plugins.delete_one({'_id': ObjectId(plugin_id)})
        
        return jsonify(ApiResponse.success(None, "插件删除成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@plugins_bp.route('/<plugin_id>/toggle', methods=['POST'])
@token_required
@handle_exception
def toggle_plugin(current_user, plugin_id):
    """切换插件状态"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(plugin_id):
            return jsonify(ApiResponse.error('无效的插件ID')), 400
        
        db = get_db()
        
        # 检查插件是否存在
        plugin = db.plugins.find_one({
            '_id': ObjectId(plugin_id),
            'user_id': current_user['id']
        })
        
        if not plugin:
            return jsonify(ApiResponse.error('插件不存在')), 404
        
        # 切换状态
        new_status = 'active' if plugin['status'] == 'inactive' else 'inactive'
        
        db.plugins.update_one(
            {'_id': ObjectId(plugin_id)},
            {'$set': {'status': new_status, 'updated_at': datetime.now()}}
        )
        
        return jsonify(ApiResponse.success({'status': new_status}, "插件状态切换成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@plugins_bp.route('/upload', methods=['POST'])
@token_required
@handle_exception
def upload_plugin(current_user):
    """上传插件"""
    try:
        if 'file' not in request.files:
            return jsonify(ApiResponse.error('没有上传文件')), 400
        
        file = request.files['file']
        if not file or file.filename == '' or file.filename is None:
            return jsonify(ApiResponse.error('没有选择文件')), 400
        
        if not file.filename.endswith('.zip'):
            return jsonify(ApiResponse.error('只支持ZIP格式的插件文件')), 400
        
        db = get_db()
        
        # 创建上传目录
        upload_dir = os.path.join('uploads', 'plugins', current_user['id'])
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # 解压并验证插件
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # 检查是否有plugin.json文件
                if 'plugin.json' not in zip_ref.namelist():
                    os.remove(file_path)
                    return jsonify(ApiResponse.error('插件文件格式不正确，缺少plugin.json')), 400
                
                # 读取插件配置
                plugin_config = json.loads(zip_ref.read('plugin.json').decode('utf-8'))
                
                # 验证必需字段
                required_fields = ['name', 'type', 'version']
                for field in required_fields:
                    if field not in plugin_config:
                        os.remove(file_path)
                        return jsonify(ApiResponse.error(f'插件配置缺少必需字段: {field}')), 400
                
                # 检查插件名称是否已存在
                existing_plugin = db.plugins.find_one({
                    'name': plugin_config['name'],
                    'user_id': current_user['id']
                })
                
                if existing_plugin:
                    os.remove(file_path)
                    return jsonify(ApiResponse.error('插件名称已存在')), 400
                
                # 创建插件记录
                plugin_data = {
                    'name': plugin_config['name'],
                    'description': plugin_config.get('description', ''),
                    'type': plugin_config['type'],
                    'version': plugin_config['version'],
                    'author': plugin_config.get('author', current_user['username']),
                    'status': 'inactive',
                    'config': plugin_config.get('config', {}),
                    'metadata': plugin_config.get('metadata', {}),
                    'file_path': file_path,
                    'user_id': current_user['id'],
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
                
                result = db.plugins.insert_one(plugin_data)
                plugin_data['id'] = str(result.inserted_id)
                
                return jsonify(ApiResponse.success(plugin_data, "插件上传成功"))
                
        except Exception as e:
            os.remove(file_path)
            return jsonify(ApiResponse.error(f'插件文件解析失败: {str(e)}')), 400
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@plugins_bp.route('/<plugin_id>/download', methods=['GET'])
@token_required
@handle_exception
def download_plugin(current_user, plugin_id):
    """下载插件"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(plugin_id):
            return jsonify(ApiResponse.error('无效的插件ID')), 400
        
        db = get_db()
        
        # 检查插件是否存在
        plugin = db.plugins.find_one({
            '_id': ObjectId(plugin_id),
            'user_id': current_user['id']
        })
        
        if not plugin:
            return jsonify(ApiResponse.error('插件不存在')), 404
        
        if not plugin.get('file_path') or not os.path.exists(plugin['file_path']):
            return jsonify(ApiResponse.error('插件文件不存在')), 404
        
        return send_file(
            plugin['file_path'],
            as_attachment=True,
            download_name=f"{plugin['name']}_{plugin['version']}.zip"
        )
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@plugins_bp.route('/<plugin_id>/test', methods=['POST'])
@token_required
@handle_exception
def test_plugin(current_user, plugin_id):
    """测试插件"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(plugin_id):
            return jsonify(ApiResponse.error('无效的插件ID')), 400
        
        data = request.get_json()
        test_input = data.get('input', {})
        
        db = get_db()
        
        # 检查插件是否存在
        plugin = db.plugins.find_one({
            '_id': ObjectId(plugin_id),
            'user_id': current_user['id']
        })
        
        if not plugin:
            return jsonify(ApiResponse.error('插件不存在')), 404
        
        # 执行插件测试
        try:
            result = plugin_executor.test_plugin(plugin, test_input)
            return jsonify(ApiResponse.success(result, "插件测试成功"))
        except Exception as e:
            return jsonify(ApiResponse.error(f'插件测试失败: {str(e)}')), 400
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@plugins_bp.route('/<plugin_id>/execute', methods=['POST'])
@token_required
@handle_exception
def execute_plugin(current_user, plugin_id):
    """执行插件"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(plugin_id):
            return jsonify(ApiResponse.error('无效的插件ID')), 400
        
        data = request.get_json()
        execution_input = data.get('input', {})
        
        db = get_db()
        
        # 检查插件是否存在
        plugin = db.plugins.find_one({
            '_id': ObjectId(plugin_id),
            'user_id': current_user['id']
        })
        
        if not plugin:
            return jsonify(ApiResponse.error('插件不存在')), 404
        
        # 执行插件
        try:
            result = plugin_executor.execute_plugin(plugin, execution_input)
            return jsonify(ApiResponse.success(result, "插件执行成功"))
        except Exception as e:
            return jsonify(ApiResponse.error(f'插件执行失败: {str(e)}')), 400
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@plugins_bp.route('/available', methods=['GET'])
@token_required
@handle_exception
def get_available_plugins(current_user):
    """获取可用插件列表"""
    try:
        db = get_db()
        
        # 获取激活状态的插件
        plugins = list(db.plugins.find({
            'user_id': current_user['id'],
            'status': 'active'
        }, {
            '_id': 1,
            'name': 1,
            'description': 1,
            'type': 1,
            'version': 1
        }).sort('name', 1))
        
        # 格式化数据
        for plugin in plugins:
            plugin['id'] = str(plugin['_id'])
            del plugin['_id']
        
        return jsonify(ApiResponse.success(plugins, "获取可用插件列表成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@plugins_bp.route('/<plugin_id>/config', methods=['GET'])
@token_required
@handle_exception
def get_plugin_config(current_user, plugin_id):
    """获取插件配置"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(plugin_id):
            return jsonify(ApiResponse.error('无效的插件ID')), 400
        
        db = get_db()
        
        # 检查插件是否存在
        plugin = db.plugins.find_one({
            '_id': ObjectId(plugin_id),
            'user_id': current_user['id']
        })
        
        if not plugin:
            return jsonify(ApiResponse.error('插件不存在')), 404
        
        config = plugin.get('config', {})
        return jsonify(ApiResponse.success(config, "获取插件配置成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@plugins_bp.route('/<plugin_id>/config', methods=['PUT'])
@token_required
@handle_exception
def update_plugin_config(current_user, plugin_id):
    """更新插件配置"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(plugin_id):
            return jsonify(ApiResponse.error('无效的插件ID')), 400
        
        data = request.get_json()
        config = data.get('config', {})
        
        db = get_db()
        
        # 检查插件是否存在
        plugin = db.plugins.find_one({
            '_id': ObjectId(plugin_id),
            'user_id': current_user['id']
        })
        
        if not plugin:
            return jsonify(ApiResponse.error('插件不存在')), 404
        
        # 更新配置
        db.plugins.update_one(
            {'_id': ObjectId(plugin_id)},
            {'$set': {'config': config, 'updated_at': datetime.now()}}
        )
        
        return jsonify(ApiResponse.success(None, "插件配置更新成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400 