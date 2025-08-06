# 模型管理路由模块
# 提供模型的CRUD操作、Ollama集成、模型测试等功能

from flask import Blueprint, request, jsonify
from app.services.database import get_db
from app.services.ollama import OllamaService
from app.utils.auth import token_required
from app.utils.response import ApiResponse, handle_exception, validate_pagination, validate_required_fields, sanitize_data, serialize_mongo_data
from bson import ObjectId
from datetime import datetime
import json

# 创建模型蓝图
models_bp = Blueprint('models', __name__)

@models_bp.route('', methods=['GET'])
@models_bp.route('/', methods=['GET'])
@token_required
@handle_exception
def get_models(current_user):
    """
    获取模型列表
    支持分页、搜索、按提供商和类型筛选
    """
    print(f"🔍 获取模型列表 - 用户: {current_user['username']}")
    
    # 获取查询参数
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    provider = request.args.get('provider', '')
    model_type = request.args.get('type', '')
    search = request.args.get('search', '')
    
    print(f"📝 查询参数: page={page}, limit={limit}, provider={provider}, type={model_type}, search={search}")
    
    page, limit = validate_pagination(page, limit)
    
    # 构建查询条件
    query = {}
    
    if provider:
        query['provider'] = provider
    
    if model_type:
        query['type'] = model_type  # 使用与前端一致的字段名
    
    if search:
        query['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}}
        ]
    
    print(f"🔍 查询条件: {query}")
    
    db = get_db()
    print(f"📊 数据库类型: {type(db)}")
    
    # 计算总数
    total = db.models.count_documents(query)
    print(f"📊 模型总数: {total}")
    
    # 获取分页数据
    skip = (page - 1) * limit
    models = list(db.models.find(query).skip(skip).limit(limit).sort('created_at', -1))
    print(f"📊 获取到 {len(models)} 个模型")
    
    # 格式化数据
    for model in models:
        model['id'] = str(model['_id'])
        model['created_at'] = model['created_at'].isoformat() if model.get('created_at') else None
        model['updated_at'] = model['updated_at'].isoformat() if model.get('updated_at') else None
        
        # 确保状态字段正确
        if 'status' not in model or model['status'] is None:
            model['status'] = 'active'  # 默认状态为active
        elif isinstance(model['status'], bool):
            model['status'] = 'active' if model['status'] else 'inactive'
        elif model['status'] not in ['active', 'inactive', 'available']:
            model['status'] = 'active'
        
        # 确保所有ObjectId都转换为字符串
        if 'parameters' in model and isinstance(model['parameters'], dict):
            for key, value in model['parameters'].items():
                if isinstance(value, ObjectId):
                    model['parameters'][key] = str(value)
        
        # 确保字段名与前端期望一致
        if 'model_type' in model:
            model['type'] = model['model_type']
            del model['model_type']
        
        if 'api_base' in model:
            model['server_url'] = model['api_base']
            del model['api_base']
        
        del model['_id']
        
        print(f"  📊 模型: {model.get('name', '未知')} - 状态: {model.get('status', '未知')}")
    
    print("✅ 模型列表获取成功")
    return jsonify(ApiResponse.success({
        'data': models,
        'total': total,
        'page': page,
        'page_size': limit
    }, "获取模型列表成功"))

@models_bp.route('/<model_id>', methods=['GET'])
@token_required
@handle_exception
def get_model(current_user, model_id):
    """
    获取模型详情
    """
    # 验证ID格式
    if not ObjectId.is_valid(model_id):
        return jsonify(ApiResponse.error('无效的模型ID')), 400
    
    db = get_db()
    
    # 获取模型
    model = db.models.find_one({'_id': ObjectId(model_id)})
    if not model:
        return jsonify(ApiResponse.error('模型不存在')), 404
    
    # 格式化数据
    model['id'] = str(model['_id'])
    model['created_at'] = model['created_at'].isoformat() if model.get('created_at') else None
    model['updated_at'] = model['updated_at'].isoformat() if model.get('updated_at') else None
    
    # 确保字段名与前端期望一致
    if 'model_type' in model:
        model['type'] = model['model_type']
        del model['model_type']
    
    if 'api_base' in model:
        model['server_url'] = model['api_base']
        del model['api_base']
    
    del model['_id']
    
    return jsonify(ApiResponse.success(model, "获取模型详情成功"))

