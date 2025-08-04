"""
知识库模型模块
定义知识库相关的数据模型
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

class Knowledge:
    def __init__(
        self,
        name: str,
        description: str,
        type: str,
        status: bool = True,
        config: Optional[Dict[str, Any]] = None,
        document_count: int = 0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.name = name
        self.description = description
        self.type = type
        self.status = status
        self.config = config or {}
        self.document_count = document_count
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'status': self.status,
            'config': self.config,
            'document_count': self.document_count,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Knowledge':
        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            type=data.get('type', ''),
            status=data.get('status', True),
            config=data.get('config', {}),
            document_count=data.get('document_count', 0),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

class KnowledgeDocument(BaseModel):
    """知识库文档模型"""
    id: Optional[str] = Field(None, alias="_id")
    knowledge_id: str = Field(..., description="知识库ID")
    name: str = Field(..., description="文档名称")
    content: str = Field(..., description="文档内容")
    file_type: str = Field(..., description="文件类型")
    file_size: int = Field(..., description="文件大小(字节)")
    status: str = Field("processing", description="处理状态: processing, processed, failed")
    user_id: str = Field(..., description="上传者ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    vector_embedding: Optional[List[float]] = Field(None, description="向量嵌入")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "knowledge_id": "kb123",
                "name": "产品手册.pdf",
                "content": "产品使用说明...",
                "file_type": "application/pdf",
                "file_size": 1024000,
                "status": "processed",
                "user_id": "user123",
                "metadata": {
                    "author": "张三",
                    "version": "1.0"
                }
            }
        }

class KnowledgeSearchRequest(BaseModel):
    """知识库搜索请求模型"""
    query: str = Field(..., description="搜索查询")
    knowledge_id: str = Field(..., description="知识库ID")
    limit: int = Field(10, description="返回结果数量限制")
    similarity_threshold: Optional[float] = Field(None, description="相似度阈值")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "如何安装产品？",
                "knowledge_id": "kb123",
                "limit": 5,
                "similarity_threshold": 0.8
            }
        }

class KnowledgeSearchResult(BaseModel):
    """知识库搜索结果模型"""
    document_id: str = Field(..., description="文档ID")
    document_name: str = Field(..., description="文档名称")
    content: str = Field(..., description="匹配内容")
    similarity_score: float = Field(..., description="相似度分数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc123",
                "document_name": "安装指南.pdf",
                "content": "产品安装步骤：1. 打开包装...",
                "similarity_score": 0.95,
                "metadata": {
                    "author": "张三",
                    "version": "1.0"
                }
            }
        }

class KnowledgeCreateRequest(BaseModel):
    """创建知识库请求模型"""
    name: str = Field(..., description="知识库名称")
    description: str = Field(..., description="知识库描述")
    vector_dimension: int = Field(1536, description="向量维度")
    similarity_threshold: float = Field(0.8, description="相似度阈值")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "技术文档库",
                "description": "包含技术文档和API说明",
                "vector_dimension": 1536,
                "similarity_threshold": 0.8
            }
        }

class KnowledgeUpdateRequest(BaseModel):
    """更新知识库请求模型"""
    name: Optional[str] = Field(None, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    vector_dimension: Optional[int] = Field(None, description="向量维度")
    similarity_threshold: Optional[float] = Field(None, description="相似度阈值")
    status: Optional[str] = Field(None, description="状态")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "更新后的知识库名称",
                "description": "更新后的描述",
                "similarity_threshold": 0.9
            }
        }

class DocumentUploadRequest(BaseModel):
    """文档上传请求模型"""
    name: str = Field(..., description="文档名称")
    content: str = Field(..., description="文档内容")
    file_type: str = Field(..., description="文件类型")
    file_size: int = Field(..., description="文件大小")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "用户手册.txt",
                "content": "产品使用说明...",
                "file_type": "text/plain",
                "file_size": 1024,
                "metadata": {
                    "author": "李四",
                    "version": "2.0"
                }
            }
        }

class KnowledgeStats(BaseModel):
    """知识库统计信息模型"""
    total_knowledge_bases: int = Field(..., description="知识库总数")
    total_documents: int = Field(..., description="文档总数")
    active_knowledge_bases: int = Field(..., description="活跃知识库数")
    processing_documents: int = Field(..., description="处理中的文档数")
    failed_documents: int = Field(..., description="失败的文档数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_knowledge_bases": 5,
                "total_documents": 150,
                "active_knowledge_bases": 4,
                "processing_documents": 2,
                "failed_documents": 1
            }
        }

# 数据库操作函数
def create_knowledge_base(db, knowledge_data: KnowledgeCreateRequest, user_id: str) -> Knowledge:
    """创建知识库"""
    knowledge_dict = knowledge_data.dict()
    knowledge_dict['user_id'] = user_id
    knowledge_dict['created_at'] = datetime.now()
    knowledge_dict['updated_at'] = datetime.now()
    
    result = db.knowledge_bases.insert_one(knowledge_dict)
    knowledge_dict['_id'] = str(result.inserted_id)
    
    return Knowledge(**knowledge_dict)

def get_knowledge_base(db, knowledge_id: str) -> Optional[Knowledge]:
    """获取知识库"""
    try:
        knowledge_dict = db.knowledge_bases.find_one({"_id": ObjectId(knowledge_id)})
        if knowledge_dict:
            knowledge_dict['_id'] = str(knowledge_dict['_id'])
            return Knowledge(**knowledge_dict)
    except Exception as e:
        print(f"获取知识库失败: {e}")
    return None

def get_user_knowledge_bases(db, user_id: str) -> List[Knowledge]:
    """获取用户的知识库列表"""
    knowledge_bases = []
    try:
        cursor = db.knowledge_bases.find({"user_id": user_id})
        for knowledge_dict in cursor:
            knowledge_dict['_id'] = str(knowledge_dict['_id'])
            knowledge_bases.append(Knowledge(**knowledge_dict))
    except Exception as e:
        print(f"获取用户知识库失败: {e}")
    return knowledge_bases

def update_knowledge_base(db, knowledge_id: str, update_data: KnowledgeUpdateRequest) -> bool:
    """更新知识库"""
    try:
        update_dict = update_data.dict(exclude_unset=True)
        update_dict['updated_at'] = datetime.now()
        
        result = db.knowledge_bases.update_one(
            {"_id": ObjectId(knowledge_id)},
            {"$set": update_dict}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"更新知识库失败: {e}")
        return False

def delete_knowledge_base(db, knowledge_id: str) -> bool:
    """删除知识库"""
    try:
        # 删除知识库
        result = db.knowledge_bases.delete_one({"_id": ObjectId(knowledge_id)})
        # 删除相关文档
        db.knowledge_documents.delete_many({"knowledge_id": knowledge_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"删除知识库失败: {e}")
        return False

def create_document(db, document_data: DocumentUploadRequest, knowledge_id: str, user_id: str) -> KnowledgeDocument:
    """创建文档"""
    document_dict = document_data.dict()
    document_dict['knowledge_id'] = knowledge_id
    document_dict['user_id'] = user_id
    document_dict['created_at'] = datetime.now()
    document_dict['updated_at'] = datetime.now()
    
    result = db.knowledge_documents.insert_one(document_dict)
    document_dict['_id'] = str(result.inserted_id)
    
    return KnowledgeDocument(**document_dict)

def get_document(db, document_id: str) -> Optional[KnowledgeDocument]:
    """获取文档"""
    try:
        document_dict = db.knowledge_documents.find_one({"_id": ObjectId(document_id)})
        if document_dict:
            document_dict['_id'] = str(document_dict['_id'])
            return KnowledgeDocument(**document_dict)
    except Exception as e:
        print(f"获取文档失败: {e}")
    return None

def get_knowledge_documents(db, knowledge_id: str) -> List[KnowledgeDocument]:
    """获取知识库的文档列表"""
    documents = []
    try:
        cursor = db.knowledge_documents.find({"knowledge_id": knowledge_id})
        for document_dict in cursor:
            document_dict['_id'] = str(document_dict['_id'])
            documents.append(KnowledgeDocument(**document_dict))
    except Exception as e:
        print(f"获取知识库文档失败: {e}")
    return documents

def update_document_status(db, document_id: str, status: str, vector_embedding: Optional[List[float]] = None) -> bool:
    """更新文档状态"""
    try:
        update_dict = {"status": status, "updated_at": datetime.now()}
        if vector_embedding:
            update_dict['vector_embedding'] = vector_embedding
        
        result = db.knowledge_documents.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": update_dict}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"更新文档状态失败: {e}")
        return False

def delete_document(db, document_id: str) -> bool:
    """删除文档"""
    try:
        result = db.knowledge_documents.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0
    except Exception as e:
        print(f"删除文档失败: {e}")
        return False

def get_knowledge_stats(db, user_id: str) -> KnowledgeStats:
    """获取知识库统计信息"""
    try:
        total_kb = db.knowledge_bases.count_documents({"user_id": user_id})
        active_kb = db.knowledge_bases.count_documents({"user_id": user_id, "status": "active"})
        total_docs = db.knowledge_documents.count_documents({"user_id": user_id})
        processing_docs = db.knowledge_documents.count_documents({"user_id": user_id, "status": "processing"})
        failed_docs = db.knowledge_documents.count_documents({"user_id": user_id, "status": "failed"})
        
        return KnowledgeStats(
            total_knowledge_bases=total_kb,
            total_documents=total_docs,
            active_knowledge_bases=active_kb,
            processing_documents=processing_docs,
            failed_documents=failed_docs
        )
    except Exception as e:
        print(f"获取统计信息失败: {e}")
        return KnowledgeStats(
            total_knowledge_bases=0,
            total_documents=0,
            active_knowledge_bases=0,
            processing_documents=0,
            failed_documents=0
        ) 