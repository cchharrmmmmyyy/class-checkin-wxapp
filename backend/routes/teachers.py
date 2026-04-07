from flask import Blueprint, request, jsonify
from services import TeacherService, LeaveService
from utils.auth import token_required, role_required

teacher_function = Blueprint('teachers', __name__, url_prefix='/api/teachers')


@teacher_function.route('/monitors', methods=['POST'])
@token_required
@role_required('teacher')
def appoint_monitor():
    try:
        teacher = request.user_info
        data = request.get_json()
        student_id = data.get('student_id', '').strip()

        if not student_id:
            return jsonify({
                'success': False,
                'message': '学生学号不能为空'
            }), 400

        result = TeacherService.appoint_monitor(student_id, teacher['class'])

        if not result.get('success'):
            status = 404 if '未找到' in result.get('message', '') else (403 if '不在' in result.get('message', '') else 400)
            return jsonify(result), status

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'任命班委失败: {str(e)}'
        }), 500


@teacher_function.route('/monitors', methods=['GET'])
@token_required
@role_required('teacher')
def get_class_monitors():
    try:
        teacher = request.user_info
        monitors = TeacherService.get_monitors(teacher['class'])
        return jsonify({
            'success': True,
            'message': '查询成功',
            'data': monitors
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询班委信息失败: {str(e)}'
        }), 500


@teacher_function.route('/students', methods=['GET'])
@token_required
@role_required('teacher')
def get_class_students():
    try:
        teacher = request.user_info
        students = TeacherService.get_students(teacher['class'])
        return jsonify({
            'success': True,
            'message': '查询成功',
            'data': students
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询学生列表失败: {str(e)}'
        }), 500


@teacher_function.route('/classes', methods=['GET'])
@token_required
@role_required('teacher')
def get_class_list():
    try:
        classes = TeacherService.get_class_list()
        return jsonify({
            'success': True,
            'message': '查询成功',
            'data': classes
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取班级列表失败: {str(e)}'
        }), 500


@teacher_function.route('/monitors/<student_id>', methods=['DELETE'])
@token_required
@role_required('teacher')
def remove_monitor(student_id):
    try:
        teacher = request.user_info
        result = TeacherService.remove_monitor(student_id, teacher['class'])

        if not result.get('success'):
            status = 404 if '未找到' in result.get('message', '') else (403 if '不在' in result.get('message', '') else 400)
            return jsonify(result), status

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'移除班委失败: {str(e)}'
        }), 500


@teacher_function.route('/leave-applications', methods=['GET'])
@token_required
@role_required('teacher')
def get_leave_applications():
    try:
        teacher = request.user_info
        applications = LeaveService.get_pending_applications(teacher['class'])
        return jsonify({
            'success': True,
            'message': '查询成功',
            'data': applications
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500


@teacher_function.route('/leave-applications/<int:leave_id>/approve', methods=['POST'])
@token_required
@role_required('teacher')
def approve_leave(leave_id):
    try:
        teacher = request.user_info
        data = request.get_json()
        status = data.get('status', '')

        if not status:
            return jsonify({
                'success': False,
                'message': '审批状态不能为空'
            }), 400

        result = LeaveService.approve_leave(leave_id, teacher['class'], status)

        if not result.get('success'):
            status = 404 if '未找到' in result.get('message', '') else 400
            return jsonify(result), status

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'请假审批失败: {str(e)}'
        }), 500
