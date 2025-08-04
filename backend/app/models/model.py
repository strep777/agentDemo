from datetime import datetime
from bson import ObjectId
from app.services.database import get_db

class Model:
    def __init__(self, name, provider, model_type, **kwargs):
        self.name = name
        self.provider = provider
        self.model_type = model_type
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.is_active = True
        self.version = kwargs.get('version', '1.0.0')
        self.description = kwargs.get('description', '')
        self.api_key = kwargs.get('api_key', '')
        self.api_base = kwargs.get('api_base', '')
        self.max_tokens = kwargs.get('max_tokens', 4096)
        self.temperature = kwargs.get('temperature', 0.7)
        self.top_p = kwargs.get('top_p', 1.0)
        self.frequency_penalty = kwargs.get('frequency_penalty', 0.0)
        self.presence_penalty = kwargs.get('presence_penalty', 0.0)
        self.settings = kwargs.get('settings', {})
        self.metadata = kwargs.get('metadata', {})
        self.stats = kwargs.get('stats', {
            'total_requests': 0,
            'success_rate': 0,
            'avg_response_time': 0,
            'total_tokens_used': 0
        })
        
    def to_dict(self):
        """转换为字典格式"""
        return {
            'name': self.name,
            'provider': self.provider,
            'model_type': self.model_type,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active,
            'version': self.version,
            'description': self.description,
            'api_key': self.api_key,
            'api_base': self.api_base,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
            'settings': self.settings,
            'metadata': self.metadata,
            'stats': self.stats
        }
    
    @staticmethod
    def create(model_data):
        """创建新模型"""
        db = get_db()
        model = Model(**model_data)
        result = db.models.insert_one(model.to_dict())
        model.id = str(result.inserted_id)
        return model
    
    @staticmethod
    def find_by_id(model_id):
        """根据ID查找模型"""
        db = get_db()
        model_data = db.models.find_one({"_id": ObjectId(model_id)})
        if model_data:
            model = Model(
                name=model_data['name'],
                provider=model_data['provider'],
                model_type=model_data['model_type'],
                version=model_data.get('version', '1.0.0'),
                description=model_data.get('description', ''),
                api_key=model_data.get('api_key', ''),
                api_base=model_data.get('api_base', ''),
                max_tokens=model_data.get('max_tokens', 4096),
                temperature=model_data.get('temperature', 0.7),
                top_p=model_data.get('top_p', 1.0),
                frequency_penalty=model_data.get('frequency_penalty', 0.0),
                presence_penalty=model_data.get('presence_penalty', 0.0),
                settings=model_data.get('settings', {}),
                metadata=model_data.get('metadata', {}),
                stats=model_data.get('stats', {
                    'total_requests': 0,
                    'success_rate': 0,
                    'avg_response_time': 0,
                    'total_tokens_used': 0
                })
            )
            model.id = str(model_data['_id'])
            model.created_at = model_data['created_at']
            model.updated_at = model_data['updated_at']
            model.is_active = model_data.get('is_active', True)
            return model
        return None
    
    @staticmethod
    def find_by_name(name):
        """根据名称查找模型"""
        db = get_db()
        model_data = db.models.find_one({"name": name})
        if model_data:
            model = Model(
                name=model_data['name'],
                provider=model_data['provider'],
                model_type=model_data['model_type'],
                version=model_data.get('version', '1.0.0'),
                description=model_data.get('description', ''),
                api_key=model_data.get('api_key', ''),
                api_base=model_data.get('api_base', ''),
                max_tokens=model_data.get('max_tokens', 4096),
                temperature=model_data.get('temperature', 0.7),
                top_p=model_data.get('top_p', 1.0),
                frequency_penalty=model_data.get('frequency_penalty', 0.0),
                presence_penalty=model_data.get('presence_penalty', 0.0),
                settings=model_data.get('settings', {}),
                metadata=model_data.get('metadata', {}),
                stats=model_data.get('stats', {
                    'total_requests': 0,
                    'success_rate': 0,
                    'avg_response_time': 0,
                    'total_tokens_used': 0
                })
            )
            model.id = str(model_data['_id'])
            model.created_at = model_data['created_at']
            model.updated_at = model_data['updated_at']
            model.is_active = model_data.get('is_active', True)
            return model
        return None
    
    @staticmethod
    def find_by_provider(provider, limit=50, skip=0):
        """根据提供商查找模型"""
        db = get_db()
        models = []
        cursor = db.models.find({"provider": provider, "is_active": True}).skip(skip).limit(limit)
        for model_data in cursor:
            model = Model(
                name=model_data['name'],
                provider=model_data['provider'],
                model_type=model_data['model_type'],
                version=model_data.get('version', '1.0.0'),
                description=model_data.get('description', ''),
                api_key=model_data.get('api_key', ''),
                api_base=model_data.get('api_base', ''),
                max_tokens=model_data.get('max_tokens', 4096),
                temperature=model_data.get('temperature', 0.7),
                top_p=model_data.get('top_p', 1.0),
                frequency_penalty=model_data.get('frequency_penalty', 0.0),
                presence_penalty=model_data.get('presence_penalty', 0.0),
                settings=model_data.get('settings', {}),
                metadata=model_data.get('metadata', {}),
                stats=model_data.get('stats', {
                    'total_requests': 0,
                    'success_rate': 0,
                    'avg_response_time': 0,
                    'total_tokens_used': 0
                })
            )
            model.id = str(model_data['_id'])
            model.created_at = model_data['created_at']
            model.updated_at = model_data['updated_at']
            model.is_active = model_data.get('is_active', True)
            models.append(model)
        return models
    
    @staticmethod
    def find_by_type(model_type, limit=50, skip=0):
        """根据类型查找模型"""
        db = get_db()
        models = []
        cursor = db.models.find({"model_type": model_type, "is_active": True}).skip(skip).limit(limit)
        for model_data in cursor:
            model = Model(
                name=model_data['name'],
                provider=model_data['provider'],
                model_type=model_data['model_type'],
                version=model_data.get('version', '1.0.0'),
                description=model_data.get('description', ''),
                api_key=model_data.get('api_key', ''),
                api_base=model_data.get('api_base', ''),
                max_tokens=model_data.get('max_tokens', 4096),
                temperature=model_data.get('temperature', 0.7),
                top_p=model_data.get('top_p', 1.0),
                frequency_penalty=model_data.get('frequency_penalty', 0.0),
                presence_penalty=model_data.get('presence_penalty', 0.0),
                settings=model_data.get('settings', {}),
                metadata=model_data.get('metadata', {}),
                stats=model_data.get('stats', {
                    'total_requests': 0,
                    'success_rate': 0,
                    'avg_response_time': 0,
                    'total_tokens_used': 0
                })
            )
            model.id = str(model_data['_id'])
            model.created_at = model_data['created_at']
            model.updated_at = model_data['updated_at']
            model.is_active = model_data.get('is_active', True)
            models.append(model)
        return models
    
    def update(self, update_data):
        """更新模型信息"""
        db = get_db()
        update_data['updated_at'] = datetime.now()
        result = db.models.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": update_data}
        )
        if result.modified_count > 0:
            for key, value in update_data.items():
                setattr(self, key, value)
            return True
        return False
    
    def delete(self):
        """删除模型"""
        db = get_db()
        result = db.models.delete_one({"_id": ObjectId(self.id)})
        return result.deleted_count > 0
    
    def update_stats(self, stats_data):
        """更新模型统计信息"""
        db = get_db()
        result = db.models.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": {"stats": stats_data, "updated_at": datetime.now()}}
        )
        if result.modified_count > 0:
            self.stats = stats_data
            self.updated_at = datetime.now()
            return True
        return False
    
    @staticmethod
    def get_all(limit=50, skip=0):
        """获取所有模型"""
        db = get_db()
        models = []
        cursor = db.models.find().skip(skip).limit(limit)
        for model_data in cursor:
            model = Model(
                name=model_data['name'],
                provider=model_data['provider'],
                model_type=model_data['model_type'],
                version=model_data.get('version', '1.0.0'),
                description=model_data.get('description', ''),
                api_key=model_data.get('api_key', ''),
                api_base=model_data.get('api_base', ''),
                max_tokens=model_data.get('max_tokens', 4096),
                temperature=model_data.get('temperature', 0.7),
                top_p=model_data.get('top_p', 1.0),
                frequency_penalty=model_data.get('frequency_penalty', 0.0),
                presence_penalty=model_data.get('presence_penalty', 0.0),
                settings=model_data.get('settings', {}),
                metadata=model_data.get('metadata', {}),
                stats=model_data.get('stats', {
                    'total_requests': 0,
                    'success_rate': 0,
                    'avg_response_time': 0,
                    'total_tokens_used': 0
                })
            )
            model.id = str(model_data['_id'])
            model.created_at = model_data['created_at']
            model.updated_at = model_data['updated_at']
            model.is_active = model_data.get('is_active', True)
            models.append(model)
        return models 