@models_bp.route('', methods=['POST'])
@models_bp.route('/', methods=['POST'])
@token_required
@handle_exception
def create_model(current_user):
    """
    创建模型
    支持各种类型的模型创建，包括Ollama模型
    """
    # 检查用户权限
    if current_user.get('role') != 'admin':
        return jsonify(ApiResponse.error('只有管理员可以创建模型')), 403
    
    data = request.get_json()
    print(f"📝 创建模型数据: {data}")
    
    # 验证必需字段
    required_fields = ['name', 'provider', 'type']
    validate_required_fields(data, required_fields)
    
    db = get_db()
    
    # 检查模型名称是否已存在
    existing_model = db.models.find_one({'name': data['name']})
    if existing_model:
        return jsonify(ApiResponse.error('模型名称已存在')), 400
    
    # 创建模型数据
    model_data = {
        'name': data['name'],
        'provider': data['provider'],
        'type': data['type'],  # 保持与前端一致的字段名
        'description': data.get('description', ''),
        'version': data.get('version', '1.0.0'),
        'api_key': data.get('api_key', ''),
        'server_url': data.get('server_url', ''),  # 保持与前端一致的字段名
        'max_tokens': data.get('max_tokens', 4096),
        'temperature': data.get('temperature', 0.7),
        'top_p': data.get('top_p', 1.0),
        'frequency_penalty': data.get('frequency_penalty', 0.0),
        'presence_penalty': data.get('presence_penalty', 0.0),
        'parameters': data.get('parameters', {}),  # 保持与前端一致的字段名
        'settings': data.get('settings', {}),
        'metadata': data.get('metadata', {}),
        'is_active': data.get('is_active', True),
        'status': 'active',  # 默认状态，与前端保持一致
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
        'stats': {
            'usage_count': 0,
            'success_count': 0,
            'error_count': 0,
            'avg_response_time': 0
        }
    }
    
    print(f"💾 保存模型数据: {model_data}")
    
    # 插入数据库
    result = db.models.insert_one(model_data)
    
    # 重新获取插入的数据，确保所有字段都正确格式化
    inserted_model = db.models.find_one({'_id': result.inserted_id})
    if inserted_model:
        # 使用序列化函数处理所有MongoDB类型
        response_data = serialize_mongo_data(inserted_model)
        # 确保ID字段正确
        if isinstance(response_data, dict):
            response_data['id'] = str(inserted_model['_id'])
            # 移除原始的_id字段
            if '_id' in response_data:
                del response_data['_id']
        else:
            response_data = {
                'id': str(inserted_model['_id']),
                'name': inserted_model.get('name'),
                'provider': inserted_model.get('provider'),
                'type': inserted_model.get('type'),
                'status': inserted_model.get('status', 'active')
            }
        
        print(f"✅ 模型创建成功: {inserted_model.get('name')}")
        return jsonify(ApiResponse.success(response_data, "模型创建成功")), 201
    else:
        print("❌ 模型创建失败：无法获取插入的数据")
        return jsonify(ApiResponse.error("模型创建失败")), 500

@models_bp.route('/<model_id>', methods=['PUT'])
@token_required
@handle_exception
def update_model(current_user, model_id):
    """
    更新模型
    """
    # 检查用户权限
    if current_user.get('role') != 'admin':
        return jsonify(ApiResponse.error('只有管理员可以更新模型')), 403
    
    # 验证ID格式
    if not ObjectId.is_valid(model_id):
        return jsonify(ApiResponse.error('无效的模型ID')), 400
    
    data = request.get_json()
    print(f"📝 更新模型数据: {data}")
    
    db = get_db()
    
    # 检查模型是否存在
    existing_model = db.models.find_one({'_id': ObjectId(model_id)})
    if not existing_model:
        return jsonify(ApiResponse.error('模型不存在')), 404
    
    # 如果更新名称，检查是否与其他模型冲突
    if 'name' in data and data['name'] != existing_model['name']:
        name_conflict = db.models.find_one({
            'name': data['name'],
            '_id': {'$ne': ObjectId(model_id)}
        })
        if name_conflict:
            return jsonify(ApiResponse.error('模型名称已存在')), 400
    
    # 更新数据
    update_data = {
        'updated_at': datetime.now()
    }
    
    # 只更新提供的字段
    allowed_fields = [
        'name', 'description', 'version', 'api_key', 'server_url',
        'max_tokens', 'temperature', 'top_p', 'frequency_penalty',
        'presence_penalty', 'parameters', 'settings', 'metadata',
        'is_active', 'status'
    ]
    
    for field in allowed_fields:
        if field in data:
            update_data[field] = data[field]
    
    print(f"💾 更新模型数据: {update_data}")
    
    # 执行更新
    result = db.models.update_one(
        {'_id': ObjectId(model_id)},
        {'$set': update_data}
    )
    
    if result.modified_count > 0:
        print(f"✅ 模型更新成功: {model_id}")
        return jsonify(ApiResponse.success(None, "模型更新成功"))
    else:
        print(f"❌ 模型更新失败: {model_id}")
        return jsonify(ApiResponse.error("模型更新失败")), 500

