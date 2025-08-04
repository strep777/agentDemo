"""
活动服务模块
记录用户活动日志
"""

from datetime import datetime
from typing import Dict, Any
from app.services.database import get_db

class ActivityService:
    def __init__(self):
        pass
    
    def record_conversation_started(self, user_id: str, agent_name: str, conversation_id: str):
        """
        记录对话开始活动
        """
        try:
            db = get_db()
            activity = {
                'user_id': user_id,
                'type': 'conversation_started',
                'title': f'开始与{agent_name}对话',
                'description': f'用户开始与智能体{agent_name}的对话',
                'metadata': {
                    'agent_name': agent_name,
                    'conversation_id': conversation_id
                },
                'created_at': datetime.now()
            }
            db.activities.insert_one(activity)
        except Exception as e:
            print(f"记录活动失败: {e}")
    
    def record_agent_created(self, user_id: str, agent_name: str, agent_id: str):
        """
        记录智能体创建活动
        """
        try:
            db = get_db()
            activity = {
                'user_id': user_id,
                'type': 'agent_created',
                'title': f'创建智能体{agent_name}',
                'description': f'用户创建了新的智能体{agent_name}',
                'metadata': {
                    'agent_name': agent_name,
                    'agent_id': agent_id
                },
                'created_at': datetime.now()
            }
            db.activities.insert_one(activity)
        except Exception as e:
            print(f"记录活动失败: {e}")
    
    def record_knowledge_updated(self, user_id: str, knowledge_name: str, knowledge_id: str):
        """
        记录知识库更新活动
        """
        try:
            db = get_db()
            activity = {
                'user_id': user_id,
                'type': 'knowledge_updated',
                'title': f'更新知识库{knowledge_name}',
                'description': f'用户更新了知识库{knowledge_name}',
                'metadata': {
                    'knowledge_name': knowledge_name,
                    'knowledge_id': knowledge_id
                },
                'created_at': datetime.now()
            }
            db.activities.insert_one(activity)
        except Exception as e:
            print(f"记录活动失败: {e}")
    
    def record_plugin_installed(self, user_id: str, plugin_name: str, plugin_id: str):
        """
        记录插件安装活动
        """
        try:
            db = get_db()
            activity = {
                'user_id': user_id,
                'type': 'plugin_installed',
                'title': f'安装插件{plugin_name}',
                'description': f'用户安装了插件{plugin_name}',
                'metadata': {
                    'plugin_name': plugin_name,
                    'plugin_id': plugin_id
                },
                'created_at': datetime.now()
            }
            db.activities.insert_one(activity)
        except Exception as e:
            print(f"记录活动失败: {e}")
    
    def get_user_activities(self, user_id: str, limit: int = 10):
        """
        获取用户活动列表
        """
        try:
            db = get_db()
            activities = list(db.activities.find({'user_id': user_id})
                            .sort('created_at', -1)
                            .limit(limit))
            
            for activity in activities:
                activity['id'] = str(activity['_id'])
                activity['created_at'] = activity['created_at'].isoformat()
                del activity['_id']
            
            return activities
        except Exception as e:
            print(f"获取活动列表失败: {e}")
            return []

# 创建全局实例
activity_service = ActivityService() 