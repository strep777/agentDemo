import bcrypt
from datetime import datetime
from bson import ObjectId
from app.services.database import get_db

class User:
    def __init__(self, username, email, password_hash=None, role="user", **kwargs):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.is_active = True
        self.avatar = kwargs.get('avatar', '')
        self.bio = kwargs.get('bio', '')
        self.settings = kwargs.get('settings', {})
        
    def to_dict(self):
        """转换为字典格式"""
        return {
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active,
            'avatar': self.avatar,
            'bio': self.bio,
            'settings': self.settings
        }
    
    @staticmethod
    def create(user_data):
        """创建新用户"""
        db = get_db()
        user = User(**user_data)
        result = db.users.insert_one(user.to_dict())
        user.id = str(result.inserted_id)
        return user
    
    @staticmethod
    def find_by_email(email):
        """根据邮箱查找用户"""
        db = get_db()
        user_data = db.users.find_one({"email": email})
        if user_data:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data.get('password_hash'),
                role=user_data.get('role', 'user'),
                avatar=user_data.get('avatar', ''),
                bio=user_data.get('bio', ''),
                settings=user_data.get('settings', {})
            )
            user.id = str(user_data['_id'])
            user.created_at = user_data['created_at']
            user.updated_at = user_data['updated_at']
            user.is_active = user_data.get('is_active', True)
            return user
        return None
    
    @staticmethod
    def find_by_id(user_id):
        """根据ID查找用户"""
        db = get_db()
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data.get('password_hash'),
                role=user_data.get('role', 'user'),
                avatar=user_data.get('avatar', ''),
                bio=user_data.get('bio', ''),
                settings=user_data.get('settings', {})
            )
            user.id = str(user_data['_id'])
            user.created_at = user_data['created_at']
            user.updated_at = user_data['updated_at']
            user.is_active = user_data.get('is_active', True)
            return user
        return None
    
    def update(self, update_data):
        """更新用户信息"""
        db = get_db()
        update_data['updated_at'] = datetime.now()
        result = db.users.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": update_data}
        )
        if result.modified_count > 0:
            for key, value in update_data.items():
                setattr(self, key, value)
            return True
        return False
    
    def delete(self):
        """删除用户"""
        db = get_db()
        result = db.users.delete_one({"_id": ObjectId(self.id)})
        return result.deleted_count > 0
    
    @staticmethod
    def get_all(limit=50, skip=0):
        """获取所有用户"""
        db = get_db()
        users = []
        cursor = db.users.find().skip(skip).limit(limit)
        for user_data in cursor:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data.get('password_hash'),
                role=user_data.get('role', 'user'),
                avatar=user_data.get('avatar', ''),
                bio=user_data.get('bio', ''),
                settings=user_data.get('settings', {})
            )
            user.id = str(user_data['_id'])
            user.created_at = user_data['created_at']
            user.updated_at = user_data['updated_at']
            user.is_active = user_data.get('is_active', True)
            users.append(user)
        return users
    
    @staticmethod
    def hash_password(password: str) -> str:
        """哈希密码"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """验证密码"""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8')) 