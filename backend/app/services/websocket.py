"""
WebSocket服务模块
提供实时通信功能，用于工作流执行状态、聊天消息等
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from typing import Dict, Any
import json
import logging
from datetime import datetime
from flask import request

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketService:
    """WebSocket服务类"""
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.active_connections: Dict[str, Any] = {}
        self.setup_events()
    
    def setup_events(self):
        """设置WebSocket事件处理器"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """客户端连接事件"""
            client_id = request.sid
            self.active_connections[client_id] = {
                'user_id': None,
                'rooms': set()
            }
            logger.info(f"客户端连接: {client_id}")
            emit('connected', {'status': 'connected', 'client_id': client_id})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """客户端断开连接事件"""
            client_id = request.sid
            if client_id in self.active_connections:
                # 清理房间
                for room in self.active_connections[client_id]['rooms']:
                    leave_room(room)
                del self.active_connections[client_id]
            logger.info(f"客户端断开连接: {client_id}")
        
        @self.socketio.on('authenticate')
        def handle_authenticate(data):
            """用户认证事件"""
            client_id = request.sid
            user_id = data.get('user_id')
            token = data.get('token')
            
            if user_id and token:
                self.active_connections[client_id]['user_id'] = user_id
                # 加入用户房间
                join_room(f"user_{user_id}")
                self.active_connections[client_id]['rooms'].add(f"user_{user_id}")
                emit('authenticated', {'status': 'success', 'user_id': user_id})
                logger.info(f"用户认证成功: {user_id}")
            else:
                emit('authenticated', {'status': 'error', 'message': '认证失败'})
        
        @self.socketio.on('join_chat')
        def handle_join_chat(data):
            """加入聊天房间"""
            client_id = request.sid
            chat_id = data.get('chat_id')
            user_id = data.get('user_id')
            
            if chat_id and user_id:
                room_name = f"chat_{chat_id}"
                join_room(room_name)
                self.active_connections[client_id]['rooms'].add(room_name)
                emit('joined_chat', {'chat_id': chat_id, 'status': 'joined'})
                logger.info(f"用户 {user_id} 加入聊天 {chat_id}")
        
        @self.socketio.on('leave_chat')
        def handle_leave_chat(data):
            """离开聊天房间"""
            client_id = request.sid
            chat_id = data.get('chat_id')
            
            if chat_id:
                room_name = f"chat_{chat_id}"
                leave_room(room_name)
                if room_name in self.active_connections[client_id]['rooms']:
                    self.active_connections[client_id]['rooms'].remove(room_name)
                emit('left_chat', {'chat_id': chat_id, 'status': 'left'})
        
        @self.socketio.on('join_workflow')
        def handle_join_workflow(data):
            """加入工作流房间"""
            client_id = request.sid
            workflow_id = data.get('workflow_id')
            user_id = data.get('user_id')
            
            if workflow_id and user_id:
                room_name = f"workflow_{workflow_id}"
                join_room(room_name)
                self.active_connections[client_id]['rooms'].add(room_name)
                emit('joined_workflow', {'workflow_id': workflow_id, 'status': 'joined'})
                logger.info(f"用户 {user_id} 加入工作流 {workflow_id}")
        
        @self.socketio.on('workflow_progress')
        def handle_workflow_progress(data):
            """工作流执行进度"""
            workflow_id = data.get('workflow_id')
            step = data.get('step')
            status = data.get('status')
            message = data.get('message')
            
            if workflow_id:
                room_name = f"workflow_{workflow_id}"
                emit('workflow_update', {
                    'workflow_id': workflow_id,
                    'step': step,
                    'status': status,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                }, room=room_name)
        
        @self.socketio.on('chat_message')
        def handle_chat_message(data):
            """聊天消息事件"""
            chat_id = data.get('chat_id')
            message = data.get('message')
            user_id = data.get('user_id')
            
            if chat_id and message:
                room_name = f"chat_{chat_id}"
                emit('new_message', {
                    'chat_id': chat_id,
                    'message': message,
                    'user_id': user_id,
                    'timestamp': datetime.now().isoformat()
                }, room=room_name)
        
        @self.socketio.on('typing')
        def handle_typing(data):
            """用户正在输入事件"""
            chat_id = data.get('chat_id')
            user_id = data.get('user_id')
            is_typing = data.get('is_typing')
            
            if chat_id:
                room_name = f"chat_{chat_id}"
                emit('user_typing', {
                    'chat_id': chat_id,
                    'user_id': user_id,
                    'is_typing': is_typing
                }, room=room_name)
    
    def broadcast_workflow_status(self, workflow_id: str, status: str, message: str = ""):
        """广播工作流状态"""
        room_name = f"workflow_{workflow_id}"
        self.socketio.emit('workflow_status', {
            'workflow_id': workflow_id,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }, room=room_name)
    
    def broadcast_chat_message(self, chat_id: str, message: Dict[str, Any]):
        """广播聊天消息"""
        room_name = f"chat_{chat_id}"
        self.socketio.emit('new_message', message, room=room_name)
    
    def broadcast_notification(self, user_id: str, notification: Dict[str, Any]):
        """广播通知"""
        room_name = f"user_{user_id}"
        self.socketio.emit('notification', notification, room=room_name)
    
    def get_active_connections(self) -> Dict[str, Any]:
        """获取活跃连接"""
        return self.active_connections

# 全局WebSocket服务实例
websocket_service = None

def init_websocket(socketio: SocketIO):
    """初始化WebSocket服务"""
    global websocket_service
    websocket_service = WebSocketService(socketio)
    logger.info("WebSocket服务初始化完成")

def get_websocket_service() -> WebSocketService:
    """获取WebSocket服务实例"""
    return websocket_service 