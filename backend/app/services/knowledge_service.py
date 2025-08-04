import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from app.services.database import get_db

class KnowledgeService:
    def __init__(self):
        self.db = get_db()
    
    def get_knowledge_bases(self, user_id: str, page: int = 1, page_size: int = 20, search: str = "") -> Dict[str, Any]:
        """获取知识库列表"""
        try:
            # 构建查询条件
            query = {'user_id': user_id}
            if search:
                query['name'] = {'$regex': search, '$options': 'i'}
            
            # 计算总数
            total = self.db.knowledge_bases.count_documents(query)
            
            # 获取分页数据
            skip = (page - 1) * page_size
            bases = list(self.db.knowledge_bases.find(query)
                        .skip(skip)
                        .limit(page_size)
                        .sort('created_at', -1))
            
            # 格式化数据
            for base in bases:
                base['id'] = str(base['_id'])
                base['created_at'] = base['created_at'].isoformat() if base.get('created_at') else None
                base['updated_at'] = base['updated_at'].isoformat() if base.get('updated_at') else None
                del base['_id']
            
            return {
                'items': bases,
                'total': total,
                'page': page,
                'page_size': page_size
            }
            
        except Exception as e:
            raise Exception(f"获取知识库列表失败: {str(e)}")
    
    def create_knowledge_base(self, name: str, description: str, user_id: str, 
                             vector_dimension: int = 384, similarity_threshold: float = 0.7) -> Dict[str, Any]:
        """创建知识库"""
        try:
            knowledge_base = {
                'name': name,
                'description': description,
                'user_id': user_id,
                'vector_dimension': vector_dimension,
                'similarity_threshold': similarity_threshold,
                'document_count': 0,
                'total_tokens': 0,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'is_active': True
            }
            
            result = self.db.knowledge_bases.insert_one(knowledge_base)
            knowledge_base['id'] = str(result.inserted_id)
            del knowledge_base['_id']
            
            return knowledge_base
            
        except Exception as e:
            raise Exception(f"创建知识库失败: {str(e)}")
    
    def get_knowledge_base(self, knowledge_base_id: str, user_id: str) -> Dict[str, Any]:
        """获取知识库详情"""
        try:
            if not ObjectId.is_valid(knowledge_base_id):
                raise Exception("无效的知识库ID")
            
            base = self.db.knowledge_bases.find_one({
                '_id': ObjectId(knowledge_base_id),
                'user_id': user_id
            })
            
            if not base:
                raise Exception("知识库不存在")
            
            base['id'] = str(base['_id'])
            base['created_at'] = base['created_at'].isoformat() if base.get('created_at') else None
            base['updated_at'] = base['updated_at'].isoformat() if base.get('updated_at') else None
            del base['_id']
            
            return base
            
        except Exception as e:
            raise Exception(f"获取知识库详情失败: {str(e)}")
    
    def update_knowledge_base(self, knowledge_base_id: str, user_id: str, update_data: Dict[str, Any]) -> bool:
        """更新知识库"""
        try:
            if not ObjectId.is_valid(knowledge_base_id):
                raise Exception("无效的知识库ID")
            
            update_data['updated_at'] = datetime.now()
            
            result = self.db.knowledge_bases.update_one(
                {'_id': ObjectId(knowledge_base_id), 'user_id': user_id},
                {'$set': update_data}
            )
            
            if result.matched_count == 0:
                raise Exception("知识库不存在")
            
            return True
            
        except Exception as e:
            raise Exception(f"更新知识库失败: {str(e)}")
    
    def delete_knowledge_base(self, knowledge_base_id: str, user_id: str) -> bool:
        """删除知识库"""
        try:
            if not ObjectId.is_valid(knowledge_base_id):
                raise Exception("无效的知识库ID")
            
            # 删除知识库
            result = self.db.knowledge_bases.delete_one({
                '_id': ObjectId(knowledge_base_id),
                'user_id': user_id
            })
            
            if result.deleted_count == 0:
                raise Exception("知识库不存在")
            
            # 删除相关文档
            self.db.documents.delete_many({'knowledge_base_id': knowledge_base_id})
            
            return True
            
        except Exception as e:
            raise Exception(f"删除知识库失败: {str(e)}")
    
    def upload_document(self, knowledge_base_id: str, user_id: str, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """上传文档到知识库"""
        try:
            if not ObjectId.is_valid(knowledge_base_id):
                raise Exception("无效的知识库ID")
            
            # 验证知识库归属
            base = self.db.knowledge_bases.find_one({
                '_id': ObjectId(knowledge_base_id),
                'user_id': user_id
            })
            
            if not base:
                raise Exception("知识库不存在")
            
            # 创建文档记录
            document = {
                'knowledge_base_id': knowledge_base_id,
                'name': file_data.get('name', ''),
                'content': file_data.get('content', ''),
                'file_type': file_data.get('file_type', 'text'),
                'file_size': file_data.get('file_size', 0),
                'token_count': file_data.get('token_count', 0),
                'user_id': user_id,
                'created_at': datetime.now(),
                'is_active': True
            }
            
            result = self.db.documents.insert_one(document)
            document['id'] = str(result.inserted_id)
            del document['_id']
            
            # 更新知识库统计信息
            self.db.knowledge_bases.update_one(
                {'_id': ObjectId(knowledge_base_id)},
                {
                    '$inc': {
                        'document_count': 1,
                        'total_tokens': document['token_count']
                    },
                    '$set': {'updated_at': datetime.now()}
                }
            )
            
            return document
            
        except Exception as e:
            raise Exception(f"上传文档失败: {str(e)}")
    
    def search_knowledge(self, knowledge_base_id: str, user_id: str, query: str, 
                        limit: int = 5) -> List[Dict[str, Any]]:
        """搜索知识库"""
        try:
            if not ObjectId.is_valid(knowledge_base_id):
                raise Exception("无效的知识库ID")
            
            # 验证知识库归属
            base = self.db.knowledge_bases.find_one({
                '_id': ObjectId(knowledge_base_id),
                'user_id': user_id
            })
            
            if not base:
                raise Exception("知识库不存在")
            
            # 简单的文本搜索（可以后续集成向量搜索）
            documents = list(self.db.documents.find({
                'knowledge_base_id': knowledge_base_id,
                'is_active': True,
                '$or': [
                    {'name': {'$regex': query, '$options': 'i'}},
                    {'content': {'$regex': query, '$options': 'i'}}
                ]
            }).limit(limit))
            
            # 格式化结果
            for doc in documents:
                doc['id'] = str(doc['_id'])
                doc['created_at'] = doc['created_at'].isoformat() if doc.get('created_at') else None
                del doc['_id']
            
            return documents
            
        except Exception as e:
            raise Exception(f"搜索知识库失败: {str(e)}")
    
    def delete_document(self, document_id: str, user_id: str) -> bool:
        """删除文档"""
        try:
            if not ObjectId.is_valid(document_id):
                raise Exception("无效的文档ID")
            
            # 获取文档信息
            document = self.db.documents.find_one({
                '_id': ObjectId(document_id),
                'user_id': user_id
            })
            
            if not document:
                raise Exception("文档不存在")
            
            # 删除文档
            result = self.db.documents.delete_one({
                '_id': ObjectId(document_id),
                'user_id': user_id
            })
            
            if result.deleted_count == 0:
                raise Exception("文档不存在")
            
            # 更新知识库统计信息
            self.db.knowledge_bases.update_one(
                {'_id': ObjectId(document['knowledge_base_id'])},
                {
                    '$inc': {
                        'document_count': -1,
                        'total_tokens': -document.get('token_count', 0)
                    },
                    '$set': {'updated_at': datetime.now()}
                }
            )
            
            return True
            
        except Exception as e:
            raise Exception(f"删除文档失败: {str(e)}")
    
    def get_relevant_context_sync(self, query: str, knowledge_base_ids: List[str]) -> str:
        """同步获取相关上下文"""
        try:
            if not knowledge_base_ids:
                return ""
            
            # 从所有知识库中搜索相关内容
            all_results = []
            for base_id in knowledge_base_ids:
                if ObjectId.is_valid(base_id):
                    documents = list(self.db.documents.find({
                        'knowledge_base_id': base_id,
                        'is_active': True,
                        '$or': [
                            {'name': {'$regex': query, '$options': 'i'}},
                            {'content': {'$regex': query, '$options': 'i'}}
                        ]
                    }).limit(3))
                    
                    all_results.extend(documents)
            
            # 按相关性排序（这里使用简单的文本匹配，可以后续优化）
            relevant_docs = sorted(all_results, key=lambda x: len(x.get('content', '')), reverse=True)[:5]
            
            # 构建上下文
            context_parts = []
            for doc in relevant_docs:
                context_parts.append(f"文档: {doc.get('name', '')}\n内容: {doc.get('content', '')}")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            print(f"获取相关上下文失败: {str(e)}")
            return ""
    
    async def get_relevant_context(self, query: str, knowledge_base_ids: List[str]) -> str:
        """异步获取相关上下文"""
        # 对于异步版本，暂时使用同步实现
        return self.get_relevant_context_sync(query, knowledge_base_ids) 