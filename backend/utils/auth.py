"""
认证模块
负责用户认证和授权，包括生成JWT令牌、验证令牌和装饰器
"""

import jwt
import datetime
import os
from functools import wraps
from flask import request, jsonify

SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
TOKEN_EXPIRE_HOURS = 24

def generate_token(user_id, username, role, user_class=''):
    """
    生成JWT令牌
    """
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'class': user_class,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRE_HOURS),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def decode_token(token):
    """
    解析JWT令牌
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """
    装饰器：验证JWT令牌
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'success': False, 'message': '令牌格式错误'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': '缺少令牌'}), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({'success': False, 'message': '令牌无效或已过期'}), 401
        
        request.user_info = payload
        return f(*args, **kwargs)
    
    return decorated

def role_required(*allowed_roles):
    """
    装饰器：验证用户角色权限
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'user_info'):
                return jsonify({'success': False, 'message': '请先登录'}), 401
            
            user_role = request.user_info.get('role')
            if user_role not in allowed_roles:
                return jsonify({
                    'success': False, 
                    'message': f'权限不足，需要角色: {", ".join(allowed_roles)}'
                }), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator
