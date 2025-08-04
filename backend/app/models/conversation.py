from datetime import datetime
from bson import ObjectId
from app.services.database import get_db

class Conversation:
    def __init__(self, user_id, agent_id, title=None, **kwargs):
        self.user_id = user_id
        self.agent_id = agent_id
        self.title = title or "新对话"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.is_active = True
        self.messages = kwargs.get('messages', [])
        self.settings = kwargs.get('settings', {})
        self.metadata = kwargs.get('metadata', {})
        
    def to_dict(self):
        """转换为字典格式"""
        return {
            'user_id': self.user_id,
            'agent_id': self.agent_id,
            'title': self.title,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active,
            'messages': self.messages,
            'settings': self.settings,
            'metadata': self.metadata
        }
    
    @staticmethod
    def create(conversation_data):
        """创建新对话"""
        db = get_db()
        conversation = Conversation(**conversation_data)
        result = db.conversations.insert_one(conversation.to_dict())
        conversation.id = str(result.inserted_id)
        return conversation
    
    @staticmethod
    def find_by_id(conversation_id):
        """根据ID查找对话"""
        db = get_db()
        conversation_data = db.conversations.find_one({"_id": ObjectId(conversation_id)})
        if conversation_data:
            conversation = Conversation(
                user_id=conversation_data['user_id'],
                agent_id=conversation_data['agent_id'],
                title=conversation_data.get('title', '新对话'),
                messages=conversation_data.get('messages', []),
                settings=conversation_data.get('settings', {}),
                metadata=conversation_data.get('metadata', {})
            )
            conversation.id = str(conversation_data['_id'])
            conversation.created_at = conversation_data['created_at']
            conversation.updated_at = conversation_data['updated_at']
            conversation.is_active = conversation_data.get('is_active', True)
            return conversation
        return None
    
    @staticmethod
    def find_by_user_id(user_id, limit=50, skip=0):
        """根据用户ID查找对话"""
        db = get_db()
        conversations = []
        cursor = db.conversations.find({"user_id": user_id}).sort("updated_at", -1).skip(skip).limit(limit)
        for conversation_data in cursor:
            conversation = Conversation(
                user_id=conversation_data['user_id'],
                agent_id=conversation_data['agent_id'],
                title=conversation_data.get('title', '新对话'),
                messages=conversation_data.get('messages', []),
                settings=conversation_data.get('settings', {}),
                metadata=conversation_data.get('metadata', {})
            )
            conversation.id = str(conversation_data['_id'])
            conversation.created_at = conversation_data['created_at']
            conversation.updated_at = conversation_data['updated_at']
            conversation.is_active = conversation_data.get('is_active', True)
            conversations.append(conversation)
        return conversations
    
    @staticmethod
    def find_by_agent_id(agent_id, limit=50, skip=0):
        """根据智能体ID查找对话"""
        db = get_db()
        conversations = []
        cursor = db.conversations.find({"agent_id": agent_id}).sort("updated_at", -1).skip(skip).limit(limit)
        for conversation_data in cursor:
            conversation = Conversation(
                user_id=conversation_data['user_id'],
                agent_id=conversation_data['agent_id'],
                title=conversation_data.get('title', '新对话'),
                messages=conversation_data.get('messages', []),
                settings=conversation_data.get('settings', {}),
                metadata=conversation_data.get('metadata', {})
            )
            conversation.id = str(conversation_data['_id'])
            conversation.created_at = conversation_data['created_at']
            conversation.updated_at = conversation_data['updated_at']
            conversation.is_active = conversation_data.get('is_active', True)
            conversations.append(conversation)
        return conversations
    
    def update(self, update_data):
        """更新对话信息"""
        db = get_db()
        update_data['updated_at'] = datetime.now()
        result = db.conversations.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": update_data}
        )
        if result.modified_count > 0:
            for key, value in update_data.items():
                setattr(self, key, value)
            return True
        return False
    
    def add_message(self, message):
        """添加消息到对话"""
        db = get_db()
        message['timestamp'] = datetime.now()
        message['id'] = str(ObjectId())
        
        result = db.conversations.update_one(
            {"_id": ObjectId(self.id)},
            {
                "$push": {"messages": message},
                "$set": {"updated_at": datetime.now()}
            }
        )
        if result.modified_count > 0:
            self.messages.append(message)
            self.updated_at = datetime.now()
            return True
        return False
    
    def delete(self):
        """删除对话"""
        db = get_db()
        result = db.conversations.delete_one({"_id": ObjectId(self.id)})
        return result.deleted_count > 0
    
    @staticmethod
    def get_all(limit=50, skip=0):
        """获取所有对话"""
        db = get_db()
        conversations = []
        cursor = db.conversations.find().sort("updated_at", -1).skip(skip).limit(limit)
        for conversation_data in cursor:
            conversation = Conversation(
                user_id=conversation_data['user_id'],
                agent_id=conversation_data['agent_id'],
                title=conversation_data.get('title', '新对话'),
                messages=conversation_data.get('messages', []),
                settings=conversation_data.get('settings', {}),
                metadata=conversation_data.get('metadata', {})
            )
            conversation.id = str(conversation_data['_id'])
            conversation.created_at = conversation_data['created_at']
            conversation.updated_at = conversation_data['updated_at']
            conversation.is_active = conversation_data.get('is_active', True)
            conversations.append(conversation)
        return conversations
    
    def save(self):
        """保存对话到数据库"""
        db = get_db()
        if hasattr(self, 'id') and self.id:
            # 更新现有对话
            result = db.conversations.update_one(
                {"_id": ObjectId(self.id)},
                {"$set": self.to_dict()}
            )
            return result.modified_count > 0
        else:
            # 创建新对话
            result = db.conversations.insert_one(self.to_dict())
            self.id = str(result.inserted_id)
            return True
    
    @staticmethod
    def find_by_user_and_agent(user_id: str, agent_id: str):
        """根据用户ID和智能体ID查找对话"""
        db = get_db()
        conversation_data = db.conversations.find_one({
            "user_id": user_id,
            "agent_id": agent_id,
            "is_active": True
        })
        if conversation_data:
            conversation = Conversation(
                user_id=conversation_data['user_id'],
                agent_id=conversation_data['agent_id'],
                title=conversation_data.get('title', '新对话'),
                messages=conversation_data.get('messages', []),
                settings=conversation_data.get('settings', {}),
                metadata=conversation_data.get('metadata', {})
            )
            conversation.id = str(conversation_data['_id'])
            conversation.created_at = conversation_data['created_at']
            conversation.updated_at = conversation_data['updated_at']
            conversation.is_active = conversation_data.get('is_active', True)
            return conversation
        return None 