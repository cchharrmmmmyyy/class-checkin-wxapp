from flask import Blueprint, jsonify, request
from services import AdminService
from utils.jwt import token_required, role_required

admin_user_bp = Blueprint('admin_user', __name__, url_prefix='/api/admin')


@admin_user_bp.route('/users', methods=['GET'])
@token_required
@role_required(['admin'])
def get_users():
    class_name = request.args.get('class_name', '').strip() or None
    role = request.args.get('role', '').strip() or None
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 50, type=int)

    result = AdminService.list_users_paginated(
        class_name=class_name, role=role, page=page, size=size
    )
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_user_bp.route('/users', methods=['POST'])
@token_required
@role_required(['admin'])
def create_user():
    data = request.get_json()
    username = data.get('username', '').strip()
    user_id = data.get('user_id', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', '').strip()
    class_name = data.get('class', '').strip()

    if not username or not user_id or not password or not role:
        return jsonify({'code': 5000, 'message': '用户名、密码、角色和用户ID不能为空'}), 400

    result = AdminService.save_user(username, user_id, password, role, class_name)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_user_bp.route('/users/<user_id>', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_user(user_id):
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', '').strip()
    class_name = data.get('class', '').strip()

    result = AdminService.save_user(username, user_id, password, role, class_name)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_user_bp.route('/users/<user_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_user(user_id):
    result = AdminService.delete_user(user_id)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_user_bp.route('/users/reset-password', methods=['POST'])
@token_required
@role_required(['admin'])
def admin_reset_password():
    data = request.get_json()
    user_id = data.get('user_id', '').strip()

    if not user_id:
        return jsonify({'code': 5000, 'message': '用户ID不能为空'}), 400

    result = AdminService.reset_password(user_id)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200
