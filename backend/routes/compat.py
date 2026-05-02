"""
旧同义接口兼容层：
- 保留短期可用，响应头声明弃用与下线时间；
- 返回结构统一为 {code, message, data, trace_id?}。
"""
from flask import Blueprint, request
from services import PunchService, LeaveService, TeacherService
from utils.auth import token_required, role_required
from utils.api_response import success, mark_legacy_route

compat_bp = Blueprint('compat', __name__, url_prefix='/api')


def _legacy(response_tuple):
    response, status = response_tuple
    return mark_legacy_route(response), status


@compat_bp.route('/students/punch', methods=['POST'])
@token_required
@role_required(['student', 'monitor'])
def legacy_student_punch():
    user_id = request.current_user['user_id']
    data = request.get_json() or {}
    result = PunchService.punch(user_id, data.get('latitude'), data.get('longitude'))
    return _legacy(success(result))


@compat_bp.route('/students/records', methods=['GET'])
@token_required
def legacy_student_records():
    user_id = request.current_user['user_id']
    records = PunchService.get_user_punch_records(user_id)
    return _legacy(success(records))


@compat_bp.route('/students/leave-records', methods=['GET'])
@token_required
def legacy_student_leave_records():
    user_id = request.current_user['user_id']
    records = LeaveService.get_user_leave_records(user_id)
    return _legacy(success(records))


@compat_bp.route('/teachers/classes', methods=['GET'])
@token_required
@role_required(['teacher'])
def legacy_teacher_classes():
    classes = TeacherService.get_class_list()
    return _legacy(success(classes))


@compat_bp.route('/teachers/students', methods=['GET'])
@token_required
@role_required(['teacher'])
def legacy_teacher_students():
    class_name = request.current_user.get('class', '')
    students = TeacherService.get_students(class_name)
    return _legacy(success(students))