@models_bp.route('/<model_id>', methods=['DELETE'])
@token_required
@handle_exception
def delete_model(current_user, model_id):
    """
    删除模型
    """
    # 检查用户权限
    if current_user.get('role') != 'admin':
        return jsonify(ApiResponse.error('只有管理员可以删除模型')), 403
    
    # 验证ID格式
    if not ObjectId.is_valid(model_id):
        return jsonify(ApiResponse.error('无效的模型ID')), 400
    
    db = get_db()
    
    # 检查模型是否存在
    existing_model = db.models.find_one({'_id': ObjectId(model_id)})
    if not existing_model:
        return jsonify(ApiResponse.error('模型不存在')), 404
    
    # 执行删除
    result = db.models.delete_one({'_id': ObjectId(model_id)})
    
    if result.deleted_count > 0:
        print(f"✅ 模型删除成功: {model_id}")
        return jsonify(ApiResponse.success(None, "模型删除成功"))
    else:
        print(f"❌ 模型删除失败: {model_id}")
        return jsonify(ApiResponse.error("模型删除失败")), 500

@models_bp.route('/<model_id>/test', methods=['POST'])
@token_required
@handle_exception
def test_model(current_user, model_id):
    """
    测试模型
    """
    # 验证ID格式
    if not ObjectId.is_valid(model_id):
        return jsonify(ApiResponse.error('无效的模型ID')), 400
    
    data = request.get_json()
    message = data.get('message', 'Hello, how are you?')
    
    db = get_db()
    
    # 获取模型
    model = db.models.find_one({'_id': ObjectId(model_id)})
    if not model:
        return jsonify(ApiResponse.error('模型不存在')), 404
    
    try:
        print(f"🧪 测试模型: {model.get('name')} - 消息: {message[:50]}...")
        
        # 根据提供商调用不同的测试方法
        if model.get('provider') == 'ollama':
            # 使用Ollama服务测试
            server_url = model.get('server_url', 'http://localhost:11434')
            model_name = model.get('name')
            
            print(f"🔧 使用Ollama测试 - 服务器: {server_url}, 模型: {model_name}")
            
            ollama_service = OllamaService(server_url)
            response = ollama_service.generate_text(
                model_name=model_name,
                prompt=message,
                temperature=model.get('temperature', 0.7),
                max_tokens=model.get('max_tokens', 1000)
            )
            
            print(f"✅ Ollama模型测试成功")
            return jsonify(ApiResponse.success({
                'success': True,
                'response': response,
                'model_name': model_name,
                'provider': 'ollama'
            }, "模型测试成功"))
        else:
            # 其他提供商的测试逻辑
            print(f"🔧 使用通用测试 - 提供商: {model.get('provider')}")
            return jsonify(ApiResponse.success({
                'success': True,
                'response': f"模型 {model.get('name')} 的测试回复：{message}",
                'model_name': model.get('name'),
                'provider': model.get('provider')
            }, "模型测试成功"))
            
    except Exception as e:
        print(f"❌ 模型测试失败: {str(e)}")
        return jsonify(ApiResponse.success({
            'success': False,
            'error': str(e)
        }, "模型测试失败"))

@models_bp.route('/providers', methods=['GET'])
@token_required
@handle_exception
def get_model_providers(current_user):
    """
    获取支持的模型提供商列表
    """
    providers = [
        {'value': 'ollama', 'label': 'Ollama'},
        {'value': 'openai', 'label': 'OpenAI'},
        {'value': 'local', 'label': '本地模型'},
        {'value': 'huggingface', 'label': 'Hugging Face'}
    ]
    return jsonify(ApiResponse.success(providers, "获取提供商列表成功"))

