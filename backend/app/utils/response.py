"""
统一API响应格式和异常处理
"""

from functools import wraps
from flask import jsonify
from typing import Any, Dict, Optional, Union
import json
from datetime import datetime
from bson import ObjectId

def serialize_mongo_data(data):
    """序列化MongoDB数据，处理ObjectId和datetime"""
    if isinstance(data, dict):
        return {k: serialize_mongo_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_mongo_data(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, datetime):
        return data.isoformat()
    else:
        return data

class ApiResponse:
    """统一API响应格式"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功", code: int = 200) -> Dict:
        """成功响应"""
        response = {
            "success": True,
            "code": code,
            "message": message
        }
        if data is not None:
            response["data"] = data
        return response
    
    @staticmethod
    def error(message: str = "操作失败", code: int = 400, data: Any = None) -> Dict:
        """错误响应"""
        response = {
            "success": False,
            "code": code,
            "message": message
        }
        if data is not None:
            response["data"] = data
        return response
    
    @staticmethod
    def paginated(data: list, total: int, page: int, page_size: int, 
                  message: str = "获取数据成功") -> Dict:
        """分页响应"""
        return {
            "success": True,
            "code": 200,
            "message": message,
            "data": {
                "items": data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size
            }
        }

def handle_exception(f):
    """异常处理装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify(ApiResponse.error(str(e))), 500
    return decorated_function

def validate_pagination(page: int, page_size: int, max_page_size: int = 100) -> tuple:
    """验证分页参数"""
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20
    if page_size > max_page_size:
        page_size = max_page_size
    return page, page_size

def validate_required_fields(data: Dict, required_fields: list) -> None:
    """验证必需字段"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"缺少必需字段: {', '.join(missing_fields)}")

def sanitize_data(data: Dict, allowed_fields: list) -> Dict:
    """清理数据，只保留允许的字段"""
    return {k: v for k, v in data.items() if k in allowed_fields}

class ValidationError(Exception):
    """验证错误"""
    pass

class PermissionError(Exception):
    """权限错误"""
    pass

class ResourceNotFoundError(Exception):
    """资源不存在错误"""
    pass 