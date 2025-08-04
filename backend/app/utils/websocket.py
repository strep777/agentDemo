"""
WebSocket工具模块
提供WebSocket连接管理功能
"""

from flask_socketio import SocketIO

# 全局SocketIO实例
socketio = None

def init_websocket(app_socketio: SocketIO):
    """初始化WebSocket"""
    global socketio
    socketio = app_socketio

def get_socketio() -> SocketIO:
    """获取SocketIO实例"""
    return socketio 