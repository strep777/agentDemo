from flask import Blueprint, request, jsonify, current_app
import bcrypt
import jwt
from datetime import datetime, timedelta
from app.services.database import get_db
from bson import ObjectId
import os

auth_bp = Blueprint('auth', __name__)

# JWT配置
SECRET_KEY = 'your-secret-key-here'
ALGORITHM = 'HS256'

def create_token(user_id: str, username: str):
    """创建JWT token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    """验证JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'success': False, 'message': '请填写所有必填字段'}), 400
        
        db = get_db()
        
        # 检查用户名是否已存在
        if db.users.find_one({'username': username}):
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        
        # 检查邮箱是否已存在
        if db.users.find_one({'email': email}):
            return jsonify({'success': False, 'message': '邮箱已存在'}), 400
        
        # 加密密码
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # 创建用户
        user = {
            'username': username,
            'email': email,
            'password': hashed_password.decode('utf-8'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'role': 'user',
            'status': 'active'
        }
        
        result = db.users.insert_one(user)
        
        # 创建token
        token = create_token(str(result.inserted_id), username)
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'data': {
                'token': token,
                'user': {
                    'id': str(result.inserted_id),
                    'username': username,
                    'email': email,
                    'role': 'user'
                }
            }
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'success': False, 'message': '请填写用户名和密码'}), 400
        
        db = get_db()
        
        # 查找用户
        user = db.users.find_one({'username': username})
        
        # 开发环境：如果用户不存在，自动创建用户
        is_dev = os.environ.get('FLASK_ENV') == 'development' or current_app.debug
        if not user and is_dev:
            try:
                # 创建默认用户
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                user = {
                    'username': username,
                    'email': f'{username}@example.com',
                    'password': hashed_password.decode('utf-8'),
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow(),
                    'role': 'user',
                    'status': 'active'
                }
                result = db.users.insert_one(user)
                user['_id'] = result.inserted_id
                print(f"开发环境：自动创建用户 {username}")
            except Exception as e:
                print(f"开发环境：自动创建用户失败 {username}: {e}")
                return jsonify({'success': False, 'message': '用户创建失败'}), 500
        
        if not user:
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
        
        # 验证密码
        if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
        
        # 检查用户状态
        if user.get('status') != 'active':
            return jsonify({'success': False, 'message': '账户已被禁用'}), 401
        
        # 创建token
        token = create_token(str(user['_id']), user['username'])
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'token': token,
                'user': {
                    'id': str(user['_id']),
                    'username': user['username'],
                    'email': user['email'],
                    'role': user.get('role', 'user')
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """获取用户信息"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未提供有效的认证token'}), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            return jsonify({'success': False, 'message': 'token无效或已过期'}), 401
        
        db = get_db()
        user = db.users.find_one({'_id': ObjectId(payload['user_id'])})
        
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'role': user.get('role', 'user'),
                'created_at': user['created_at'].isoformat() if user.get('created_at') else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户信息失败: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    # 由于使用JWT，客户端只需要删除token即可
    return jsonify({'success': True, 'message': '登出成功'}), 200 