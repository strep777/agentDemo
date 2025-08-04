#!/usr/bin/env python3
"""
测试models模块导入
"""

def test_models_import():
    """测试models模块导入"""
    try:
        print("🔍 测试models模块导入...")
        
        # 测试基础导入
        from app.routes.models import models_bp
        print("✅ models_bp导入成功")
        
        # 测试数据库服务导入
        from app.services.database import get_db
        print("✅ get_db导入成功")
        
        # 测试Ollama服务导入
        from app.services.ollama import OllamaService
        print("✅ OllamaService导入成功")
        
        # 测试认证工具导入
        from app.utils.auth import token_required
        print("✅ token_required导入成功")
        
        # 测试响应工具导入
        from app.utils.response import ApiResponse, handle_exception, validate_pagination, validate_required_fields, sanitize_data, serialize_mongo_data
        print("✅ 响应工具导入成功")
        
        # 测试其他依赖导入
        from bson import ObjectId
        from datetime import datetime
        import json
        print("✅ 其他依赖导入成功")
        
        print("✅ 所有导入测试通过")
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_models_import() 