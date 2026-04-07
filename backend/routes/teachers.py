from flask import Blueprint, request, jsonify
from datetime import datetime
from dao import user_dao, leave_dao
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

        student = user_dao.get_user_by_id(student_id)

        if not student:
            return jsonify({
                'success': False,
                'message': '未找到该学生'
            }), 404

        if student['class'] != teacher['class']:
            return jsonify({
                'success': False,
                'message': '该学生不在您的班级中'
            }), 403

        if student['role'] != 'student':
            return jsonify({
                'success': False,
                'message': '只有学生才能被任命为班委'
            }), 400

        user_dao.update_user_role(student_id, 'monitor')

        return jsonify({
            'success': True,
            'message': '任命班委成功',
            'data': {
                'student_name': student['username'],
                'student_id': student['user_id'],
                'class': student['class'],
                'appointed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 200

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
        monitors = user_dao.get_monitors_by_class(teacher['class'])

        return jsonify({
            'success': True,
            'message': '查询成功',
            'data': [{'username': m['username'], 'user_id': m['user_id']} for m in monitors]
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
        students = user_dao.get_users_by_class(teacher['class'])

        return jsonify({
            'success': True,
            'message': '查询成功',
            'data': [{'username': s['username'], 'user_id': s['user_id'], 'role': s['role']} for s in students]
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
        classes = user_dao.get_all_classes()

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

        student = user_dao.get_user_by_id(student_id)

        if not student:
            return jsonify({
                'success': False,
                'message': '未找到该学生'
            }), 404

        if student['class'] != teacher['class']:
            return jsonify({
                'success': False,
                'message': '该学生不在您的班级中'
            }), 403

        if student['role'] != 'monitor':
            return jsonify({
                'success': False,
                'message': '该学生不是班委'
            }), 400

        user_dao.update_user_role(student_id, 'student')

        return jsonify({
            'success': True,
            'message': '移除班委成功',
            'data': {
                'student_name': student['username'],
                'student_id': student['user_id'],
                'class': student['class'],
                'removed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 200

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
        applications = leave_dao.get_pending_leave_applications_by_class(teacher['class'])

        return jsonify({
            'success': True,
            'message': '查询成功',
            'data': [{
                'id': app['id'],
                'username': app['username'],
                'user_id': app['user_id'],
                'leave_start_date': app['leave_start_date'],
                'leave_end_date': app['leave_end_date'],
                'leave_status': app['leave_status']
            } for app in applications]
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

        if status not in ['approved', 'rejected']:
            return jsonify({
                'success': False,
                'message': '审批状态只能是approved或rejected'
            }), 400

        leave_application = leave_dao.get_leave_record_by_id_and_class(leave_id, teacher['class'])

        if not leave_application:
            return jsonify({
                'success': False,
                'message': '未找到该请假申请或该申请不属于您的班级'
            }), 404

        if leave_application['leave_status'] != 'pending':
            return jsonify({
                'success': False,
                'message': f'该请假申请已处于{leave_application["leave_status"]}状态，无法重复审批'
            }), 400

        leave_dao.update_leave_status(leave_id, status)

        return jsonify({
            'success': True,
            'message': '请假审批成功',
            'data': {
                'leave_id': leave_id,
                'status': status
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'请假审批失败: {str(e)}'
        }), 500
