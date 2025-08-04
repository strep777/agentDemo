#!/usr/bin/env python3
"""
简单测试models路由
"""

from flask import Flask
from app.routes.models import models_bp
from app.utils.auth import token_required
import os

# 设置开发环境
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

def test_models_route():
    """测试models路由"""
    try:
        print("🔍 测试models路由...")
        
        # 创建测试应用
        app = Flask(__name__)
        app.register_blueprint(models_bp, url_prefix='/api/models')
        
        print("✅ Flask应用创建成功")
        print("✅ models蓝图注册成功")
        
        # 测试路由注册
        with app.test_client() as client:
            print("✅ 测试客户端创建成功")
            
            # 测试GET /api/models端点
            response = client.get('/api/models', headers={
                'Authorization': 'Bearer dev-token-12345'
            })
            
            print(f"📊 响应状态码: {response.status_code}")
            print(f"📊 响应数据: {response.get_data(as_text=True)}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_models_route() 