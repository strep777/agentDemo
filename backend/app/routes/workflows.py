from flask import Blueprint, request, jsonify
from app.services.database import get_db
from app.utils.auth import token_required
from app.utils.response import ApiResponse, handle_exception, validate_required_fields, serialize_mongo_data
from bson import ObjectId
from datetime import datetime

workflows_bp = Blueprint('workflows', __name__)

@workflows_bp.route('', methods=['GET'])
@workflows_bp.route('/', methods=['GET'])
@token_required
@handle_exception
def get_workflows(current_user):
    """获取工作流列表"""
    try:
        print(f"🔍 获取工作流列表 - 用户: {current_user['username']}")
        
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
        total = db.workflows.count_documents(query)
        
        # 获取分页数据
        skip = (page - 1) * limit
        workflows = list(db.workflows.find(query)
                        .skip(skip)
                        .limit(limit)
                        .sort('updated_at', -1))
        
        # 格式化数据
        for workflow in workflows:
            workflow['id'] = str(workflow['_id'])
            workflow['created_at'] = workflow['created_at'].isoformat() if workflow.get('created_at') else None
            workflow['updated_at'] = workflow['updated_at'].isoformat() if workflow.get('updated_at') else None
            del workflow['_id']
        
        print(f"✅ 获取到 {len(workflows)} 个工作流")
        
        # 序列化数据以处理 ObjectId 和 datetime
        serialized_workflows = serialize_mongo_data(workflows)
        
        return jsonify(ApiResponse.success({
            'data': serialized_workflows,
            'total': total,
            'page': page,
            'page_size': limit
        }, "获取工作流列表成功"))
        
    except Exception as e:
        print(f"❌ 获取工作流列表失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

@workflows_bp.route('/<workflow_id>', methods=['GET'])
@token_required
@handle_exception
def get_workflow(current_user, workflow_id):
    """获取工作流详情"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(workflow_id):
            return jsonify(ApiResponse.error('无效的工作流ID')), 400
        
        db = get_db()
        
        # 验证工作流归属
        workflow = db.workflows.find_one({
            '_id': ObjectId(workflow_id),
            'user_id': current_user['id']
        })
        
        if not workflow:
            return jsonify(ApiResponse.error('工作流不存在')), 404
        
        # 格式化数据
        workflow['id'] = str(workflow['_id'])
        workflow['created_at'] = workflow['created_at'].isoformat() if workflow.get('created_at') else None
        workflow['updated_at'] = workflow['updated_at'].isoformat() if workflow.get('updated_at') else None
        del workflow['_id']
        
        # 序列化数据以处理 ObjectId 和 datetime
        serialized_workflow = serialize_mongo_data(workflow)
        
        return jsonify(ApiResponse.success(serialized_workflow, "获取工作流详情成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@workflows_bp.route('', methods=['POST'])
@workflows_bp.route('/', methods=['POST'])
@token_required
@handle_exception
def create_workflow(current_user):
    """创建工作流"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['name', 'description']
        validate_required_fields(data, required_fields)
        
        db = get_db()
        
        # 检查工作流名称是否重复
        existing_workflow = db.workflows.find_one({
            'user_id': current_user['id'],
            'name': data['name']
        })
        
        if existing_workflow:
            return jsonify(ApiResponse.error('工作流名称已存在')), 400
        
        # 创建工作流数据
        workflow_data = {
            'user_id': current_user['id'],
            'name': data['name'],
            'description': data['description'],
            'nodes': data.get('nodes', []),
            'edges': data.get('edges', []),
            'status': 'draft',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        result = db.workflows.insert_one(workflow_data)
        workflow_data['id'] = str(result.inserted_id)
        
        # 格式化时间
        workflow_data['created_at'] = workflow_data['created_at'].isoformat()
        workflow_data['updated_at'] = workflow_data['updated_at'].isoformat()
        
        print(f"✅ 工作流创建成功: {workflow_data['name']}")
        
        # 序列化数据以处理 ObjectId 和 datetime
        serialized_workflow_data = serialize_mongo_data(workflow_data)
        
        return jsonify(ApiResponse.success(serialized_workflow_data, "工作流创建成功")), 201
        
    except Exception as e:
        print(f"❌ 创建工作流失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

@workflows_bp.route('/<workflow_id>', methods=['PUT'])
@token_required
@handle_exception
def update_workflow(current_user, workflow_id):
    """更新工作流"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(workflow_id):
            return jsonify(ApiResponse.error('无效的工作流ID')), 400
        
        data = request.get_json()
        
        db = get_db()
        
        # 验证工作流归属
        workflow = db.workflows.find_one({
            '_id': ObjectId(workflow_id),
            'user_id': current_user['id']
        })
        
        if not workflow:
            return jsonify(ApiResponse.error('工作流不存在')), 404
        
        # 检查名称是否重复（排除当前工作流）
        if 'name' in data:
            existing_workflow = db.workflows.find_one({
                'user_id': current_user['id'],
                'name': data['name'],
                '_id': {'$ne': ObjectId(workflow_id)}
            })
            
            if existing_workflow:
                return jsonify(ApiResponse.error('工作流名称已存在')), 400
        
        # 更新工作流
        update_data = {
            'updated_at': datetime.now()
        }
        
        if 'name' in data:
            update_data['name'] = data['name']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'nodes' in data:
            update_data['nodes'] = data['nodes']
        if 'edges' in data:
            update_data['edges'] = data['edges']
        if 'status' in data:
            update_data['status'] = data['status']
        
        db.workflows.update_one(
            {'_id': ObjectId(workflow_id)},
            {'$set': update_data}
        )
        
        print(f"✅ 工作流更新成功: {workflow_id}")
        
        return jsonify(ApiResponse.success(None, "工作流更新成功"))
        
    except Exception as e:
        print(f"❌ 更新工作流失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

@workflows_bp.route('/<workflow_id>', methods=['DELETE'])
@token_required
@handle_exception
def delete_workflow(current_user, workflow_id):
    """删除工作流"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(workflow_id):
            return jsonify(ApiResponse.error('无效的工作流ID')), 400
        
        db = get_db()
        
        # 验证工作流归属
        workflow = db.workflows.find_one({
            '_id': ObjectId(workflow_id),
            'user_id': current_user['id']
        })
        
        if not workflow:
            return jsonify(ApiResponse.error('工作流不存在')), 404
        
        # 删除工作流
        db.workflows.delete_one({'_id': ObjectId(workflow_id)})
        
        print(f"✅ 工作流删除成功: {workflow_id}")
        
        return jsonify(ApiResponse.success(None, "工作流删除成功"))
        
    except Exception as e:
        print(f"❌ 删除工作流失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

@workflows_bp.route('/<workflow_id>/execute', methods=['POST'])
@token_required
@handle_exception
def execute_workflow(current_user, workflow_id):
    """执行工作流"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(workflow_id):
            return jsonify(ApiResponse.error('无效的工作流ID')), 400
        
        data = request.get_json()
        
        db = get_db()
        
        # 验证工作流归属
        workflow = db.workflows.find_one({
            '_id': ObjectId(workflow_id),
            'user_id': current_user['id']
        })
        
        if not workflow:
            return jsonify(ApiResponse.error('工作流不存在')), 404
        
        # 记录执行历史
        execution_data = {
            'workflow_id': workflow_id,
            'user_id': current_user['id'],
            'input_data': data.get('input', {}),
            'status': 'running',
            'started_at': datetime.now(),
            'created_at': datetime.now()
        }
        
        result = db.execution_history.insert_one(execution_data)
        execution_id = str(result.inserted_id)
        
        print(f"✅ 工作流执行开始: {workflow_id}")
        
        return jsonify(ApiResponse.success({
            'execution_id': execution_id
        }, "工作流执行开始"))
        
    except Exception as e:
        print(f"❌ 执行工作流失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

@workflows_bp.route('/executions', methods=['GET'])
@token_required
@handle_exception
def get_executions(current_user):
    """获取执行历史"""
    try:
        print(f"🔍 获取执行历史 - 用户: {current_user['username']}")
        
        db = get_db()
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        workflow_id = request.args.get('workflow_id', '')
        
        # 构建查询条件
        query = {'user_id': current_user['id']}
        if workflow_id:
            query['workflow_id'] = workflow_id
        
        # 计算总数
        total = db.execution_history.count_documents(query)
        
        # 获取分页数据
        skip = (page - 1) * limit
        executions = list(db.execution_history.find(query)
                         .skip(skip)
                         .limit(limit)
                         .sort('created_at', -1))
        
        # 格式化数据
        for execution in executions:
            execution['id'] = str(execution['_id'])
            execution['created_at'] = execution['created_at'].isoformat() if execution.get('created_at') else None
            execution['started_at'] = execution['started_at'].isoformat() if execution.get('started_at') else None
            execution['completed_at'] = execution['completed_at'].isoformat() if execution.get('completed_at') else None
            del execution['_id']
        
        print(f"✅ 获取到 {len(executions)} 条执行记录")
        
        return jsonify(ApiResponse.success({
            'data': executions,
            'total': total,
            'page': page,
            'page_size': limit
        }, "获取执行历史成功"))
        
    except Exception as e:
        print(f"❌ 获取执行历史失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

@workflows_bp.route('/executions/<execution_id>', methods=['GET'])
@token_required
@handle_exception
def get_execution(current_user, execution_id):
    """获取执行详情"""
    try:
        # 验证ID格式
        if not ObjectId.is_valid(execution_id):
            return jsonify(ApiResponse.error('无效的执行ID')), 400
        
        db = get_db()
        
        # 验证执行记录归属
        execution = db.execution_history.find_one({
            '_id': ObjectId(execution_id),
            'user_id': current_user['id']
        })
        
        if not execution:
            return jsonify(ApiResponse.error('执行记录不存在')), 404
        
        # 格式化数据
        execution['id'] = str(execution['_id'])
        execution['created_at'] = execution['created_at'].isoformat() if execution.get('created_at') else None
        execution['started_at'] = execution['started_at'].isoformat() if execution.get('started_at') else None
        execution['completed_at'] = execution['completed_at'].isoformat() if execution.get('completed_at') else None
        del execution['_id']
        
        return jsonify(ApiResponse.success(execution, "获取执行详情成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400 