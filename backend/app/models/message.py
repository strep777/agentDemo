"""
消息模型
定义聊天消息的数据结构
"""

from datetime import datetime
from bson import ObjectId
from app.services.database import get_db

class Message:
    def __init__(self, conversation_id, user_id, content, message_type="text", **kwargs):
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.content = content
        self.message_type = message_type
        self.timestamp = datetime.now()
        self.attachments = kwargs.get('attachments', [])
        self.metadata = kwargs.get('metadata', {})
        self.is_read = kwargs.get('is_read', False)
        
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': getattr(self, 'id', None),
            'conversation_id': self.conversation_id,
            'user_id': self.user_id,
            'content': self.content,
            'message_type': self.message_type,
            'timestamp': self.timestamp,
            'attachments': self.attachments,
            'metadata': self.metadata,
            'is_read': self.is_read
        }
    
    @staticmethod
    def create(message_data):
        """创建新消息"""
        db = get_db()
        message = Message(**message_data)
        result = db.messages.insert_one(message.to_dict())
        message.id = str(result.inserted_id)
        return message
    
    @staticmethod
    def find_by_id(message_id):
        """根据ID查找消息"""
        db = get_db()
        message_data = db.messages.find_one({"_id": ObjectId(message_id)})
        if message_data:
            message = Message(
                conversation_id=message_data['conversation_id'],
                user_id=message_data['user_id'],
                content=message_data['content'],
                message_type=message_data.get('message_type', 'text'),
                attachments=message_data.get('attachments', []),
                metadata=message_data.get('metadata', {}),
                is_read=message_data.get('is_read', False)
            )
            message.id = str(message_data['_id'])
            message.timestamp = message_data['timestamp']
            return message
        return None
    
    @staticmethod
    def find_by_conversation(conversation_id, limit=100, skip=0):
        """根据对话ID查找消息"""
        db = get_db()
        messages = []
        cursor = db.messages.find({"conversation_id": conversation_id}).sort("timestamp", 1).skip(skip).limit(limit)
        for message_data in cursor:
            message = Message(
                conversation_id=message_data['conversation_id'],
                user_id=message_data['user_id'],
                content=message_data['content'],
                message_type=message_data.get('message_type', 'text'),
                attachments=message_data.get('attachments', []),
                metadata=message_data.get('metadata', {}),
                is_read=message_data.get('is_read', False)
            )
            message.id = str(message_data['_id'])
            message.timestamp = message_data['timestamp']
            messages.append(message)
        return messages
    
    @staticmethod
    def find_by_user(user_id, limit=50, skip=0):
        """根据用户ID查找消息"""
        db = get_db()
        messages = []
        cursor = db.messages.find({"user_id": user_id}).sort("timestamp", -1).skip(skip).limit(limit)
        for message_data in cursor:
            message = Message(
                conversation_id=message_data['conversation_id'],
                user_id=message_data['user_id'],
                content=message_data['content'],
                message_type=message_data.get('message_type', 'text'),
                attachments=message_data.get('attachments', []),
                metadata=message_data.get('metadata', {}),
                is_read=message_data.get('is_read', False)
            )
            message.id = str(message_data['_id'])
            message.timestamp = message_data['timestamp']
            messages.append(message)
        return messages
    
    def update(self, update_data):
        """更新消息信息"""
        db = get_db()
        update_data['timestamp'] = datetime.now()
        result = db.messages.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": update_data}
        )
        if result.modified_count > 0:
            for key, value in update_data.items():
                setattr(self, key, value)
            return True
        return False
    
    def delete(self):
        """删除消息"""
        db = get_db()
        result = db.messages.delete_one({"_id": ObjectId(self.id)})
        return result.deleted_count > 0
    
    @staticmethod
    def get_all(limit=50, skip=0):
        """获取所有消息"""
        db = get_db()
        messages = []
        cursor = db.messages.find().sort("timestamp", -1).skip(skip).limit(limit)
        for message_data in cursor:
            message = Message(
                conversation_id=message_data['conversation_id'],
                user_id=message_data['user_id'],
                content=message_data['content'],
                message_type=message_data.get('message_type', 'text'),
                attachments=message_data.get('attachments', []),
                metadata=message_data.get('metadata', {}),
                is_read=message_data.get('is_read', False)
            )
            message.id = str(message_data['_id'])
            message.timestamp = message_data['timestamp']
            messages.append(message)
        return messages
    
    def save(self):
        """保存消息到数据库"""
        db = get_db()
        if hasattr(self, 'id') and self.id:
            # 更新现有消息
            result = db.messages.update_one(
                {"_id": ObjectId(self.id)},
                {"$set": self.to_dict()}
            )
            return result.modified_count > 0
        else:
            # 创建新消息
            result = db.messages.insert_one(self.to_dict())
            self.id = str(result.inserted_id)
            return True 