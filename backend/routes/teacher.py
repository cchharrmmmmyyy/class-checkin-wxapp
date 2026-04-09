"""
教师路由模块
提供教师班级管理、请假审批、补卡审批、班委管理等功能的接口
"""
from flask import Blueprint, jsonify, request
from services import TeacherService, LeaveService, MakeupService
from utils.auth import token_required, role_required

teacher_bp = Blueprint('teacher', __name__, url_prefix='/api/teacher')


@teacher_bp.route('/classes', methods=['GET'])
@token_required
@role_required(['teacher'])
def get_classes():
    """
    获取教师所教班级列表
    ---
    返回: {"code": 200, "message": "success", "data": [...]}
    """
    classes = TeacherService.get_class_list()
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': classes
    }), 200


@teacher_bp.route('/class/students', methods=['GET'])
@token_required
@role_required(['teacher'])
def get_class_students():
    """
    获取班级学生列表
    ---
    查询参数: class_name
    返回: {"code": 200, "message": "success", "data": [...]}
    """
    teacher = request.current_user
    class_name = request.args.get('class_name', teacher.get('class', '')).strip()

    if not class_name:
        return jsonify({
            'code': 4001,
            'message': '班级名称不能为空'
        }), 400

    students = TeacherService.get_students(class_name)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': students
    }), 200


@teacher_bp.route('/class/punch-summary', methods=['GET'])
@token_required
@role_required(['teacher'])
def get_class_punch_summary():
    """
    获取班级打卡汇总
    ---
    查询参数: class_name, date
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    from services import StatisticsService
    from datetime import date

    teacher = request.current_user
    class_name = request.args.get('class_name', teacher.get('class', '')).strip()
    date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))

    if not class_name:
        return jsonify({
            'code': 4001,
            'message': '班级名称不能为空'
        }), 400

    summary = StatisticsService.get_daily_statistics(class_name, date_str)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': summary
    }), 200


@teacher_bp.route('/leave/pending', methods=['GET'])
@token_required
@role_required(['teacher'])
def get_pending_leaves():
    """
    获取待审批的请假列表
    ---
    查询参数: class_name
    返回: {"code": 200, "message": "success", "data": [...]}
    """
    teacher = request.current_user
    class_name = request.args.get('class_name', teacher.get('class', '')).strip()

    if not class_name:
        return jsonify({
            'code': 4001,
            'message': '班级名称不能为空'
        }), 400

    applications = LeaveService.get_pending_applications(class_name)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': applications
    }), 200


@teacher_bp.route('/leave/approve', methods=['POST'])
@token_required
@role_required(['teacher'])
def approve_leave():
    """
    审批请假申请
    ---
    请求体: {"leave_id": 1, "status": "approved/rejected"}
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    teacher = request.current_user
    data = request.get_json()
    leave_id = data.get('leave_id')
    status = data.get('status', '').strip()

    if not leave_id:
        return jsonify({
            'code': 4002,
            'message': '请假记录ID不能为空'
        }), 400

    if not status:
        return jsonify({
            'code': 4003,
            'message': '审批状态不能为空'
        }), 400

    class_name = teacher.get('class', '')
    result = LeaveService.approve_leave(leave_id, class_name, status)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@teacher_bp.route('/makeup/pending', methods=['GET'])
@token_required
@role_required(['teacher'])
def get_pending_makeups():
    """
    获取待审批的补卡列表
    ---
    查询参数: class_name
    返回: {"code": 200, "message": "success", "data": [...]}
    """
    teacher = request.current_user
    class_name = request.args.get('class_name', teacher.get('class', '')).strip()

    if not class_name:
        return jsonify({
            'code': 4001,
            'message': '班级名称不能为空'
        }), 400

    applications = MakeupService.get_pending_makeup_applications(class_name)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': applications
    }), 200


@teacher_bp.route('/makeup/approve', methods=['POST'])
@token_required
@role_required(['teacher'])
def approve_makeup():
    """
    审批补卡申请
    ---
    请求体: {"makeup_id": 1, "status": "approved/rejected", "punch_time": "08:00:00"}
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    teacher = request.current_user
    data = request.get_json()
    makeup_id = data.get('makeup_id')
    status = data.get('status', '').strip()
    punch_time = data.get('punch_time', '12:00:00')

    if not makeup_id:
        return jsonify({
            'code': 4004,
            'message': '补卡记录ID不能为空'
        }), 400

    if not status:
        return jsonify({
            'code': 4005,
            'message': '审批状态不能为空'
        }), 400

    class_name = teacher.get('class', '')
    result = MakeupService.approve_makeup(makeup_id, class_name, status)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@teacher_bp.route('/monitor/appoint', methods=['POST'])
@token_required
@role_required(['teacher'])
def appoint_monitor():
    """
    任命班委
    ---
    请求体: {"student_id": "xxx"}
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    teacher = request.current_user
    data = request.get_json()
    student_id = data.get('student_id', '').strip()

    if not student_id:
        return jsonify({
            'code': 4006,
            'message': '学生学号不能为空'
        }), 400

    teacher_class = teacher.get('class', '')
    result = TeacherService.appoint_monitor(student_id, teacher_class)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@teacher_bp.route('/monitor/remove', methods=['DELETE'])
@token_required
@role_required(['teacher'])
def remove_monitor():
    """
    撤销班委
    ---
    查询参数: student_id
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    teacher = request.current_user
    student_id = request.args.get('student_id', '').strip()

    if not student_id:
        return jsonify({
            'code': 4007,
            'message': '学生学号不能为空'
        }), 400

    teacher_class = teacher.get('class', '')
    result = TeacherService.remove_monitor(student_id, teacher_class)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@teacher_bp.route('/monitors', methods=['GET'])
@token_required
@role_required(['teacher'])
def get_monitors():
    """
    获取班级班委列表
    ---
    查询参数: class_name
    返回: {"code": 200, "message": "success", "data": [...]}
    """
    teacher = request.current_user
    class_name = request.args.get('class_name', teacher.get('class', '')).strip()

    if not class_name:
        return jsonify({
            'code': 4001,
            'message': '班级名称不能为空'
        }), 400

    monitors = TeacherService.get_monitors(class_name)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': monitors
    }), 200