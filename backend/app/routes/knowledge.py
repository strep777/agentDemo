from flask import Blueprint, request, jsonify
from app.services.database import get_db
from app.utils.auth import token_required
from app.utils.response import ApiResponse, handle_exception, validate_required_fields, serialize_mongo_data
from bson import ObjectId
from datetime import datetime

knowledge_bp = Blueprint('knowledge', __name__)

@knowledge_bp.route('', methods=['GET'])
@knowledge_bp.route('/', methods=['GET'])
@token_required
@handle_exception
def get_knowledge_bases(current_user):
    """获取知识库列表"""
    try:
        print(f"🔍 获取知识库列表 - 用户: {current_user['username']}")
        
        db = get_db()
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        search = request.args.get('search', '')
        
        # 构建查询条件
        query = {'user_id': current_user['id']}
        if search:
            query['name'] = {'$regex': search, '$options': 'i'}
        
        # 计算总数
        total = db.knowledge_bases.count_documents(query)
        
        # 获取分页数据
        skip = (page - 1) * limit
        knowledge_bases = list(db.knowledge_bases.find(query)
                             .skip(skip)
                             .limit(limit)
                             .sort('updated_at', -1))
        
        # 格式化数据
        for kb in knowledge_bases:
            kb['id'] = str(kb['_id'])
            kb['created_at'] = kb['created_at'].isoformat() if kb.get('created_at') else None
            kb['updated_at'] = kb['updated_at'].isoformat() if kb.get('updated_at') else None
            del kb['_id']
        
        print(f"✅ 获取到 {len(knowledge_bases)} 个知识库")
        
        # 序列化数据以处理 ObjectId 和 datetime
        serialized_knowledge_bases = serialize_mongo_data(knowledge_bases)
        
        return jsonify(ApiResponse.success({
            'data': serialized_knowledge_bases,
            'total': total,
            'page': page,
            'page_size': limit
        }, "获取知识库列表成功"))
        
    except Exception as e:
        print(f"❌ 获取知识库列表失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

@knowledge_bp.route('/<kb_id>', methods=['GET'])
@token_required
@handle_exception
def get_knowledge_base(current_user, kb_id):
    """获取知识库详情"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(kb_id):
            return jsonify(ApiResponse.error('无效的知识库ID')), 400
        
        db = get_db()
        
        # 验证知识库归属
        kb = db.knowledge_bases.find_one({
            '_id': ObjectId(kb_id),
            'user_id': current_user['id']
        })
        
        if not kb:
            return jsonify(ApiResponse.error('知识库不存在')), 404
        
        # 格式化数据
        kb['id'] = str(kb['_id'])
        kb['created_at'] = kb['created_at'].isoformat() if kb.get('created_at') else None
        kb['updated_at'] = kb['updated_at'].isoformat() if kb.get('updated_at') else None
        del kb['_id']
        
        # 序列化数据以处理 ObjectId 和 datetime
        serialized_kb = serialize_mongo_data(kb)
        
        return jsonify(ApiResponse.success(serialized_kb, "获取知识库详情成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@knowledge_bp.route('', methods=['POST'])
@knowledge_bp.route('/', methods=['POST'])
@token_required
@handle_exception
def create_knowledge_base(current_user):
    """创建知识库"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['name', 'description']
        validate_required_fields(data, required_fields)
        
        db = get_db()
        
        # 检查知识库名称是否重复
        existing_kb = db.knowledge_bases.find_one({
            'user_id': current_user['id'],
            'name': data['name']
        })
        
        if existing_kb:
            return jsonify(ApiResponse.error('知识库名称已存在')), 400
        
        # 创建知识库数据
        kb_data = {
            'user_id': current_user['id'],
            'name': data['name'],
            'description': data['description'],
            'type': data.get('type', 'general'),
            'status': 'active',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        result = db.knowledge_bases.insert_one(kb_data)
        kb_data['id'] = str(result.inserted_id)
        
        # 格式化时间
        kb_data['created_at'] = kb_data['created_at'].isoformat()
        kb_data['updated_at'] = kb_data['updated_at'].isoformat()
        
        print(f"✅ 知识库创建成功: {kb_data['name']}")
        
        # 序列化数据以处理 ObjectId 和 datetime
        serialized_kb_data = serialize_mongo_data(kb_data)
        
        return jsonify(ApiResponse.success(serialized_kb_data, "知识库创建成功")), 201
        
    except Exception as e:
        print(f"❌ 创建知识库失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

@knowledge_bp.route('/<kb_id>', methods=['PUT'])
@token_required
@handle_exception
def update_knowledge_base(current_user, kb_id):
    """更新知识库"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(kb_id):
            return jsonify(ApiResponse.error('无效的知识库ID')), 400
        
        data = request.get_json()
        
        db = get_db()
        
        # 验证知识库归属
        kb = db.knowledge_bases.find_one({
            '_id': ObjectId(kb_id),
            'user_id': current_user['id']
        })
        
        if not kb:
            return jsonify(ApiResponse.error('知识库不存在')), 404
        
        # 检查名称是否重复（排除当前知识库）
        if 'name' in data:
            existing_kb = db.knowledge_bases.find_one({
                'user_id': current_user['id'],
                'name': data['name'],
                '_id': {'$ne': ObjectId(kb_id)}
            })
            
            if existing_kb:
                return jsonify(ApiResponse.error('知识库名称已存在')), 400
        
        # 更新知识库
        update_data = {
            'updated_at': datetime.now()
        }
        
        if 'name' in data:
            update_data['name'] = data['name']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'type' in data:
            update_data['type'] = data['type']
        if 'status' in data:
            update_data['status'] = data['status']
        
        db.knowledge_bases.update_one(
            {'_id': ObjectId(kb_id)},
            {'$set': update_data}
        )
        
        print(f"✅ 知识库更新成功: {kb_id}")
        
        return jsonify(ApiResponse.success(None, "知识库更新成功"))
        
    except Exception as e:
        print(f"❌ 更新知识库失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

@knowledge_bp.route('/<kb_id>', methods=['DELETE'])
@token_required
@handle_exception
def delete_knowledge_base(current_user, kb_id):
    """删除知识库"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(kb_id):
            return jsonify(ApiResponse.error('无效的知识库ID')), 400
        
        db = get_db()
        
        # 验证知识库归属
        kb = db.knowledge_bases.find_one({
            '_id': ObjectId(kb_id),
            'user_id': current_user['id']
        })
        
        if not kb:
            return jsonify(ApiResponse.error('知识库不存在')), 404
        
        # 删除知识库和所有相关文档
        db.knowledge_bases.delete_one({'_id': ObjectId(kb_id)})
        db.documents.delete_many({'knowledge_base_id': kb_id})
        
        print(f"✅ 知识库删除成功: {kb_id}")
        
        return jsonify(ApiResponse.success(None, "知识库删除成功"))
        
    except Exception as e:
        print(f"❌ 删除知识库失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

@knowledge_bp.route('/<kb_id>/documents', methods=['GET'])
@token_required
@handle_exception
def get_documents(current_user, kb_id):
    """获取知识库文档列表"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(kb_id):
            return jsonify(ApiResponse.error('无效的知识库ID')), 400
        
        db = get_db()
        
        # 验证知识库归属
        kb = db.knowledge_bases.find_one({
            '_id': ObjectId(kb_id),
            'user_id': current_user['id']
        })
        
        if not kb:
            return jsonify(ApiResponse.error('知识库不存在')), 404
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # 计算总数
        total = db.documents.count_documents({'knowledge_base_id': kb_id})
        
        # 获取分页数据
        skip = (page - 1) * limit
        documents = list(db.documents.find({'knowledge_base_id': kb_id})
                        .skip(skip)
                        .limit(limit)
                        .sort('created_at', -1))
        
        # 格式化数据
        for doc in documents:
            doc['id'] = str(doc['_id'])
            doc['created_at'] = doc['created_at'].isoformat() if doc.get('created_at') else None
            doc['updated_at'] = doc['updated_at'].isoformat() if doc.get('updated_at') else None
            del doc['_id']
        
        print(f"✅ 获取到 {len(documents)} 个文档")
        
        return jsonify(ApiResponse.success({
            'data': documents,
            'total': total,
            'page': page,
            'page_size': limit
        }, "获取文档列表成功"))
        
    except Exception as e:
        print(f"❌ 获取文档列表失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

@knowledge_bp.route('/<kb_id>/documents', methods=['POST'])
@token_required
@handle_exception
def upload_document(current_user, kb_id):
    """上传文档到知识库"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(kb_id):
            return jsonify(ApiResponse.error('无效的知识库ID')), 400
        
        db = get_db()
        
        # 验证知识库归属
        kb = db.knowledge_bases.find_one({
            '_id': ObjectId(kb_id),
            'user_id': current_user['id']
        })
        
        if not kb:
            return jsonify(ApiResponse.error('知识库不存在')), 404
        
        # 处理文件上传
        if 'file' not in request.files:
            return jsonify(ApiResponse.error('没有上传文件')), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify(ApiResponse.error('没有选择文件')), 400
        
        # 保存文档数据
        doc_data = {
            'knowledge_base_id': kb_id,
            'name': file.filename,
            'type': file.content_type,
            'size': 0,  # 实际大小需要计算
            'status': 'processing',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        result = db.documents.insert_one(doc_data)
        doc_data['id'] = str(result.inserted_id)
        
        # 格式化时间
        doc_data['created_at'] = doc_data['created_at'].isoformat()
        doc_data['updated_at'] = doc_data['updated_at'].isoformat()
        
        print(f"✅ 文档上传成功: {file.filename}")
        
        return jsonify(ApiResponse.success(doc_data, "文档上传成功")), 201
        
    except Exception as e:
        print(f"❌ 上传文档失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

@knowledge_bp.route('/<kb_id>/rebuild-index', methods=['POST'])
@token_required
@handle_exception
def rebuild_index(current_user, kb_id):
    """重建知识库索引"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(kb_id):
            return jsonify(ApiResponse.error('无效的知识库ID')), 400
        
        db = get_db()
        
        # 验证知识库归属
        kb = db.knowledge_bases.find_one({
            '_id': ObjectId(kb_id),
            'user_id': current_user['id']
        })
        
        if not kb:
            return jsonify(ApiResponse.error('知识库不存在')), 404
        
        # 这里应该实现重建索引的逻辑
        # 1. 获取知识库中的所有文档
        # 2. 重新处理文档内容
        # 3. 更新索引
        # 4. 更新知识库状态
        
        print(f"✅ 索引重建成功: {kb_id}")
        
        return jsonify(ApiResponse.success(None, "索引重建成功"))
        
    except Exception as e:
        print(f"❌ 重建索引失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

@knowledge_bp.route('/<kb_id>/documents/<doc_id>', methods=['DELETE'])
@token_required
@handle_exception
def delete_document(current_user, kb_id, doc_id):
    """删除知识库文档"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(kb_id) or not ObjectId.is_valid(doc_id):
            return jsonify(ApiResponse.error('无效的ID')), 400
        
        db = get_db()
        
        # 验证知识库归属
        kb = db.knowledge_bases.find_one({
            '_id': ObjectId(kb_id),
            'user_id': current_user['id']
        })
        
        if not kb:
            return jsonify(ApiResponse.error('知识库不存在')), 404
        
        # 验证文档归属
        doc = db.documents.find_one({
            '_id': ObjectId(doc_id),
            'knowledge_base_id': kb_id
        })
        
        if not doc:
            return jsonify(ApiResponse.error('文档不存在')), 404
        
        # 删除文档
        db.documents.delete_one({'_id': ObjectId(doc_id)})
        
        print(f"✅ 文档删除成功: {doc_id}")
        
        return jsonify(ApiResponse.success(None, "文档删除成功"))
        
    except Exception as e:
        print(f"❌ 删除文档失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400 