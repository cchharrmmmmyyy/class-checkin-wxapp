"""
认证模块
负责用户认证和授权,包括生成JWT令牌、验证令牌和装饰器
"""

import jwt
import datetime
from datetime import timezone
from functools import wraps
from flask import request
from config import Config
from utils.exceptions import AuthenticationException

SECRET_KEY = Config.SECRET_KEY
TOKEN_EXPIRE_HOURS = Config.TOKEN_EXPIRE_HOURS

def generate_token(user_id, username, role, user_class=''):
    """
    生成JWT令牌
    """
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'class': user_class,
        'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=TOKEN_EXPIRE_HOURS),
        'iat': datetime.datetime.now(timezone.utc)
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

def token_required(f=None, *, allow_cookie=False):
    """
    装饰器：验证JWT令牌
    allow_cookie: 是否支持从Cookie获取token（网页端用）
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None

            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                try:
                    token = auth_header.split(' ')[1]
                except IndexError:
                    raise AuthenticationException('令牌格式错误')
            elif 'token' in request.args:
                token = request.args['token']
            elif allow_cookie and 'token' in request.cookies:
                token = request.cookies.get('token')

            if not token:
                raise AuthenticationException('缺少令牌')

            payload = decode_token(token)
            if not payload:
                raise AuthenticationException('令牌无效或已过期')

            request.current_user = payload
            return f(*args, **kwargs)

        return decorated

    if f is not None:
        return decorator(f)
    return decorator

def role_required(allowed_roles):
    """
    装饰器：验证用户角色权限
    allowed_roles: 可以是单个角色字符串或角色列表
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                raise AuthenticationException('请先登录')

            user_role = request.current_user.get('role')
            if user_role not in allowed_roles:
                raise AuthenticationException(
                    f'权限不足，需要角色: {", ".join(allowed_roles)}',
                    code=403,
                    http_status=403
                )

            return f(*args, **kwargs)
        return decorated
    return decorator
