"""
学生路由模块
提供学生打卡、请假、补卡、通知等功能的接口
"""
from flask import Blueprint, jsonify, request
from services import PunchService, LeaveService, MakeupService, NotificationService
from utils.auth import token_required, role_required

student_bp = Blueprint('student', __name__, url_prefix='/api/student')


@student_bp.route('/punch', methods=['POST'])
@token_required
@role_required(['student', 'monitor'])
def punch():
    """
    学生打卡接口
    ---
    请求体: {"latitude": 1.0, "longitude": 1.0, "device_id": "xxx"}
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    user_id = request.current_user['user_id']
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    device_id = data.get('device_id')

    result = PunchService.punch(user_id, latitude, longitude)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@student_bp.route('/punch-records', methods=['GET'])
@token_required
@role_required(['student', 'monitor'])
def get_punch_records():
    """
    获取学生打卡记录
    ---
    查询参数: start_date, end_date, limit, offset
    返回: {"code": 200, "message": "success", "data": [...]}
    """
    user_id = request.current_user['user_id']
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    records = PunchService.get_user_punch_records(
        user_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': records
    }), 200


@student_bp.route('/leave/apply', methods=['POST'])
@token_required
@role_required(['student', 'monitor'])
def apply_leave():
    """
    学生提交请假申请
    ---
    请求体: {"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "leave_type": "xxx", "reason": "xxx"}
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    user_id = request.current_user['user_id']
    data = request.get_json()
    start_date = data.get('start_date', '').strip()
    end_date = data.get('end_date', '').strip()
    leave_type = data.get('leave_type', 'personal')
    reason = data.get('reason', '')

    result = LeaveService.apply_leave(user_id, start_date, end_date)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@student_bp.route('/leave/records', methods=['GET'])
@token_required
@role_required(['student', 'monitor'])
def get_leave_records():
    """
    获取学生请假记录
    ---
    查询参数: status (pending/approved/rejected)
    返回: {"code": 200, "message": "success", "data": [...]}
    """
    user_id = request.current_user['user_id']
    status = request.args.get('status')

    records = LeaveService.get_user_leave_records(user_id)
    if status:
        records = [r for r in records if r.get('leave_status') == status]
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': records
    }), 200


@student_bp.route('/makeup/apply', methods=['POST'])
@token_required
@role_required(['student', 'monitor'])
def apply_makeup():
    """
    学生提交补卡申请
    ---
    请求体: {"target_date": "YYYY-MM-DD", "reason": "xxx"}
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    user_id = request.current_user['user_id']
    data = request.get_json()
    target_date = data.get('target_date', '').strip()
    reason = data.get('reason', '').strip()

    if not target_date or not reason:
        return jsonify({
            'code': 4001,
            'message': '补卡日期和原因不能为空'
        }), 400

    result = MakeupService.apply_makeup(user_id, target_date, reason)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@student_bp.route('/makeup/records', methods=['GET'])
@token_required
@role_required(['student', 'monitor'])
def get_makeup_records():
    """
    获取学生补卡记录
    ---
    返回: {"code": 200, "message": "success", "data": [...]}
    """
    user_id = request.current_user['user_id']
    records = MakeupService.get_user_makeup_records(user_id)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': records
    }), 200


@student_bp.route('/notifications', methods=['GET'])
@token_required
@role_required(['student', 'monitor'])
def get_notifications():
    """
    获取学生通知列表
    ---
    查询参数: unread_only (true/false), limit, offset
    返回: {"code": 200, "message": "success", "data": [...]}
    """
    user_id = request.current_user['user_id']
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    notifications = NotificationService.get_user_notifications(
        user_id,
        is_read=not unread_only if unread_only else None,
        limit=limit,
        offset=offset
    )
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': notifications
    }), 200