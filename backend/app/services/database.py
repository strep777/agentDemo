import os
from pymongo import MongoClient
from datetime import datetime

# 数据库配置
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://root:qwbt123@172.16.156.100:27017/')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'ai_agent_system')

# 主进程标志 - 通过环境变量判断
_is_main_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'

# 全局数据库客户端
client = None
db = None

def get_client():
    """获取MongoDB客户端"""
    global client
    
    if client is None:
        try:
            client = MongoClient(MONGODB_URI)
            # 测试连接
            client.admin.command('ping')
            if _is_main_process:
                print("✅ MongoDB连接成功")
        except Exception as e:
            if _is_main_process:
                print(f"❌ MongoDB连接失败: {e}")
            raise e
    return client

def close_client():
    """关闭MongoDB客户端"""
    global client
    if client:
        client.close()
        if _is_main_process:
            print("✅ MongoDB连接已关闭") 

def get_db():
    """获取数据库连接"""
    try:
        client = get_client()
        db = client[DATABASE_NAME]
        return db
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        raise e

def init_db():
    """初始化数据库"""
    try:
        # 只在主进程中执行初始化
        if _is_main_process:
            print("🔧 初始化数据库...")
            
            # 创建数据库连接
            client = get_client()
            db = client[DATABASE_NAME]
            
            # 创建索引
            create_indexes(db)
            
            print("✅ 数据库初始化完成")
        
    except Exception as e:
        if _is_main_process:
            print(f"❌ 数据库初始化失败: {e}")
        raise e

def init_database():
    """初始化数据库（别名）"""
    return init_db()

def create_indexes(db):
    """创建数据库索引"""
    try:
        # 用户集合索引
        db.users.create_index([("username", 1)], unique=True)
        db.users.create_index([("email", 1)], unique=True)
        
        # 智能体集合索引
        db.agents.create_index([("user_id", 1)])
        db.agents.create_index([("status", 1)])
        
        # 对话集合索引
        db.conversations.create_index([("user_id", 1)])
        db.conversations.create_index([("agent_id", 1)])
        db.conversations.create_index([("created_at", -1)])
        
        # 消息集合索引
        db.messages.create_index([("conversation_id", 1)])
        db.messages.create_index([("created_at", 1)])
        
        # 知识库集合索引
        db.knowledge_bases.create_index([("user_id", 1)])
        db.knowledge_bases.create_index([("status", 1)])
        
        # 文档集合索引
        db.documents.create_index([("knowledge_base_id", 1)])
        db.documents.create_index([("status", 1)])
        
        # 插件集合索引
        db.plugins.create_index([("user_id", 1)])
        db.plugins.create_index([("status", 1)])
        
        # 工作流集合索引
        db.workflows.create_index([("user_id", 1)])
        db.workflows.create_index([("status", 1)])
        
        # 模型集合索引
        db.models.create_index([("user_id", 1)])
        db.models.create_index([("status", 1)])
        
        # 训练任务集合索引
        db.training_jobs.create_index([("agent_id", 1)])
        db.training_jobs.create_index([("status", 1)])
        
        # 执行历史集合索引
        db.execution_history.create_index([("user_id", 1)])
        db.execution_history.create_index([("workflow_id", 1)])
        db.execution_history.create_index([("created_at", -1)])
        
        # 只在主进程中打印索引创建完成信息
        if _is_main_process:
            print("✅ 数据库索引创建完成")
        
    except Exception as e:
        print(f"❌ 创建索引失败: {e}")
        raise e 