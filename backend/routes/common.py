"""
通用路由模块
提供通知、操作日志等通用功能的接口
"""
from flask import Blueprint, jsonify, request
from services import NotificationService, LogService
from utils.auth import token_required, role_required

common_bp = Blueprint('common', __name__, url_prefix='/api')


@common_bp.route('/notifications', methods=['GET'])
@token_required
def get_notifications():
    """
    获取当前用户的通知列表
    ---
    查询参数: type, unread_only, limit, offset
    返回: {"code": 200, "message": "success", "data": [...]}
    """
    user_id = request.current_user['user_id']
    notification_type = request.args.get('type')
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    notifications = NotificationService.get_user_notifications(
        user_id,
        notification_type=notification_type,
        is_read=not unread_only if unread_only else None,
        limit=limit,
        offset=offset
    )
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': notifications
    }), 200


@common_bp.route('/notifications/mark-read', methods=['POST'])
@token_required
def mark_notification_read():
    """
    标记通知已读
    ---
    请求体: {"notification_id": 1}
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    user_id = request.current_user['user_id']
    data = request.get_json()
    notification_id = data.get('notification_id')

    if not notification_id:
        return jsonify({
            'code': 8001,
            'message': '通知ID不能为空'
        }), 400

    result = NotificationService.mark_as_read(notification_id, user_id)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {'marked': result}
    }), 200


@common_bp.route('/notifications/unread-count', methods=['GET'])
@token_required
def get_unread_count():
    """
    获取未读通知数量
    ---
    返回: {"code": 200, "message": "success", "data": {"count": N}}
    """
    user_id = request.current_user['user_id']
    notification_type = request.args.get('type')
    count = NotificationService.get_unread_count(user_id, notification_type)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {'count': count}
    }), 200


@common_bp.route('/operation-logs', methods=['GET'])
@token_required
@role_required(['admin', 'teacher'])
def get_operation_logs():
    """
    获取操作日志（管理员和教师可用）
    ---
    查询参数: target_type, target_id, operator_id, operation_type, start_date, end_date, limit, offset
    返回: {"code": 200, "message": "success", "data": [...]}
    """
    target_type = request.args.get('target_type')
    target_id = request.args.get('target_id')
    operator_id = request.args.get('operator_id')
    operation_type = request.args.get('operation_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    logs = LogService.get_operation_logs(
        target_type=target_type,
        target_id=target_id,
        operator_id=operator_id,
        operation_type=operation_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': logs
    }), 200