"""
认证路由模块
提供登录、修改密码、获取当前用户信息等接口
"""
from flask import Blueprint, jsonify, request
from services import AuthService
from utils.api_response import success, error

auth_bp = Blueprint('auth', __name__, url_prefix='/api')


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    统一登录接口（小程序 + 网页管理后台）
    ---
    请求头: X-Client-Type: miniprogram（小程序端必传，网页端不传）
    请求体: {"user_id": "xxx", "password": "xxx"}
    """
    data = request.get_json()
    user_id = data.get('user_id', '').strip()
    password = data.get('password', '').strip()
    is_web = request.headers.get('X-Client-Type') != 'miniprogram'

    if not user_id or not password:
        return error('学号/工号和密码不能为空', 1000, 400)

    if len(user_id) < 6 or len(user_id) > 12:
        return error('学号/工号或密码错误', 1000, 400)

    if len(password) < 6 or len(password) > 20:
        return error('学号/工号或密码错误', 1000, 400)

    result = AuthService.login(user_id, password)

    if is_web and result['user']['role'] != 'admin':
        return error('无管理员权限', 2003, 403)

    resp, status = success(result)

    if is_web:
        resp.set_cookie('adminToken', result['token'],
                        httponly=True, max_age=86400)

    return resp, status


@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """
    修改密码接口（需要登录）
    ---
    请求体: {"old_password": "xxx", "new_password": "xxx"}
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    from utils.jwt import token_required

    @token_required
    def _change_password():
        data = request.get_json()
        old_password = data.get('old_password', '').strip()
        new_password = data.get('new_password', '').strip()

        if not old_password or not new_password:
            return jsonify({
                'code': 1007,
                'message': '原密码和新密码不能为空'
            }), 400

        user_id = request.current_user['user_id']
        result = AuthService.change_password(user_id, old_password, new_password)

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': result
        }), 200

    return _change_password()


@auth_bp.route('/current-user', methods=['GET'])
def get_current_user():
    """
    获取当前用户信息（需要登录）
    ---
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    from utils.jwt import token_required

    @token_required
    def _get_current_user():
        user = request.current_user
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'user_id': user.get('user_id'),
                'username': user.get('username'),
                'role': user.get('role'),
                'class': user.get('class')
            }
        }), 200

    return _get_current_user()