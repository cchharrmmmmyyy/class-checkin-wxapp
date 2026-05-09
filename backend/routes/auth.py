"""
认证路由模块
提供登录、修改密码
"""
from flask import Blueprint, request
from services import AuthService
from utils.jwt import token_required
from utils.api_response import success
from utils.exceptions import ServiceException
from utils.error_codes import (
    JSON_INVALID, AUTH_CREDENTIALS_MISSING, AUTH_CREDENTIALS_INVALID,
    AUTH_PASSWORD_CHANGE_MISSING, PERM_ROLE_DENIED
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api')


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    user_id = (data.get('user_id') or '').strip()
    password = (data.get('password') or '').strip()
    is_web = request.headers.get('X-Client-Type') != 'miniprogram'

    if not user_id or not password:
        raise ServiceException('学号/工号和密码不能为空', code=AUTH_CREDENTIALS_MISSING)

    if len(user_id) < 6 or len(user_id) > 12:
        raise ServiceException('学号/工号或密码错误', code=AUTH_CREDENTIALS_INVALID)

    if len(password) < 6 or len(password) > 20:
        raise ServiceException('学号/工号或密码错误', code=AUTH_CREDENTIALS_INVALID)

    result = AuthService.login(user_id, password)

    if is_web and result['user']['role'] != 'admin':
        raise ServiceException('无管理员权限', code=PERM_ROLE_DENIED, http_status=403)

    resp, status = success(result)

    if is_web:
        resp.set_cookie('token', result['token'],
                       httponly=True, max_age=86400)

    return resp, status


@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    old_password = (data.get('old_password') or '').strip()
    new_password = (data.get('new_password') or '').strip()

    if not old_password or not new_password:
        raise ServiceException('原密码和新密码不能为空', code=AUTH_PASSWORD_CHANGE_MISSING)

    user_id = request.current_user['user_id']
    result = AuthService.change_password(user_id, old_password, new_password)

    return success(data=result)
