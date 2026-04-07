from flask import Blueprint, request, jsonify
from services import TeacherService, LeaveService
from utils.auth import token_required, role_required

teacher_function = Blueprint('teachers', __name__, url_prefix='/api/teachers')


@teacher_function.route('/monitors', methods=['POST'])
@token_required
@role_required('teacher')
def appoint_monitor():
    teacher = request.user_info
    data = request.get_json()
    student_id = data.get('student_id', '').strip()

    if not student_id:
        return jsonify({
            'success': False,
            'message': '学生学号不能为空',
            'code': 4000
        }), 400

    return jsonify(TeacherService.appoint_monitor(student_id, teacher['class'])), 200


@teacher_function.route('/monitors', methods=['GET'])
@token_required
@role_required('teacher')
def get_class_monitors():
    teacher = request.user_info
    monitors = TeacherService.get_monitors(teacher['class'])
    return jsonify({
        'success': True,
        'message': '查询成功',
        'data': monitors
    }), 200


@teacher_function.route('/students', methods=['GET'])
@token_required
@role_required('teacher')
def get_class_students():
    teacher = request.user_info
    students = TeacherService.get_students(teacher['class'])
    return jsonify({
        'success': True,
        'message': '查询成功',
        'data': students
    }), 200


@teacher_function.route('/classes', methods=['GET'])
@token_required
@role_required('teacher')
def get_class_list():
    classes = TeacherService.get_class_list()
    return jsonify({
        'success': True,
        'message': '查询成功',
        'data': classes
    }), 200


@teacher_function.route('/monitors/<student_id>', methods=['DELETE'])
@token_required
@role_required('teacher')
def remove_monitor(student_id):
    teacher = request.user_info
    return jsonify(TeacherService.remove_monitor(student_id, teacher['class'])), 200


@teacher_function.route('/leave-applications', methods=['GET'])
@token_required
@role_required('teacher')
def get_leave_applications():
    teacher = request.user_info
    applications = LeaveService.get_pending_applications(teacher['class'])
    return jsonify({
        'success': True,
        'message': '查询成功',
        'data': applications
    }), 200


@teacher_function.route('/leave-applications/<int:leave_id>/approve', methods=['POST'])
@token_required
@role_required('teacher')
def approve_leave(leave_id):
    teacher = request.user_info
    data = request.get_json()
    status = data.get('status', '')

    if not status:
        return jsonify({
            'success': False,
            'message': '审批状态不能为空',
            'code': 4000
        }), 400

    return jsonify(LeaveService.approve_leave(leave_id, teacher['class'], status)), 200