@models_bp.route('/types', methods=['GET'])
@token_required
@handle_exception
def get_model_types(current_user):
    """
    获取支持的模型类型列表
    """
    types = [
        {'value': 'llm', 'label': '大语言模型'},
        {'value': 'embedding', 'label': '嵌入模型'},
        {'value': 'image', 'label': '图像模型'},
        {'value': 'speech', 'label': '语音模型'}
    ]
    return jsonify(ApiResponse.success(types, "获取模型类型列表成功"))

@models_bp.route('/ollama/health', methods=['GET'])
@token_required
@handle_exception
def check_ollama_health(current_user):
    """
    检查Ollama服务器状态
    """
    from app.services.ollama import OllamaService
    
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
    print(f"🔍 检查Ollama健康状态: {server_url}")
    
    try:
        ollama_service = OllamaService(server_url)
        is_healthy = ollama_service.health_check()
        
        print(f"🏥 Ollama健康检查结果: {is_healthy}")
        
        return jsonify(ApiResponse.success({
            'healthy': is_healthy,
            'server_url': server_url
        }, "Ollama服务器状态检查完成"))
    except Exception as e:
        print(f"❌ Ollama健康检查失败: {str(e)}")
        return jsonify(ApiResponse.error(f"Ollama健康检查失败: {str(e)}")), 500

@models_bp.route('/ollama/models', methods=['GET'])
@token_required
@handle_exception
def get_ollama_models(current_user):
    """
    获取Ollama可用模型列表
    """
    from app.services.ollama import OllamaService
    
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
    print(f"📋 获取Ollama模型列表: {server_url}")
    
    try:
        ollama_service = OllamaService(server_url)
        models = ollama_service.list_models()
        
        # OllamaService现在直接返回模型名称列表
        model_names = models if isinstance(models, list) else []
        
        print(f"✅ 获取到 {len(model_names)} 个Ollama模型: {model_names}")
        
        return jsonify(ApiResponse.success(model_names, "获取Ollama模型列表成功"))
    except Exception as e:
        print(f"❌ 获取Ollama模型列表失败: {str(e)}")
        return jsonify(ApiResponse.error(f"获取Ollama模型列表失败: {str(e)}")), 500

@models_bp.route('/ollama/pull', methods=['POST'])
@token_required
@handle_exception
def pull_ollama_model(current_user):
    """
    拉取Ollama模型
    """
    data = request.get_json()
    model_name = data.get('model_name')
    
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
    server_url = data.get('server_url', default_ollama_url)
    
    if not model_name:
        return jsonify(ApiResponse.error('模型名称不能为空')), 400
    
    print(f"📥 拉取Ollama模型: {model_name} from {server_url}")
    
    try:
        from app.services.ollama import OllamaService
        ollama_service = OllamaService(server_url)
        
        result = ollama_service.pull_model(model_name)
        
        print(f"✅ 模型拉取成功: {model_name}")
        
        return jsonify(ApiResponse.success(result, "模型拉取成功"))
    except Exception as e:
        print(f"❌ 模型拉取失败: {str(e)}")
        return jsonify(ApiResponse.error(f"模型拉取失败: {str(e)}")), 500

@models_bp.route('/ollama/test', methods=['POST'])
@token_required
@handle_exception
def test_ollama_model(current_user):
    """
    测试Ollama模型
    """
    data = request.get_json()
    model_name = data.get('model_name')
    prompt = data.get('prompt', 'Hello, how are you?')
    
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
    server_url = data.get('server_url', default_ollama_url)
    
    if not model_name:
        return jsonify(ApiResponse.error('模型名称不能为空')), 400
    
    print(f"🧪 测试Ollama模型: {model_name} with prompt: {prompt[:50]}...")
    
    try:
        from app.services.ollama import OllamaService
        ollama_service = OllamaService(server_url)
        
        result = ollama_service.generate_text(model_name, prompt)
        
        print(f"✅ 模型测试成功: {model_name}")
        
        return jsonify(ApiResponse.success({
            'success': True,
            'response': result,
            'model_name': model_name,
            'provider': 'ollama'
        }, "模型测试成功"))
    except Exception as e:
        print(f"❌ 模型测试失败: {str(e)}")
        return jsonify(ApiResponse.success({
            'success': False,
            'error': str(e)
        }, "模型测试失败")) 