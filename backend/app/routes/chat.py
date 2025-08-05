# 聊天相关路由模块
# 提供对话管理、消息发送、流式聊天等功能

from flask import Blueprint, request, jsonify, Response, stream_template
from app.services.database import get_db
from app.services.ollama import OllamaService
from app.services.chat_service import ChatService
from app.services.activity_service import activity_service
from app.utils.auth import token_required
from app.utils.response import ApiResponse, handle_exception, validate_pagination, validate_required_fields, sanitize_data, serialize_mongo_data
from bson import ObjectId
from datetime import datetime
import json
import time

# 创建聊天蓝图
chat_bp = Blueprint('chat', __name__)
# 初始化Ollama服务和聊天服务
ollama_service = OllamaService()
chat_service = ChatService()

@chat_bp.route('/conversations', methods=['GET'])
@chat_bp.route('/conversations/', methods=['GET'])
@token_required
@handle_exception
def get_conversations(current_user):
    """
    获取对话列表
    支持分页、搜索、按智能体筛选等功能
    """
    try:
        print(f"🔍 获取对话列表 - 用户: {current_user['username']}")
        
        db = get_db()
        print(f"📊 数据库类型: {type(db)}")
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        agent_id = request.args.get('agent_id', '')
        search = request.args.get('search', '')
        
        print(f"📝 查询参数: page={page}, limit={limit}, agent_id={agent_id}, search={search}")
        
        # 验证分页参数
        page, limit = validate_pagination(page, limit)
        
        # 构建查询条件
        query = {'user_id': current_user['id']}
        
        if agent_id:
            query['agent_id'] = agent_id
        
        if search:
            query['title'] = {'$regex': search, '$options': 'i'}
        
        print(f"🔍 查询条件: {query}")
        
        # 计算总数
        total = db.conversations.count_documents(query)
        print(f"📊 对话总数: {total}")
        
        # 获取分页数据
        skip = (page - 1) * limit
        conversations = list(db.conversations.find(query)
                           .skip(skip)
                           .limit(limit)
                           .sort('updated_at', -1))
        print(f"📊 获取到 {len(conversations)} 个对话")
        
        # 格式化数据并获取智能体信息
        for conv in conversations:
            conv['id'] = str(conv['_id'])
            conv['created_at'] = conv['created_at'].isoformat() if conv.get('created_at') else None
            conv['updated_at'] = conv['updated_at'].isoformat() if conv.get('updated_at') else None
            
            # 获取智能体或模型信息
            if conv.get('type') == 'agent' and conv.get('agent_id'):
                agent = db.agents.find_one({'_id': ObjectId(conv['agent_id'])})
                conv['agent_name'] = agent['name'] if agent else '未知智能体'
            elif conv.get('type') == 'model' and conv.get('model_id'):
                model = db.models.find_one({'_id': ObjectId(conv['model_id'])})
                conv['model_name'] = model['name'] if model else '未知模型'
            
            # 确保所有ObjectId都转换为字符串
            if 'agent_id' in conv and isinstance(conv['agent_id'], ObjectId):
                conv['agent_id'] = str(conv['agent_id'])
            if 'model_id' in conv and isinstance(conv['model_id'], ObjectId):
                conv['model_id'] = str(conv['model_id'])
            
            del conv['_id']
        
        print("✅ 对话列表获取成功")
        
        # 序列化数据以处理 ObjectId 和 datetime
        serialized_conversations = serialize_mongo_data(conversations)
        
        return jsonify(ApiResponse.success({
            'data': serialized_conversations,
            'total': total,
            'page': page,
            'page_size': limit
        }, "获取对话列表成功"))
        
    except Exception as e:
        print(f"❌ 获取对话列表失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify(ApiResponse.error(str(e))), 400

@chat_bp.route('/conversations', methods=['POST'])
@chat_bp.route('/conversations/', methods=['POST'])
@token_required
@handle_exception
def create_conversation(current_user):
    """
    创建新对话
    支持智能体对话和模型对话两种类型
    """
    try:
        data = request.get_json()
        print(f"📝 创建对话数据: {data}")
        
        # 验证必需字段
        if data.get('type') == 'agent':
            required_fields = ['agent_id']
        elif data.get('type') == 'model':
            # 对于模型对话，不再要求必须传递model_id，因为模型选择在聊天界面进行
            required_fields = []
        else:
            return jsonify(ApiResponse.error('对话类型必须为 agent 或 model')), 400
        
        validate_required_fields(data, required_fields)
        
        db = get_db()
        
        # 验证智能体是否存在
        if data.get('type') == 'agent':
            agent = db.agents.find_one({'_id': ObjectId(data['agent_id'])})
            if not agent:
                return jsonify(ApiResponse.error('智能体不存在')), 404
        elif data.get('type') == 'model':
            # 对于模型对话，如果提供了model_id则验证，否则不验证
            if data.get('model_id'):
                model = db.models.find_one({'_id': ObjectId(data['model_id'])})
                if not model:
                    return jsonify(ApiResponse.error('模型不存在')), 404
            else:
                # 如果没有提供model_id，尝试设置第一个有效模型作为默认模型
                first_model = db.models.find_one({
                    'status': {'$in': ['active', 'available']}
                })
                if first_model:
                    data['model_id'] = str(first_model['_id'])
                    print(f"🔄 自动设置默认模型: {first_model.get('name', '未知')}")
        
        # 创建对话数据
        conversation_data = {
            'user_id': current_user['id'],
            'type': data['type'],
            'title': data.get('title', '新对话'),
            'status': 'active',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # 根据类型添加相应的ID
        if data.get('type') == 'agent' and data.get('agent_id'):
            conversation_data['agent_id'] = data['agent_id']
        elif data.get('type') == 'model' and data.get('model_id'):
            conversation_data['model_id'] = data['model_id']
        
        print(f"💾 保存对话数据: {conversation_data}")
        
        # 插入数据库
        result = db.conversations.insert_one(conversation_data)
        conversation_data['id'] = str(result.inserted_id)
        
        # 格式化时间
        conversation_data['created_at'] = conversation_data['created_at'].isoformat()
        conversation_data['updated_at'] = conversation_data['updated_at'].isoformat()
        
        # 确保所有ObjectId都转换为字符串
        if 'agent_id' in conversation_data and isinstance(conversation_data['agent_id'], ObjectId):
            conversation_data['agent_id'] = str(conversation_data['agent_id'])
        if 'model_id' in conversation_data and isinstance(conversation_data['model_id'], ObjectId):
            conversation_data['model_id'] = str(conversation_data['model_id'])
        
        print(f"✅ 对话创建成功: {conversation_data['title']}")
        
        # 序列化数据以处理 ObjectId 和 datetime
        serialized_data = serialize_mongo_data(conversation_data)
        
        return jsonify(ApiResponse.success(serialized_data, "对话创建成功")), 201
        
    except Exception as e:
        print(f"❌ 创建对话失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

@chat_bp.route('/conversations/<conversation_id>', methods=['GET'])
@token_required
@handle_exception
def get_conversation(current_user, conversation_id):
    """
    获取对话详情
    """
    try:
        # 验证ID格式
        if not ObjectId.is_valid(conversation_id):
            return jsonify(ApiResponse.error('无效的对话ID')), 400
        
        db = get_db()
        
        # 验证对话归属
        conversation = db.conversations.find_one({
            '_id': ObjectId(conversation_id),
            'user_id': current_user['id']
        })
        
        if not conversation:
            return jsonify(ApiResponse.error('对话不存在')), 404
        
        # 格式化数据
        conversation['id'] = str(conversation['_id'])
        conversation['created_at'] = conversation['created_at'].isoformat() if conversation.get('created_at') else None
        conversation['updated_at'] = conversation['updated_at'].isoformat() if conversation.get('updated_at') else None
        
        # 获取智能体信息
        if conversation.get('agent_id'):
            agent = db.agents.find_one({'_id': ObjectId(conversation['agent_id'])})
            conversation['agent_name'] = agent['name'] if agent else '未知智能体'
        
        del conversation['_id']
        
        # 序列化数据以处理 ObjectId 和 datetime
        serialized_conversation = serialize_mongo_data(conversation)
        
        return jsonify(ApiResponse.success(serialized_conversation, "获取对话详情成功"))
        
    except Exception as e:
        return jsonify(ApiResponse.error(str(e))), 400

@chat_bp.route('/conversations/<conversation_id>/messages', methods=['GET'])
@token_required
@handle_exception
def get_messages(current_user, conversation_id):
    """
    获取对话消息
    支持分页获取消息历史
    """
    print(f"🔍 开始获取消息 - 对话ID: {conversation_id}, 用户: {current_user['username']}")
    
    try:
        # 验证ID格式
        if not ObjectId.is_valid(conversation_id):
            print(f"❌ 无效的对话ID: {conversation_id}")
            return jsonify(ApiResponse.error('无效的对话ID')), 400
        
        db = get_db()
        print(f"✅ 数据库连接成功")
        
        # 验证对话归属
        try:
            conversation = db.conversations.find_one({
                '_id': ObjectId(conversation_id),
                'user_id': current_user['id']
            })
            print(f"🔍 对话查询结果: {conversation is not None}")
        except Exception as e:
            print(f"❌ 查询对话失败: {str(e)}")
            return jsonify(ApiResponse.error(f'查询对话失败: {str(e)}')), 500
        
        if not conversation:
            print(f"❌ 对话不存在或不属于用户: {conversation_id}")
            return jsonify(ApiResponse.error('对话不存在')), 404
        
        print(f"✅ 找到对话: {conversation.get('title', '未知')}")
        
        # 获取消息 - 使用ObjectId查询
        messages = []
        try:
            print(f"🔍 开始查询消息，conversation_id: {conversation_id}")
            messages = list(db.messages.find({
                'conversation_id': ObjectId(conversation_id)
            }).sort('created_at', 1))
            print(f"🔍 使用ObjectId查询成功，找到 {len(messages)} 条消息")
        except Exception as e:
            print(f"❌ 查询消息失败: {str(e)}")
            print(f"🔍 尝试使用字符串查询...")
            try:
                messages = list(db.messages.find({
                    'conversation_id': conversation_id
                }).sort('created_at', 1))
                print(f"🔍 字符串查询成功，找到 {len(messages)} 条消息")
            except Exception as e2:
                print(f"❌ 字符串查询也失败: {str(e2)}")
                # 如果查询失败，返回空列表而不是抛出异常
                messages = []
        
        print(f"🔍 最终获取消息 - 对话ID: {conversation_id}, 找到 {len(messages)} 条消息")
        
        # 格式化消息数据
        try:
            for msg in messages:
                msg['id'] = str(msg['_id'])
                msg['created_at'] = msg['created_at'].isoformat() if msg.get('created_at') else None
                del msg['_id']
            print(f"✅ 消息格式化成功")
        except Exception as e:
            print(f"❌ 消息格式化失败: {str(e)}")
            return jsonify(ApiResponse.error(f'消息格式化失败: {str(e)}')), 500
        
        # 序列化数据以处理 ObjectId 和 datetime
        try:
            serialized_messages = serialize_mongo_data(messages)
            print("✅ 消息数据序列化成功")
        except Exception as e:
            print(f"❌ 消息序列化失败: {str(e)}")
            return jsonify(ApiResponse.error(f'消息序列化失败: {str(e)}')), 500
        
        return jsonify(ApiResponse.success(serialized_messages, "获取消息列表成功"))
        
    except Exception as e:
        print(f"❌ 获取消息异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify(ApiResponse.error(f"获取消息失败: {str(e)}")), 500

@chat_bp.route('/send', methods=['POST'])
@token_required
@handle_exception
def send_message(current_user):
    """
    发送消息并获取AI回复
    支持同步回复模式
    """
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['conversation_id', 'content']
        validate_required_fields(data, required_fields)
        
        conversation_id = data['conversation_id']
        content = data['content']
        
        # 验证ID格式
        if not ObjectId.is_valid(conversation_id):
            return jsonify(ApiResponse.error('无效的对话ID')), 400
        
        db = get_db()
        
        # 验证对话归属
        conversation = db.conversations.find_one({
            '_id': ObjectId(conversation_id),
            'user_id': current_user['id']
        })
        
        if not conversation:
            return jsonify(ApiResponse.error('对话不存在')), 404
        
        # 根据对话类型获取智能体或模型信息
        if conversation.get('type') == 'agent':
            agent = db.agents.find_one({'_id': ObjectId(conversation['agent_id'])})
            if not agent:
                return jsonify(ApiResponse.error('智能体不存在')), 404
            target_name = agent['name']
        elif conversation.get('type') == 'model':
            model = db.models.find_one({'_id': ObjectId(conversation['model_id'])})
            if not model:
                return jsonify(ApiResponse.error('模型不存在')), 404
            target_name = model['name']
        else:
            return jsonify(ApiResponse.error('无效的对话类型')), 400
        
        # 保存用户消息
        user_message = {
            'conversation_id': conversation_id,
            'content': content,
            'type': 'user',
            'attachments': data.get('attachments', []),
            'metadata': data.get('metadata', {}),
            'user_id': current_user['id'],
            'created_at': datetime.now()
        }
        
        message_result = db.messages.insert_one(user_message)
        user_message_id = str(message_result.inserted_id)
        
        # 更新对话时间
        db.conversations.update_one(
            {'_id': ObjectId(conversation_id)},
            {'$set': {'updated_at': datetime.now()}}
        )
        
        # 生成AI回复
        try:
            print(f"🤖 开始生成AI回复 - 对话类型: {conversation.get('type')}")
            
            if conversation.get('type') == 'agent':
                print(f"🔧 使用智能体: {agent.get('name', '未知')}")
                ai_response = chat_service.generate_response_sync(
                    conversation_id=conversation_id,
                    agent=agent,
                    user_message=content
                )
            else:  # model type
                print(f"🔧 使用模型: {model.get('name', '未知')}")
                ai_response = chat_service.generate_model_response_sync(
                    conversation_id=conversation_id,
                    model=model,
                    user_message=content
                )
            
            print(f"✅ AI回复生成成功，长度: {len(ai_response)}")
            
            # 保存AI回复
            ai_message = {
                'conversation_id': conversation_id,
                'content': ai_response,
                'type': 'assistant',
                'attachments': [],
                'metadata': {},
                'user_id': current_user['id'],
                'created_at': datetime.now()
            }
            
            ai_message_result = db.messages.insert_one(ai_message)
            ai_message_id = str(ai_message_result.inserted_id)
            
            # 记录活动
            try:
                activity_service.record_conversation_started(
                    current_user['id'],
                    target_name,
                    conversation_id
                )
            except Exception as e:
                print(f"⚠️ 记录活动失败: {str(e)}")
            
            # 序列化数据以处理 ObjectId 和 datetime
            response_data = {
                'user_message_id': user_message_id,
                'ai_message_id': ai_message_id,
                'response': ai_response
            }
            serialized_data = serialize_mongo_data(response_data)
            
            return jsonify(ApiResponse.success(serialized_data, "消息发送成功"))
            
        except Exception as e:
            print(f"❌ 生成AI回复失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify(ApiResponse.error(f"生成回复失败: {str(e)}")), 500
        
    except Exception as e:
        print(f"❌ 发送消息失败: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400

@chat_bp.route('/stream', methods=['POST'])
@token_required
@handle_exception
def stream_chat(current_user):
    """
    流式聊天
    支持实时流式回复，提供更好的用户体验
    """
    try:
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['conversation_id', 'content']
        validate_required_fields(data, required_fields)
        
        conversation_id = data['conversation_id']
        content = data['content']
        show_thinking = data.get('show_thinking', False)
        model_id = data.get('model_id')
        attachments = data.get('attachments', [])
        
        print(f"🔄 开始流式聊天 - 对话ID: {conversation_id}, 内容: {content[:50]}...")
        print(f"🔧 深度思考: {show_thinking}, 模型ID: {model_id}, 附件数量: {len(attachments)}")
        
        # 验证ID格式
        if not ObjectId.is_valid(conversation_id):
            print(f"❌ 无效的对话ID: {conversation_id}")
            return jsonify(ApiResponse.error('无效的对话ID')), 400
        
        db = get_db()
        
        # 验证对话归属
        try:
            conversation = db.conversations.find_one({
                '_id': ObjectId(conversation_id),
                'user_id': current_user['id']
            })
            
            if not conversation:
                print(f"❌ 对话不存在或不属于用户: {conversation_id}")
                return jsonify(ApiResponse.error('对话不存在')), 404
                
            print(f"✅ 找到对话: {conversation.get('title', '未知')}")
        except Exception as e:
            print(f"❌ 查询对话失败: {str(e)}")
            return jsonify(ApiResponse.error(f'查询对话失败: {str(e)}')), 500
        
        # 根据对话类型获取智能体或模型信息
        try:
            if conversation.get('type') == 'agent':
                agent = db.agents.find_one({'_id': ObjectId(conversation['agent_id'])})
                if not agent:
                    return jsonify(ApiResponse.error('智能体不存在')), 404
                target_name = agent['name']
                model = None
            elif conversation.get('type') == 'model':
                # 如果指定了模型ID，使用指定的模型，否则使用对话的默认模型
                if model_id:
                    model = db.models.find_one({'_id': ObjectId(model_id)})
                    if not model:
                        return jsonify(ApiResponse.error('指定的模型不存在')), 404
                    print(f"✅ 使用指定模型: {model.get('name', '未知')}")
                else:
                    # 检查对话是否有默认模型
                    if conversation.get('model_id'):
                        model = db.models.find_one({'_id': ObjectId(conversation['model_id'])})
                        if not model:
                            return jsonify(ApiResponse.error('对话的默认模型不存在')), 404
                        print(f"✅ 使用对话默认模型: {model.get('name', '未知')}")
                    else:
                        # 没有指定模型且对话也没有默认模型，尝试使用第一个有效模型
                        first_model = db.models.find_one({
                            'status': {'$in': ['active', 'available']}
                        })
                        if first_model:
                            model = first_model
                            print(f"✅ 使用第一个有效模型: {model.get('name', '未知')}")
                            # 更新对话的默认模型
                            db.conversations.update_one(
                                {'_id': ObjectId(conversation_id)},
                                {'$set': {'model_id': str(first_model['_id'])}}
                            )
                        else:
                            return jsonify(ApiResponse.error('没有可用的模型，请先在模型管理中创建模型')), 400
                target_name = model['name']
                agent = None
            else:
                return jsonify(ApiResponse.error('无效的对话类型')), 400
                
            print(f"✅ 找到目标: {target_name}")
        except Exception as e:
            print(f"❌ 查询目标失败: {str(e)}")
            return jsonify(ApiResponse.error(f'查询目标失败: {str(e)}')), 500
        
        # 保存用户消息
        try:
            user_message = {
                'conversation_id': ObjectId(conversation_id),  # 确保保存为ObjectId类型
                'content': content,
                'type': 'user',
                'attachments': attachments,
                'metadata': {
                    'show_thinking': show_thinking,
                    'model_id': model_id
                },
                'user_id': current_user['id'],
                'created_at': datetime.now()
            }
            
            message_result = db.messages.insert_one(user_message)
            user_message_id = str(message_result.inserted_id)
            print(f"✅ 用户消息保存成功: {user_message_id}")
            
            # 更新对话时间
            db.conversations.update_one(
                {'_id': ObjectId(conversation_id)},
                {'$set': {'updated_at': datetime.now()}}
            )
        except Exception as e:
            print(f"❌ 保存用户消息失败: {str(e)}")
            return jsonify(ApiResponse.error(f'保存用户消息失败: {str(e)}')), 500
        
        def generate():
            """
            生成流式响应的生成器函数
            """
            try:
                # 流式生成AI回复
                full_response = ""
                print(f"🤖 开始流式生成AI回复 - 对话类型: {conversation.get('type')}")
                
                if conversation.get('type') == 'agent' and agent:
                    # 智能体对话
                    print(f"🔧 使用智能体: {agent.get('name', '未知')}")
                    try:
                        for chunk in chat_service.stream_response(
                            conversation_id=conversation_id,
                            agent=agent,
                            user_message=content
                        ):
                            full_response += chunk
                            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                    except Exception as e:
                        print(f"❌ 智能体流式生成失败: {str(e)}")
                        error_msg = f"抱歉，智能体 {agent.get('name', '未知')} 暂时无法响应：{str(e)}"
                        yield f"data: {json.dumps({'chunk': error_msg})}\n\n"
                        full_response = error_msg
                elif conversation.get('type') == 'model' and model:
                    # 模型对话
                    print(f"🔧 使用模型: {model.get('name', '未知')}")
                    try:
                        for chunk in chat_service.stream_model_response(
                            conversation_id=conversation_id,
                            model=model,
                            user_message=content,
                            show_thinking=show_thinking
                        ):
                            full_response += chunk
                            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                    except Exception as e:
                        print(f"❌ 模型流式生成失败: {str(e)}")
                        error_msg = f"抱歉，模型 {model.get('name', '未知')} 暂时无法响应：{str(e)}"
                        yield f"data: {json.dumps({'chunk': error_msg})}\n\n"
                        full_response = error_msg
                else:
                    error_msg = "抱歉，无法找到有效的智能体或模型"
                    yield f"data: {json.dumps({'chunk': error_msg})}\n\n"
                    full_response = error_msg
                
                print(f"✅ 流式AI回复生成成功，长度: {len(full_response)}")
                
                # 保存完整的AI回复
                try:
                    ai_message = {
                        'conversation_id': ObjectId(conversation_id),  # 确保保存为ObjectId类型
                        'content': full_response,
                        'type': 'assistant',
                        'attachments': [],
                        'metadata': {},
                        'user_id': current_user['id'],
                        'created_at': datetime.now()
                    }
                    
                    ai_message_result = db.messages.insert_one(ai_message)
                    ai_message_id = str(ai_message_result.inserted_id)
                    print(f"✅ AI消息保存成功: {ai_message_id}")
                except Exception as e:
                    print(f"❌ 保存AI消息失败: {str(e)}")
                    ai_message_id = None
                
                # 记录活动
                try:
                    activity_service.record_conversation_started(
                        current_user['id'],
                        target_name,
                        conversation_id
                    )
                except Exception as e:
                    print(f"⚠️ 记录活动失败: {str(e)}")
                
                # 发送完成信号
                yield f"data: {json.dumps({'done': True, 'message_id': ai_message_id})}\n\n"
                
            except Exception as e:
                print(f"❌ 流式生成失败: {str(e)}")
                import traceback
                traceback.print_exc()
                error_msg = f"抱歉，生成回复时遇到错误：{str(e)}"
                yield f"data: {json.dumps({'chunk': error_msg})}\n\n"
                yield f"data: {json.dumps({'done': True, 'message_id': None})}\n\n"
        
        # 创建SSE响应
        response = Response(generate(), mimetype='text/event-stream')
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Connection'] = 'keep-alive'
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
        
    except Exception as e:
        print(f"❌ 流式聊天异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify(ApiResponse.error(str(e))), 400

@chat_bp.route('/conversations/<conversation_id>', methods=['DELETE'])
@token_required
@handle_exception
def delete_conversation(current_user, conversation_id):
    """
    删除对话
    同时删除相关的所有消息
    """
    try:
        print(f"🗑️ 开始删除对话: {conversation_id}")
        
        # 验证ID格式
        if not ObjectId.is_valid(conversation_id):
            return jsonify(ApiResponse.error('无效的对话ID')), 400
        
        db = get_db()
        
        # 验证对话归属
        conversation = db.conversations.find_one({
            '_id': ObjectId(conversation_id),
            'user_id': current_user['id']
        })
        
        if not conversation:
            return jsonify(ApiResponse.error('对话不存在')), 404
        
        print(f"✅ 找到对话: {conversation.get('title', '未知')}")
        
        # 先删除消息，再删除对话
        try:
            start_time = time.time()
            # 删除所有相关消息
            messages_deleted = db.messages.delete_many({'conversation_id': ObjectId(conversation_id)})
            print(f"🗑️ 删除了 {messages_deleted.deleted_count} 条消息 (耗时: {time.time() - start_time:.4f}s)")
            
            start_time = time.time()
            # 删除对话
            conversation_deleted = db.conversations.delete_one({'_id': ObjectId(conversation_id)})
            print(f"🗑️ 删除了 {conversation_deleted.deleted_count} 个对话 (耗时: {time.time() - start_time:.4f}s)")
            
            if conversation_deleted.deleted_count > 0:
                print("✅ 对话删除成功")
                return jsonify(ApiResponse.success(None, "对话删除成功"))
            else:
                print("❌ 对话删除失败: 未找到对话进行删除")
                return jsonify(ApiResponse.error("对话删除失败")), 500
                
        except Exception as e:
            print(f"❌ 删除操作失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify(ApiResponse.error(f"删除失败: {str(e)}")), 500
        
    except Exception as e:
        print(f"❌ 删除对话异常: {str(e)}")
        return jsonify(ApiResponse.error(str(e))), 400 