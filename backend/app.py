from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import logging
from logging.handlers import RotatingFileHandler


# 全局变量声明 - 通过环境变量判断
_is_main_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'

# 设置开发环境
if not os.environ.get('FLASK_ENV'):
    os.environ['FLASK_ENV'] = 'development'
if not os.environ.get('FLASK_DEBUG'):
    os.environ['FLASK_DEBUG'] = '1'

# 只在主进程中打印环境信息
if _is_main_process:
    print(f"🌍 环境变量设置:")
    print(f"   FLASK_ENV: {os.environ.get('FLASK_ENV')}")
    print(f"   FLASK_DEBUG: {os.environ.get('FLASK_DEBUG')}")

# 创建Flask应用
app = Flask(__name__)

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

# 允许跨域请求 - 修复CORS配置
CORS(app, 
     resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}},
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     expose_headers=["Content-Type", "Authorization"])

# 初始化SocketIO
socketio = SocketIO(
    app, 
    cors_allowed_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    async_mode='eventlet',
    logger=True,
    engineio_logger=True
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
        # 只在主进程中打印成功信息
        if _is_main_process:
            print("✅ 数据库连接成功")
    except Exception as e:
        if _is_main_process:
            print(f"❌ 数据库连接失败: {e}")
            print("❌ 系统无法启动，请检查数据库连接")
        raise e

# 健康检查端点
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'AI Agent Management System is running'}

# 根路径重定向到健康检查
@app.route('/')
def root():
    return {'status': 'healthy', 'message': 'AI Agent Management System is running'}

# 调试端点
@app.route('/debug')
def debug_info():
    return {
        'status': 'running',
        'port': 3000,
        'cors_enabled': True,
        'database_connected': True,
        'endpoints': [
            '/health',
            '/api/agents',
            '/api/conversations',
            '/api/dashboard/stats',
            '/api/models',
            '/api/workflows',
            '/api/plugins'
        ]
    }

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
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(data):
    print('Received message:', data)
    socketio.emit('response', {'data': 'Message received'})

if __name__ == '__main__':
    import os
    print('FLASK_ENV:', os.environ.get('FLASK_ENV'))
    print('FLASK_DEBUG:', os.environ.get('FLASK_DEBUG'))
    # 确保输出目录存在
    os.makedirs('output', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # 注册蓝图和初始化数据库
    register_blueprints()
    init_database()
    
    # 只在主进程中打印启动信息
    if _is_main_process:
        print("🚀 AI智能体管理系统后端服务器启动中...")
        print(f"📊 数据库连接: {app.config['MONGODB_URI']}")
        print(f"🌐 API地址: http://localhost:3000/api")
        print(f"🔌 WebSocket地址: ws://localhost:3000/socket.io")
        print(f"💡 前端地址: http://localhost:5173")
        print(f"🏥 健康检查: http://localhost:3000/health")
        print(f"🔧 Ollama地址: {app.config['OLLAMA_BASE_URL']}")
        print("=" * 60)
    
    # 启动服务器
    socketio.run(app, host='0.0.0.0', port=3000, debug=True, use_reloader=True) 