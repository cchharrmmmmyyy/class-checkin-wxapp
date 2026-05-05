"""
学生路由模块
提供学生打卡、请假、补卡等功能的接口（通知相关接口已统一至 common 模块）
"""
from flask import Blueprint, request
from services import PunchService, LeaveService, MakeupService, StatisticsService
from utils.jwt import token_required, role_required
from utils.api_response import success
from utils.exceptions import ServiceException
from utils.error_codes import JSON_INVALID, LEAVE_CLASS_NOT_FOUND

student_bp = Blueprint('student', __name__, url_prefix='/api/student')


def _get_class_name():
    return request.current_user.get('class', '') or None


# 打卡
@student_bp.route('/punch', methods=['POST'])
@token_required
@role_required(['student', 'monitor'])
def punch():
    user_id = request.current_user['user_id']
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    result = PunchService.punch(user_id, data.get('latitude'), data.get('longitude'))
    return success(result)


# 获取打卡记录
@student_bp.route('/punch-records', methods=['GET'])
@token_required
@role_required(['student', 'monitor'])
def get_punch_records():
    user_id = request.current_user['user_id']
    result = PunchService.get_user_punch_records(
        user_id,
        start_date=request.args.get('start_date'),
        end_date=request.args.get('end_date'),
        page=request.args.get('page', 1, type=int),
        size=request.args.get('size', 50, type=int)
    )
    return success(result)


# 申请请假
@student_bp.route('/leave/apply', methods=['POST'])
@token_required
@role_required(['student', 'monitor'])
def apply_leave():
    user_id = request.current_user['user_id']
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    result = LeaveService.apply_leave(
        user_id,
        (data.get('start_date') or '').strip(),
        (data.get('end_date') or '').strip(),
        (data.get('leave_type') or 'personal').strip(),
        (data.get('reason') or '').strip()
    )
    return success(result)


# 获取请假记录
@student_bp.route('/leave/records', methods=['GET'])
@token_required
@role_required(['student', 'monitor'])
def get_leave_records():
    user_id = request.current_user['user_id']
    result = LeaveService.get_user_leave_records(
        user_id,
        status=request.args.get('status'),
        page=request.args.get('page', 1, type=int),
        size=request.args.get('size', 50, type=int)
    )
    return success(result)


# 申请补卡
@student_bp.route('/makeup/apply', methods=['POST'])
@token_required
@role_required(['student', 'monitor'])
def apply_makeup():
    user_id = request.current_user['user_id']
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    result = MakeupService.apply_makeup(
        user_id,
        (data.get('target_date') or '').strip(),
        (data.get('reason') or '').strip()
    )
    return success(result)


# 获取补卡记录
@student_bp.route('/makeup/records', methods=['GET'])
@token_required
@role_required(['student', 'monitor'])
def get_makeup_records():
    user_id = request.current_user['user_id']
    result = MakeupService.get_user_makeup_records(
        user_id,
        page=request.args.get('page', 1, type=int),
        size=request.args.get('size', 50, type=int)
    )
    return success(result)


# 获取班级打卡情况（班委）
@student_bp.route('/monitor/class-punch-status', methods=['GET'])
@token_required
@role_required(['monitor'])
def get_monitor_class_punch_status():
    class_name = _get_class_name()
    if not class_name:
        raise ServiceException('班级信息不存在', code=LEAVE_CLASS_NOT_FOUND)

    summary = StatisticsService.get_daily_statistics(class_name, request.args.get('date'))
    return success(summary)


# 获取班级请假情况（班委）
@student_bp.route('/monitor/class-leaves', methods=['GET'])
@token_required
@role_required(['monitor'])
def get_monitor_class_leaves():
    class_name = _get_class_name()
    if not class_name:
        raise ServiceException('班级信息不存在', code=LEAVE_CLASS_NOT_FOUND)

    result = LeaveService.get_pending_applications(
        class_name,
        page=request.args.get('page', 1, type=int),
        size=request.args.get('size', 50, type=int)
    )
    return success(result)


# 获取班级补卡情况（班委）
@student_bp.route('/monitor/class-makeups', methods=['GET'])
@token_required
@role_required(['monitor'])
def get_monitor_class_makeups():
    class_name = _get_class_name()
    if not class_name:
        raise ServiceException('班级信息不存在', code=LEAVE_CLASS_NOT_FOUND)

    result = MakeupService.get_pending_makeup_applications(
        class_name,
        page=request.args.get('page', 1, type=int),
        size=request.args.get('size', 50, type=int)
    )
    return success(result)
