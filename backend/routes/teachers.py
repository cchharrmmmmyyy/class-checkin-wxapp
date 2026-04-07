from flask import Blueprint, request, jsonify
from datetime import datetime
from database import execute_query, execute_query_one, execute_update
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

        student = execute_query_one(
            "SELECT username, user_id, role, class FROM users WHERE user_id = ?",
            (student_id,)
        )

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

        execute_update(
            "UPDATE users SET role = 'monitor' WHERE user_id = ?",
            (student_id,)
        )

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
        monitors = execute_query(
            "SELECT username, user_id FROM users WHERE class = ? AND role = 'monitor'",
            (teacher['class'],)
        )

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
        students = execute_query(
            "SELECT username, user_id, role FROM users WHERE class = ? AND role IN ('student', 'monitor')",
            (teacher['class'],)
        )

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
        classes = execute_query(
            "SELECT DISTINCT class FROM users WHERE role = 'student' AND class != '' ORDER BY class"
        )

        return jsonify({
            'success': True,
            'message': '查询成功',
            'data': [c['class'] for c in classes]
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

        student = execute_query_one(
            "SELECT username, user_id, role, class FROM users WHERE user_id = ?",
            (student_id,)
        )

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

        execute_update(
            "UPDATE users SET role = 'student' WHERE user_id = ?",
            (student_id,)
        )

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
        applications = execute_query(
            "SELECT pr.*, u.username FROM punch_records pr JOIN users u ON pr.user_id = u.user_id WHERE pr.leave_status = 'pending' AND pr.leave_start_date IS NOT NULL AND pr.leave_end_date IS NOT NULL AND u.class = ? ORDER BY pr.id DESC",
            (teacher['class'],)
        )

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

        leave_application = execute_query_one(
            "SELECT * FROM punch_records WHERE id = ? AND user_id IN (SELECT user_id FROM users WHERE class = ?)",
            (leave_id, teacher['class'])
        )

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

        execute_update(
            "UPDATE punch_records SET leave_status = ? WHERE id = ?",
            (status, leave_id)
        )

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