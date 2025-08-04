from datetime import datetime
from bson import ObjectId
from app.services.database import get_db

class Plugin:
    def __init__(self, name, description, author, user_id=None, **kwargs):
        self.name = name
        self.description = description
        self.author = author
        self.user_id = user_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.is_active = True
        self.version = kwargs.get('version', '1.0.0')
        self.category = kwargs.get('category', 'general')
        self.tags = kwargs.get('tags', [])
        self.icon = kwargs.get('icon', '')
        self.config_schema = kwargs.get('config_schema', {})
        self.api_endpoint = kwargs.get('api_endpoint', '')
        self.is_public = kwargs.get('is_public', False)
        self.downloads = kwargs.get('downloads', 0)
        self.rating = kwargs.get('rating', 0.0)
        self.reviews = kwargs.get('reviews', [])
        self.metadata = kwargs.get('metadata', {})
        self.stats = kwargs.get('stats', {
            'total_uses': 0,
            'success_rate': 0,
            'avg_response_time': 0
        })
        
    def to_dict(self):
        """转换为字典格式"""
        return {
            'name': self.name,
            'description': self.description,
            'author': self.author,
            'user_id': self.user_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active,
            'version': self.version,
            'category': self.category,
            'tags': self.tags,
            'icon': self.icon,
            'config_schema': self.config_schema,
            'api_endpoint': self.api_endpoint,
            'is_public': self.is_public,
            'downloads': self.downloads,
            'rating': self.rating,
            'reviews': self.reviews,
            'metadata': self.metadata,
            'stats': self.stats
        }
    
    @staticmethod
    def create(plugin_data):
        """创建新插件"""
        db = get_db()
        plugin = Plugin(**plugin_data)
        result = db.plugins.insert_one(plugin.to_dict())
        plugin.id = str(result.inserted_id)
        return plugin
    
    @staticmethod
    def find_by_id(plugin_id):
        """根据ID查找插件"""
        db = get_db()
        plugin_data = db.plugins.find_one({"_id": ObjectId(plugin_id)})
        if plugin_data:
            plugin = Plugin(
                name=plugin_data['name'],
                description=plugin_data['description'],
                author=plugin_data['author'],
                version=plugin_data.get('version', '1.0.0'),
                category=plugin_data.get('category', 'general'),
                tags=plugin_data.get('tags', []),
                icon=plugin_data.get('icon', ''),
                config_schema=plugin_data.get('config_schema', {}),
                api_endpoint=plugin_data.get('api_endpoint', ''),
                is_public=plugin_data.get('is_public', False),
                downloads=plugin_data.get('downloads', 0),
                rating=plugin_data.get('rating', 0.0),
                reviews=plugin_data.get('reviews', []),
                metadata=plugin_data.get('metadata', {}),
                stats=plugin_data.get('stats', {
                    'total_uses': 0,
                    'success_rate': 0,
                    'avg_response_time': 0
                })
            )
            plugin.id = str(plugin_data['_id'])
            plugin.created_at = plugin_data['created_at']
            plugin.updated_at = plugin_data['updated_at']
            plugin.is_active = plugin_data.get('is_active', True)
            return plugin
        return None
    
    @staticmethod
    def find_by_name(name):
        """根据名称查找插件"""
        db = get_db()
        plugin_data = db.plugins.find_one({"name": name})
        if plugin_data:
            plugin = Plugin(
                name=plugin_data['name'],
                description=plugin_data['description'],
                author=plugin_data['author'],
                version=plugin_data.get('version', '1.0.0'),
                category=plugin_data.get('category', 'general'),
                tags=plugin_data.get('tags', []),
                icon=plugin_data.get('icon', ''),
                config_schema=plugin_data.get('config_schema', {}),
                api_endpoint=plugin_data.get('api_endpoint', ''),
                is_public=plugin_data.get('is_public', False),
                downloads=plugin_data.get('downloads', 0),
                rating=plugin_data.get('rating', 0.0),
                reviews=plugin_data.get('reviews', []),
                metadata=plugin_data.get('metadata', {}),
                stats=plugin_data.get('stats', {
                    'total_uses': 0,
                    'success_rate': 0,
                    'avg_response_time': 0
                })
            )
            plugin.id = str(plugin_data['_id'])
            plugin.created_at = plugin_data['created_at']
            plugin.updated_at = plugin_data['updated_at']
            plugin.is_active = plugin_data.get('is_active', True)
            return plugin
        return None
    
    @staticmethod
    def find_by_category(category, limit=50, skip=0):
        """根据分类查找插件"""
        db = get_db()
        plugins = []
        cursor = db.plugins.find({"category": category, "is_active": True}).sort("downloads", -1).skip(skip).limit(limit)
        for plugin_data in cursor:
            plugin = Plugin(
                name=plugin_data['name'],
                description=plugin_data['description'],
                author=plugin_data['author'],
                version=plugin_data.get('version', '1.0.0'),
                category=plugin_data.get('category', 'general'),
                tags=plugin_data.get('tags', []),
                icon=plugin_data.get('icon', ''),
                config_schema=plugin_data.get('config_schema', {}),
                api_endpoint=plugin_data.get('api_endpoint', ''),
                is_public=plugin_data.get('is_public', False),
                downloads=plugin_data.get('downloads', 0),
                rating=plugin_data.get('rating', 0.0),
                reviews=plugin_data.get('reviews', []),
                metadata=plugin_data.get('metadata', {}),
                stats=plugin_data.get('stats', {
                    'total_uses': 0,
                    'success_rate': 0,
                    'avg_response_time': 0
                })
            )
            plugin.id = str(plugin_data['_id'])
            plugin.created_at = plugin_data['created_at']
            plugin.updated_at = plugin_data['updated_at']
            plugin.is_active = plugin_data.get('is_active', True)
            plugins.append(plugin)
        return plugins
    
    @staticmethod
    def find_public_plugins(limit=50, skip=0):
        """查找公开的插件"""
        db = get_db()
        plugins = []
        cursor = db.plugins.find({"is_public": True, "is_active": True}).sort("downloads", -1).skip(skip).limit(limit)
        for plugin_data in cursor:
            plugin = Plugin(
                name=plugin_data['name'],
                description=plugin_data['description'],
                author=plugin_data['author'],
                version=plugin_data.get('version', '1.0.0'),
                category=plugin_data.get('category', 'general'),
                tags=plugin_data.get('tags', []),
                icon=plugin_data.get('icon', ''),
                config_schema=plugin_data.get('config_schema', {}),
                api_endpoint=plugin_data.get('api_endpoint', ''),
                is_public=plugin_data.get('is_public', False),
                downloads=plugin_data.get('downloads', 0),
                rating=plugin_data.get('rating', 0.0),
                reviews=plugin_data.get('reviews', []),
                metadata=plugin_data.get('metadata', {}),
                stats=plugin_data.get('stats', {
                    'total_uses': 0,
                    'success_rate': 0,
                    'avg_response_time': 0
                })
            )
            plugin.id = str(plugin_data['_id'])
            plugin.created_at = plugin_data['created_at']
            plugin.updated_at = plugin_data['updated_at']
            plugin.is_active = plugin_data.get('is_active', True)
            plugins.append(plugin)
        return plugins
    
    def update(self, update_data):
        """更新插件信息"""
        db = get_db()
        update_data['updated_at'] = datetime.now()
        result = db.plugins.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": update_data}
        )
        if result.modified_count > 0:
            for key, value in update_data.items():
                setattr(self, key, value)
            return True
        return False
    
    def delete(self):
        """删除插件"""
        db = get_db()
        result = db.plugins.delete_one({"_id": ObjectId(self.id)})
        return result.deleted_count > 0
    
    def increment_downloads(self):
        """增加下载次数"""
        db = get_db()
        result = db.plugins.update_one(
            {"_id": ObjectId(self.id)},
            {"$inc": {"downloads": 1}}
        )
        if result.modified_count > 0:
            self.downloads += 1
            return True
        return False
    
    def add_review(self, review):
        """添加评论"""
        db = get_db()
        review['timestamp'] = datetime.now()
        review['id'] = str(ObjectId())
        
        result = db.plugins.update_one(
            {"_id": ObjectId(self.id)},
            {
                "$push": {"reviews": review},
                "$set": {"updated_at": datetime.now()}
            }
        )
        if result.modified_count > 0:
            self.reviews.append(review)
            self.updated_at = datetime.now()
            return True
        return False
    
    def update_stats(self, stats_data):
        """更新插件统计信息"""
        db = get_db()
        result = db.plugins.update_one(
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
        """获取所有插件"""
        db = get_db()
        plugins = []
        cursor = db.plugins.find().sort("downloads", -1).skip(skip).limit(limit)
        for plugin_data in cursor:
            plugin = Plugin(
                name=plugin_data['name'],
                description=plugin_data['description'],
                author=plugin_data['author'],
                version=plugin_data.get('version', '1.0.0'),
                category=plugin_data.get('category', 'general'),
                tags=plugin_data.get('tags', []),
                icon=plugin_data.get('icon', ''),
                config_schema=plugin_data.get('config_schema', {}),
                api_endpoint=plugin_data.get('api_endpoint', ''),
                is_public=plugin_data.get('is_public', False),
                downloads=plugin_data.get('downloads', 0),
                rating=plugin_data.get('rating', 0.0),
                reviews=plugin_data.get('reviews', []),
                metadata=plugin_data.get('metadata', {}),
                stats=plugin_data.get('stats', {
                    'total_uses': 0,
                    'success_rate': 0,
                    'avg_response_time': 0
                })
            )
            plugin.id = str(plugin_data['_id'])
            plugin.created_at = plugin_data['created_at']
            plugin.updated_at = plugin_data['updated_at']
            plugin.is_active = plugin_data.get('is_active', True)
            plugins.append(plugin)
        return plugins
    
    @staticmethod
    def find_by_user_id(user_id, limit=50, skip=0):
        """根据用户ID查找插件"""
        db = get_db()
        plugins = []
        cursor = db.plugins.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
        for plugin_data in cursor:
            plugin = Plugin(
                name=plugin_data['name'],
                description=plugin_data['description'],
                author=plugin_data['author'],
                user_id=plugin_data.get('user_id'),
                version=plugin_data.get('version', '1.0.0'),
                category=plugin_data.get('category', 'general'),
                tags=plugin_data.get('tags', []),
                icon=plugin_data.get('icon', ''),
                config_schema=plugin_data.get('config_schema', {}),
                api_endpoint=plugin_data.get('api_endpoint', ''),
                is_public=plugin_data.get('is_public', False),
                downloads=plugin_data.get('downloads', 0),
                rating=plugin_data.get('rating', 0.0),
                reviews=plugin_data.get('reviews', []),
                metadata=plugin_data.get('metadata', {}),
                stats=plugin_data.get('stats', {
                    'total_uses': 0,
                    'success_rate': 0,
                    'avg_response_time': 0
                })
            )
            plugin.id = str(plugin_data['_id'])
            plugin.created_at = plugin_data['created_at']
            plugin.updated_at = plugin_data['updated_at']
            plugin.is_active = plugin_data.get('is_active', True)
            plugins.append(plugin)
        return plugins 