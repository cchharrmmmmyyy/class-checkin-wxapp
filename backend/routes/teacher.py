"""
教师路由模块
提供教师班级管理、请假审批、补卡审批、班委管理等功能的接口
"""
from flask import Blueprint, request
from services import TeacherService, LeaveService, MakeupService
from utils.jwt import token_required, role_required
from utils.api_response import success, error

teacher_bp = Blueprint('teacher', __name__, url_prefix='/api/teacher')


def _get_teacher_class(teacher):
    """获取教师的班级，处理None情况"""
    class_name = teacher.get('class', '') or ''
    return class_name.strip()


@teacher_bp.route('/classes', methods=['GET'])
@token_required
@role_required(['teacher'])
def get_classes():
    """获取教师所教班级列表"""
    classes = TeacherService.get_class_list()
    return success(classes)


@teacher_bp.route('/class/students', methods=['GET'])
@token_required
@role_required(['teacher'])
def get_class_students():
    """获取班级学生列表"""
    teacher = request.current_user
    class_name = request.args.get('class_name', _get_teacher_class(teacher))
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 50, type=int)

    if not class_name:
        return error(message='班级名称不能为空', code=4001, http_status=400)

    result = TeacherService.get_students(class_name, page=page, size=size)
    return success(result)


@teacher_bp.route('/class/punch-summary', methods=['GET'])
@token_required
@role_required(['teacher'])
def get_class_punch_summary():
    """获取班级打卡汇总"""
    from services import StatisticsService
    from datetime import date

    teacher = request.current_user
    class_name = request.args.get('class_name', _get_teacher_class(teacher))
    date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))

    if not class_name:
        return error(message='班级名称不能为空', code=4001, http_status=400)

    summary = StatisticsService.get_daily_statistics(class_name, date_str)
    return success(summary)


@teacher_bp.route('/leave/pending', methods=['GET'])
@token_required
@role_required(['teacher'])
def get_pending_leaves():
    """获取待审批的请假列表"""
    teacher = request.current_user
    class_name = request.args.get('class_name', _get_teacher_class(teacher))
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 50, type=int)

    if not class_name:
        return error(message='班级名称不能为空', code=4001, http_status=400)

    result = LeaveService.get_pending_applications(class_name, page=page, size=size)
    return success(result)


@teacher_bp.route('/leave/approve', methods=['POST'])
@token_required
@role_required(['teacher'])
def approve_leave():
    """审批请假申请"""
    teacher = request.current_user
    data = request.get_json()
    leave_id = data.get('leave_id')
    status = data.get('status', '').strip()

    if not leave_id:
        return error(message='请假记录ID不能为空', code=4002, http_status=400)

    if not status:
        return error(message='审批状态不能为空', code=4003, http_status=400)

    class_name = _get_teacher_class(teacher)
    result = LeaveService.approve_leave(leave_id, class_name, status)
    return success(result)


@teacher_bp.route('/makeup/pending', methods=['GET'])
@token_required
@role_required(['teacher'])
def get_pending_makeups():
    """获取待审批的补卡列表"""
    teacher = request.current_user
    class_name = request.args.get('class_name', _get_teacher_class(teacher))
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 50, type=int)

    if not class_name:
        return error(message='班级名称不能为空', code=4001, http_status=400)

    result = MakeupService.get_pending_makeup_applications(class_name, page=page, size=size)
    return success(result)


@teacher_bp.route('/makeup/approve', methods=['POST'])
@token_required
@role_required(['teacher'])
def approve_makeup():
    """审批补卡申请"""
    teacher = request.current_user
    data = request.get_json()
    makeup_id = data.get('makeup_id')
    status = data.get('status', '').strip()
    punch_time = data.get('punch_time', '12:00:00')

    if not makeup_id:
        return error(message='补卡记录ID不能为空', code=4004, http_status=400)

    if not status:
        return error(message='审批状态不能为空', code=4005, http_status=400)

    class_name = _get_teacher_class(teacher)
    result = MakeupService.approve_makeup(makeup_id, class_name, status, punch_time)
    return success(result)


@teacher_bp.route('/monitor/appoint', methods=['POST'])
@token_required
@role_required(['teacher'])
def appoint_monitor():
    """任命班委"""
    teacher = request.current_user
    data = request.get_json()
    student_id = data.get('student_id', '').strip()

    if not student_id:
        return error(message='学生学号不能为空', code=4006, http_status=400)

    teacher_class = _get_teacher_class(teacher)
    result = TeacherService.appoint_monitor(student_id, teacher_class)
    return success(result)


@teacher_bp.route('/monitor/remove', methods=['DELETE'])
@token_required
@role_required(['teacher'])
def remove_monitor():
    """撤销班委"""
    teacher = request.current_user
    student_id = request.args.get('student_id', '').strip()

    if not student_id:
        return error(message='学生学号不能为空', code=4007, http_status=400)

    teacher_class = _get_teacher_class(teacher)
    result = TeacherService.remove_monitor(student_id, teacher_class)
    return success(result)


@teacher_bp.route('/monitors', methods=['GET'])
@token_required
@role_required(['teacher'])
def get_monitors():
    """获取班级班委列表"""
    teacher = request.current_user
    class_name = request.args.get('class_name', _get_teacher_class(teacher))
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 50, type=int)

    if not class_name:
        return error(message='班级名称不能为空', code=4001, http_status=400)

    result = TeacherService.get_monitors(class_name, page=page, size=size)
    return success(result)
