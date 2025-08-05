from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import logging
from logging.handlers import RotatingFileHandler

# 创建Flask应用
app = Flask(__name__)

# 设置开发环境
if not os.environ.get('FLASK_ENV'):
    os.environ['FLASK_ENV'] = 'development'
if not os.environ.get('FLASK_DEBUG'):
    os.environ['FLASK_DEBUG'] = '1'

# 配置日志
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/agent_system.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('AI智能体管理系统启动')

# 配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['MONGODB_URI'] = os.environ.get('MONGODB_URI', 'mongodb://root:qwbt123@172.16.156.100:27017/')
app.config['OLLAMA_BASE_URL'] = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')

# 允许跨域请求
CORS(app, 
     resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://172.16.156.97:5173"]}},
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     expose_headers=["Content-Type", "Authorization"])

# 初始化SocketIO
socketio = SocketIO(
    app, 
    cors_allowed_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://172.16.156.97:5173"], 
    async_mode='eventlet',
    logger=False,
    engineio_logger=False
)

# 延迟导入以避免循环导入
def register_blueprints():
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

# 全局错误处理
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Not found', 'message': '请求的资源不存在'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'error': 'Internal server error', 'message': '服务器内部错误'}, 500

@app.errorhandler(Exception)
def handle_exception(error):
    return {'error': 'Unexpected error', 'message': str(error)}, 500

def init_database():
    try:
        from app.services.database import init_db
        init_db()
        app.logger.info("数据库连接成功")
    except Exception as e:
        app.logger.error(f"数据库连接失败: {e}")
        raise e

# 健康检查端点
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'AI Agent Management System is running'}

# 根路径重定向到健康检查
@app.route('/')
def root():
    return {'status': 'healthy', 'message': 'AI Agent Management System is running'}

# 调试信息端点（仅开发环境）
@app.route('/debug')
def debug_info():
    if app.debug:
        return {
            'debug': True,
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'database_uri': app.config['MONGODB_URI'],
            'ollama_url': app.config['OLLAMA_BASE_URL']
        }
    else:
        return {'error': 'Debug endpoint not available in production'}, 404

# CORS预检请求处理
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = app.make_default_options_response()
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

# 为流式响应添加CORS处理
@app.after_request
def after_request(response):
    if request.endpoint and 'stream' in request.endpoint:
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    app.logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    app.logger.info('Client disconnected')

@socketio.on('message')
def handle_message(data):
    app.logger.info(f'Received message: {data}')
    socketio.emit('response', {'data': 'Message received'})

# 应用初始化
def create_app():
    register_blueprints()
    init_database()
    return app

# 主程序入口
if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 3000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    app.logger.info(f'启动服务器: {host}:{port}')
    socketio.run(app, host=host, port=port, debug=False) 