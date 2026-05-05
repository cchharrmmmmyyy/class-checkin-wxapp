"""
教师路由模块
提供教师班级管理、请假审批、补卡审批、班委管理等功能的接口
"""
from flask import Blueprint, request
from services import TeacherService, LeaveService, MakeupService, StatisticsService
from utils.jwt import token_required, role_required
from utils.api_response import success
from utils.exceptions import ServiceException
from utils.error_codes import (
    JSON_INVALID, CLASS_NAME_MISSING,
    LEAVE_RECORD_ID_MISSING, LEAVE_STATUS_MISSING,
    MAKEUP_RECORD_ID_MISSING, MAKEUP_STATUS_MISSING,
    USER_STUDENT_ID_MISSING
)
from datetime import date

teacher_bp = Blueprint('teacher', __name__, url_prefix='/api/teacher')


def _get_teacher_class(teacher):
    class_name = teacher.get('class', '') or ''
    return class_name.strip()


# 获取所教班级列表
@teacher_bp.route('/classes', methods=['GET'])
@token_required
@role_required(['teacher'])
def get_classes():
    classes = TeacherService.get_class_list()
    return success(classes)


# 获取班级学生列表
@teacher_bp.route('/class/students', methods=['GET'])
@token_required
@role_required(['teacher'])
def get_class_students():
    teacher = request.current_user
    class_name = request.args.get('class_name', _get_teacher_class(teacher))
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 50, type=int)

    if not class_name:
        raise ServiceException('班级名称不能为空', code=CLASS_NAME_MISSING)

    result = TeacherService.get_students(class_name, page=page, size=size)
    return success(result)


# 获取班级打卡汇总
@teacher_bp.route('/class/punch-summary', methods=['GET'])
@token_required
@role_required(['teacher'])
def get_class_punch_summary():
    teacher = request.current_user
    class_name = request.args.get('class_name', _get_teacher_class(teacher))
    date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))

    if not class_name:
        raise ServiceException('班级名称不能为空', code=CLASS_NAME_MISSING)

    summary = StatisticsService.get_daily_statistics(class_name, date_str)
    return success(summary)


# 获取待审批的请假列表
@teacher_bp.route('/leave/pending', methods=['GET'])
@token_required
@role_required(['teacher'])
def get_pending_leaves():
    teacher = request.current_user
    class_name = request.args.get('class_name', _get_teacher_class(teacher))
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 50, type=int)

    if not class_name:
        raise ServiceException('班级名称不能为空', code=CLASS_NAME_MISSING)

    result = LeaveService.get_pending_applications(class_name, page=page, size=size)
    return success(result)


# 审批请假申请
@teacher_bp.route('/leave/approve', methods=['POST'])
@token_required
@role_required(['teacher'])
def approve_leave():
    teacher = request.current_user
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    leave_id = data.get('leave_id')
    status = (data.get('status') or '').strip()

    if not leave_id:
        raise ServiceException('请假记录ID不能为空', code=LEAVE_RECORD_ID_MISSING)

    if not status:
        raise ServiceException('审批状态不能为空', code=LEAVE_STATUS_MISSING)

    class_name = _get_teacher_class(teacher)
    result = LeaveService.approve_leave(leave_id, class_name, status)
    return success(result)


# 获取待审批的补卡列表
@teacher_bp.route('/makeup/pending', methods=['GET'])
@token_required
@role_required(['teacher'])
def get_pending_makeups():
    teacher = request.current_user
    class_name = request.args.get('class_name', _get_teacher_class(teacher))
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 50, type=int)

    if not class_name:
        raise ServiceException('班级名称不能为空', code=CLASS_NAME_MISSING)

    result = MakeupService.get_pending_makeup_applications(class_name, page=page, size=size)
    return success(result)


# 审批补卡申请
@teacher_bp.route('/makeup/approve', methods=['POST'])
@token_required
@role_required(['teacher'])
def approve_makeup():
    teacher = request.current_user
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    makeup_id = data.get('makeup_id')
    status = (data.get('status') or '').strip()
    punch_time = (data.get('punch_time') or '12:00:00').strip()

    if not makeup_id:
        raise ServiceException('补卡记录ID不能为空', code=MAKEUP_RECORD_ID_MISSING)

    if not status:
        raise ServiceException('审批状态不能为空', code=MAKEUP_STATUS_MISSING)

    class_name = _get_teacher_class(teacher)
    result = MakeupService.approve_makeup(makeup_id, class_name, status, punch_time)
    return success(result)


# 任命班委
@teacher_bp.route('/monitor/appoint', methods=['POST'])
@token_required
@role_required(['teacher'])
def appoint_monitor():
    teacher = request.current_user
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    student_id = (data.get('student_id') or '').strip()

    if not student_id:
        raise ServiceException('学生学号不能为空', code=USER_STUDENT_ID_MISSING)

    teacher_class = _get_teacher_class(teacher)
    result = TeacherService.appoint_monitor(student_id, teacher_class)
    return success(result)


# 撤销班委
@teacher_bp.route('/monitor/remove', methods=['DELETE'])
@token_required
@role_required(['teacher'])
def remove_monitor():
    teacher = request.current_user
    student_id = request.args.get('student_id', '').strip()

    if not student_id:
        raise ServiceException('学生学号不能为空', code=USER_STUDENT_ID_MISSING)

    teacher_class = _get_teacher_class(teacher)
    result = TeacherService.remove_monitor(student_id, teacher_class)
    return success(result)


# 获取班级班委列表
@teacher_bp.route('/monitors', methods=['GET'])
@token_required
@role_required(['teacher'])
def get_monitors():
    teacher = request.current_user
    class_name = request.args.get('class_name', _get_teacher_class(teacher))
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 50, type=int)

    if not class_name:
        raise ServiceException('班级名称不能为空', code=CLASS_NAME_MISSING)

    result = TeacherService.get_monitors(class_name, page=page, size=size)
    return success(result)
