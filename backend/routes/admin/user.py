from flask import Blueprint, request
from services import AdminUserService
from utils.jwt import token_required, role_required
from utils.api_response import success
from utils.exceptions import ServiceException
from utils.error_codes import JSON_INVALID, USER_INFO_INCOMPLETE

admin_user_bp = Blueprint('admin_user', __name__, url_prefix='/api/admin')


@admin_user_bp.route('/users', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def get_users():
    class_name = request.args.get('class_name', '').strip() or None
    role = request.args.get('role', '').strip() or None
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 50, type=int)

    result = AdminUserService.list_users_paginated(
        class_name=class_name, role=role, page=page, size=size
    )
    return success(data=result)


@admin_user_bp.route('/users', methods=['POST'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def create_user():
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    username = (data.get('username') or '').strip()
    user_id = (data.get('user_id') or '').strip()
    password = (data.get('password') or '').strip()
    role = (data.get('role') or '').strip()
    class_name = (data.get('class') or '').strip()
    real_name = (data.get('real_name') or '').strip()
    student_id = (data.get('student_id') or '').strip()

    if not username or not user_id or not password or not role or not class_name:
        raise ServiceException('用户名、用户ID、密码、角色和班级不能为空', code=USER_INFO_INCOMPLETE)

    result = AdminUserService.save_user(username, user_id, password, role, class_name, real_name, student_id)
    return success(data=result)


@admin_user_bp.route('/users/<user_id>', methods=['PUT'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def update_user(user_id):
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    role = (data.get('role') or '').strip()
    class_name = (data.get('class') or '').strip()
    real_name = (data.get('real_name') or '').strip()
    student_id = (data.get('student_id') or '').strip()

    result = AdminUserService.save_user(username, user_id, password, role, class_name, real_name, student_id)
    return success(data=result)


@admin_user_bp.route('/users/<user_id>', methods=['DELETE'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def delete_user(user_id):
    result = AdminUserService.delete_user(user_id)
    return success(data=result)


@admin_user_bp.route('/users/reset-password', methods=['POST'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def admin_reset_password():
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    user_id = (data.get('user_id') or '').strip()

    if not user_id:
        raise ServiceException('用户ID不能为空', code=USER_INFO_INCOMPLETE)

    result = AdminUserService.reset_password(user_id)
    return success(data=result)
