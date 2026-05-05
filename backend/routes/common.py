"""
通用路由模块
提供通知、操作日志等通用功能的接口
"""
from flask import Blueprint, request
from services import NotificationService, LogService
from utils.jwt import token_required, role_required
from utils.api_response import success
from utils.exceptions import ServiceException

common_bp = Blueprint('common', __name__, url_prefix='/api')


# 获取通知列表
@common_bp.route('/notifications', methods=['GET'])
@token_required
def get_notifications():
    user_id = request.current_user['user_id']
    notification_type = request.args.get('type')
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 50, type=int)

    notifications = NotificationService.get_user_notifications(
        user_id,
        notification_type=notification_type,
        is_read=not unread_only if unread_only else None,
        page=page,
        size=size
    )
    return success(data=notifications)


# 标记通知已读
@common_bp.route('/notifications/mark-read', methods=['POST'])
@token_required
def mark_notification_read():
    user_id = request.current_user['user_id']
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=4999)
    notification_id = data.get('notification_id')

    if not notification_id:
        raise ServiceException('通知ID不能为空', code=8001)

    result = NotificationService.mark_as_read(notification_id, user_id)
    return success(data={'marked': result})


# 获取未读通知数量
@common_bp.route('/notifications/unread-count', methods=['GET'])
@token_required
def get_unread_count():
    user_id = request.current_user['user_id']
    notification_type = request.args.get('type')
    count = NotificationService.get_unread_count(user_id, notification_type)
    return success(data={'count': count})


# 获取操作日志
@common_bp.route('/operation-logs', methods=['GET'])
@token_required
@role_required(['admin', 'teacher'])
def get_operation_logs():
    target_type = request.args.get('target_type')
    target_id = request.args.get('target_id')
    operator_id = request.args.get('operator_id')
    operation_type = request.args.get('operation_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 50, type=int)

    logs = LogService.get_operation_logs(
        target_type=target_type,
        target_id=target_id,
        operator_id=operator_id,
        operation_type=operation_type,
        start_date=start_date,
        end_date=end_date,
        page=page,
        size=size
    )
    return success(data=logs)
