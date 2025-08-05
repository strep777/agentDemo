from flask import Blueprint
from .auth import auth_bp
from .chat import chat_bp
from .models import models_bp
from .plugins import plugins_bp
from .settings import settings_bp
from .agents import agents_bp
from .knowledge import knowledge_bp
from .workflows import workflows_bp
from .training import training_bp
from .dashboard import dashboard_bp

# 创建主API蓝图
api_bp = Blueprint('api', __name__)

# 注册所有子蓝图
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(chat_bp, url_prefix='/chat')
api_bp.register_blueprint(models_bp, url_prefix='/models')
api_bp.register_blueprint(plugins_bp, url_prefix='/plugins')
api_bp.register_blueprint(settings_bp, url_prefix='/settings')
api_bp.register_blueprint(agents_bp, url_prefix='/agents')
api_bp.register_blueprint(knowledge_bp, url_prefix='/knowledge')
api_bp.register_blueprint(workflows_bp, url_prefix='/workflows')
api_bp.register_blueprint(training_bp, url_prefix='/training')
api_bp.register_blueprint(dashboard_bp, url_prefix='/dashboard') 