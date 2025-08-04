from functools import wraps
from flask import request, jsonify
import jwt
from bson import ObjectId
from app.services.database import get_db
import os

# JWT配置
SECRET_KEY = 'your-secret-key-here'
ALGORITHM = 'HS256'

def verify_token(token: str):
    """验证JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """JWT token验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        # 调试信息
        print(f"🔐 认证检查: {request.method} {request.path}")
        print(f"🔑 Authorization Header: {auth_header}")
        print(f"🌍 FLASK_ENV: {os.environ.get('FLASK_ENV')}")
        print(f"🌍 FLASK_DEBUG: {os.environ.get('FLASK_DEBUG')}")
        print(f"🔧 所有请求头: {dict(request.headers)}")
        print(f"🔧 请求方法: {request.method}")
        print(f"🔧 请求路径: {request.path}")
        print(f"🔧 请求URL: {request.url}")
        
        # 开发环境认证绕过
        if os.environ.get('FLASK_ENV') == 'development' or os.environ.get('FLASK_DEBUG') == '1':
            print("🌍 开发环境检测到")
            print(f"🔍 检查认证头: '{auth_header}'")
            print(f"🔍 环境变量检查: FLASK_ENV={os.environ.get('FLASK_ENV')}, FLASK_DEBUG={os.environ.get('FLASK_DEBUG')}")
            print(f"🔍 期望的认证头: 'Bearer dev-token-12345'")
            print(f"🔍 实际认证头: '{auth_header}'")
            print(f"🔍 认证头是否匹配: {auth_header == 'Bearer dev-token-12345'}")
            
            # 开发环境下，允许空认证头或正确的认证头
            if auth_header is None or auth_header == 'Bearer dev-token-12345':
                print("✅ 开发环境认证绕过成功")
                # 创建模拟用户
                current_user = {
                    'id': 'dev-user-12345',
                    'username': 'dev_user',
                    'email': 'dev@example.com',
                    'role': 'admin'
                }
                return f(current_user, *args, **kwargs)
            else:
                print(f"❌ 开发环境认证失败，期望: 'Bearer dev-token-12345' 或 None，实际: '{auth_header}'")
                return jsonify({'success': False, 'message': '开发环境认证失败'}), 401
        else:
            print("🌍 生产环境检测到")
        
        # 生产环境检查
        if not auth_header:
            print("❌ 未提供认证头")
            return jsonify({'success': False, 'message': '未提供认证头'}), 401
        
        if not auth_header.startswith('Bearer '):
            print("❌ 未提供有效的认证token")
            print(f"🔍 认证头内容: '{auth_header}'")
            return jsonify({'success': False, 'message': '未提供有效的认证token'}), 401
        
        token = auth_header.split(' ')[1]
        print(f"🔑 提取的token: {token}")
        payload = verify_token(token)
        
        if not payload:
            print("❌ token无效或已过期")
            return jsonify({'success': False, 'message': 'token无效或已过期'}), 401
        
        # 获取用户信息
        db = get_db()
        user = db.users.find_one({'_id': ObjectId(payload['user_id'])})
        
        if not user:
            print("❌ 用户不存在")
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 检查用户状态
        if user.get('status') != 'active':
            print("❌ 账户已被禁用")
            return jsonify({'success': False, 'message': '账户已被禁用'}), 401
        
        # 将用户信息传递给视图函数
        current_user = {
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'role': user.get('role', 'user')
        }
        
        print("✅ 认证成功")
        return f(current_user, *args, **kwargs)
    
    return decorated 