"""
管理员路由模块
提供管理员用户管理、考勤管理、配置管理等功能的接口
"""
import csv
import io
from datetime import date
from flask import Blueprint, jsonify, request, send_file
from services import AdminService, ConfigService, StatisticsService
from utils.jwt import token_required, role_required
from utils.api_response import mark_legacy_route

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def _parse_bool_arg(name, default=False):
    raw = request.args.get(name, None)
    if raw is None:
        return default
    return str(raw).lower() in ('1', 'true', 'yes', 'on')


@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """
    管理员登录接口
    ---
    请求体: {"user_id": "xxx", "password": "xxx"}
    返回: {"code": 200, "message": "success", "data": {"token": "...", "user": {...}, "redirect_url": "..."}}
    """
    from services import AuthService
    data = request.get_json()
    user_id = data.get('user_id', '').strip()
    password = data.get('password', '').strip()

    if not user_id or not password:
        return jsonify({'code': 1000, 'message': '账号和密码不能为空'}), 400

    result = AuthService.login(user_id, password)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/users', methods=['GET'])
@token_required
@role_required(['admin'])
def get_users():
    """
    获取用户列表（支持分页、筛选）
    ---
    查询参数: class_name, role, page, size
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    class_name = request.args.get('class_name', '').strip() or None
    role = request.args.get('role', '').strip() or None
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 50, type=int)

    result = AdminService.list_users_paginated(
        class_name=class_name,
        role=role,
        page=page,
        size=size
    )

    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/dashboard/trend', methods=['GET'])
@token_required
@role_required(['admin'])
def dashboard_trend():
    """
    仪表盘趋势图表数据
    ---
    查询参数: days (默认7)
    返回: {"code": 200, "data": {...}}
    """
    days = request.args.get('days', 7, type=int)
    result = StatisticsService.get_attendance_trend(days=days)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/attendance/export', methods=['GET'])
@token_required
@role_required(['admin'])
def export_attendance():
    """
    导出考勤记录为 CSV
    """
    username = request.args.get('username', '').strip() or None
    user_id = request.args.get('user_id', '').strip() or None
    start_date = request.args.get('start_date', '').strip() or None
    end_date = request.args.get('end_date', '').strip() or None
    leave_status = request.args.get('leave_status', '').strip() or None

    # 获取所有匹配的记录（不分页）
    result = AdminService.get_attendance_records(
        username=username,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        leave_status=leave_status,
        page=1,
        size=10000  # 足够大的数字以获取所有记录
    )

    records = result.get('items', [])

    # 生成 CSV
    output = io.StringIO()
    # 写入 BOM 以便 Excel 正确识别 UTF-8
    output.write('\ufeff')
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow(['ID', '学号', '姓名', '打卡日期', '请假开始', '请假结束', '状态'])
    
    # 写入数据
    for r in records:
        status = '-'
        if r['leave_status'] == 'pending':
            status = '待审批'
        elif r['leave_status'] == 'approved':
            status = '已批准'
        elif r['leave_status'] == 'rejected':
            status = '已拒绝'
        elif r['punch_date']:
            status = '已打卡'
            
        writer.writerow([
            r['id'],
            r['user_id'],
            r['username'],
            r['punch_date'] or '-',
            r['leave_start_date'] or '-',
            r['leave_end_date'] or '-',
            status
        ])

    output.seek(0)
    
    filename = f"attendance_export_{date.today().isoformat()}.csv"
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@admin_bp.route('/users', methods=['POST'])
@token_required
@role_required(['admin'])
def create_user():
    """
    创建用户
    ---
    请求体: {"username": "xxx", "user_id": "xxx", "password": "xxx", "role": "xxx", "class": "xxx"}
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    data = request.get_json()
    username = data.get('username', '').strip()
    user_id = data.get('user_id', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', '').strip()
    class_name = data.get('class', '').strip()

    if not username or not user_id or not password or not role:
        return jsonify({
            'code': 5000,
            'message': '用户名、密码、角色和用户ID不能为空'
        }), 400

    result = AdminService.save_user(username, user_id, password, role, class_name)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@admin_bp.route('/users/<user_id>', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_user(user_id):
    """
    更新用户信息
    ---
    请求体: {"username": "xxx", "role": "xxx", "class": "xxx", "password": "xxx"}
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', '').strip()
    class_name = data.get('class', '').strip()

    result = AdminService.save_user(username, user_id, password, role, class_name)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_user(user_id):
    """
    删除用户（软删除）
    ---
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    result = AdminService.delete_user(user_id)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@admin_bp.route('/users/reset-password', methods=['POST'])
@token_required
@role_required(['admin'])
def admin_reset_password():
    """
    重置用户密码（管理员操作）
    ---
    请求体: {"user_id": "xxx"}
    返回: {"code": 200, "message": "success", "data": {"new_password": "xxx"}}
    """
    data = request.get_json()
    user_id = data.get('user_id', '').strip()

    if not user_id:
        return jsonify({
            'code': 5000,
            'message': '用户ID不能为空'
        }), 400

    result = AdminService.reset_password(user_id)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@admin_bp.route('/org/campuses', methods=['GET'])
@token_required
@role_required(['admin'])
def list_campuses():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    name = request.args.get('name', '').strip() or None
    result = AdminService.list_campuses(name=name, page=page, size=size)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/org/campuses', methods=['POST'])
@token_required
@role_required(['admin'])
def create_campus():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    address = data.get('address')
    result = AdminService.save_campus(None, name, address)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/org/campuses/<int:campus_id>', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_campus(campus_id):
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    address = data.get('address')
    result = AdminService.save_campus(campus_id, name, address)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/org/campuses/<int:campus_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_campus(campus_id):
    result = AdminService.delete_campus(campus_id)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/org/departments', methods=['GET'])
@token_required
@role_required(['admin'])
def list_departments():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    campus_id = request.args.get('campus_id', type=int)
    name = request.args.get('name', '').strip() or None
    result = AdminService.list_departments(campus_id=campus_id, name=name, page=page, size=size)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/org/departments', methods=['POST'])
@token_required
@role_required(['admin'])
def create_department():
    data = request.get_json() or {}
    campus_id = data.get('campus_id')
    name = (data.get('name') or '').strip()
    code = data.get('code')
    result = AdminService.save_department(None, campus_id, name, code)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/org/departments/<int:department_id>', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_department(department_id):
    data = request.get_json() or {}
    campus_id = data.get('campus_id')
    name = (data.get('name') or '').strip()
    code = data.get('code')
    result = AdminService.save_department(department_id, campus_id, name, code)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/org/departments/<int:department_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_department(department_id):
    result = AdminService.delete_department(department_id)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/org/majors', methods=['GET'])
@token_required
@role_required(['admin'])
def list_majors():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    department_id = request.args.get('department_id', type=int)
    name = request.args.get('name', '').strip() or None
    result = AdminService.list_majors(department_id=department_id, name=name, page=page, size=size)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/org/majors', methods=['POST'])
@token_required
@role_required(['admin'])
def create_major():
    data = request.get_json() or {}
    department_id = data.get('department_id')
    name = (data.get('name') or '').strip()
    code = data.get('code')
    result = AdminService.save_major(None, department_id, name, code)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/org/majors/<int:major_id>', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_major(major_id):
    data = request.get_json() or {}
    department_id = data.get('department_id')
    name = (data.get('name') or '').strip()
    code = data.get('code')
    result = AdminService.save_major(major_id, department_id, name, code)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/org/majors/<int:major_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_major(major_id):
    result = AdminService.delete_major(major_id)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/org/grades', methods=['GET'])
@token_required
@role_required(['admin'])
def list_grades():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    major_id = request.args.get('major_id', type=int)
    year = request.args.get('year', type=int)
    result = AdminService.list_grades(major_id=major_id, year=year, page=page, size=size)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/org/grades', methods=['POST'])
@token_required
@role_required(['admin'])
def create_grade():
    data = request.get_json() or {}
    major_id = data.get('major_id')
    year = data.get('year')
    name = (data.get('name') or '').strip()
    result = AdminService.save_grade(None, major_id, year, name)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/org/grades/<int:grade_id>', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_grade(grade_id):
    data = request.get_json() or {}
    major_id = data.get('major_id')
    year = data.get('year')
    name = (data.get('name') or '').strip()
    result = AdminService.save_grade(grade_id, major_id, year, name)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/org/grades/<int:grade_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_grade(grade_id):
    result = AdminService.delete_grade(grade_id)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/org/classes', methods=['GET'])
@token_required
@role_required(['admin'])
def list_classes():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    grade_id = request.args.get('grade_id', type=int)
    class_name = request.args.get('class_name', '').strip() or None
    include_deleted = _parse_bool_arg('include_deleted', False)
    result = AdminService.list_classes(
        grade_id=grade_id,
        class_name=class_name,
        page=page,
        size=size,
        include_deleted=include_deleted
    )
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/org/classes', methods=['POST'])
@token_required
@role_required(['admin'])
def create_class():
    data = request.get_json() or {}
    class_name = (data.get('class_name') or '').strip()
    grade_id = data.get('grade_id')
    result = AdminService.save_class(None, class_name, grade_id)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/org/classes/<class_name>', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_class(class_name):
    data = request.get_json() or {}
    new_class_name = (data.get('class_name') or class_name).strip()
    grade_id = data.get('grade_id')
    result = AdminService.save_class(class_name, new_class_name, grade_id)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/org/classes/<class_name>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_class(class_name):
    result = AdminService.delete_class(class_name)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/teaching/assignments', methods=['GET'])
@token_required
@role_required(['admin'])
def list_teaching_assignments():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    class_name = request.args.get('class_name', '').strip() or None
    teacher_id = request.args.get('teacher_id', '').strip() or None
    semester = request.args.get('semester', '').strip() or None
    include_deleted = _parse_bool_arg('include_deleted', False)
    result = AdminService.list_teaching_assignments(
        class_name=class_name,
        teacher_id=teacher_id,
        semester=semester,
        page=page,
        size=size,
        include_deleted=include_deleted
    )
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/teaching/assignments', methods=['POST'])
@token_required
@role_required(['admin'])
def create_teaching_assignment():
    data = request.get_json() or {}
    class_name = (data.get('class_name') or '').strip()
    teacher_id = (data.get('teacher_id') or '').strip()
    semester = (data.get('semester') or '').strip() or None
    result = AdminService.create_teaching_assignment(class_name, teacher_id, semester)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/teaching/assignments/<class_name>/<teacher_id>', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_teaching_assignment(class_name, teacher_id):
    data = request.get_json() or {}
    semester = data.get('semester', '').strip() or None
    result = AdminService.update_teaching_assignment(class_name, teacher_id, semester)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/teaching/assignments/<class_name>/<teacher_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_teaching_assignment(class_name, teacher_id):
    result = AdminService.delete_teaching_assignment(class_name, teacher_id)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/rules/time-slots', methods=['GET'])
@token_required
@role_required(['admin'])
def list_time_slots():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    name = request.args.get('name', '').strip() or None
    enabled = request.args.get('enabled')
    include_deleted = _parse_bool_arg('include_deleted', False)
    result = AdminService.list_time_slots(
        name=name,
        enabled=enabled,
        page=page,
        size=size,
        include_deleted=include_deleted
    )
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/rules/time-slots', methods=['POST'])
@token_required
@role_required(['admin'])
def create_time_slot():
    data = request.get_json() or {}
    result = AdminService.save_time_slot(
        None,
        (data.get('name') or '').strip(),
        data.get('start_time'),
        data.get('end_time'),
        data.get('enabled', 1)
    )
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/rules/time-slots/<int:slot_id>', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_time_slot(slot_id):
    data = request.get_json() or {}
    result = AdminService.save_time_slot(
        slot_id,
        (data.get('name') or '').strip(),
        data.get('start_time'),
        data.get('end_time'),
        data.get('enabled', 1)
    )
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/rules/time-slots/<int:slot_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_time_slot(slot_id):
    result = AdminService.delete_time_slot(slot_id)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/rules/punch-geofences', methods=['GET'])
@token_required
@role_required(['admin'])
def list_punch_geofences():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    name = request.args.get('name', '').strip() or None
    enabled = request.args.get('enabled')
    fence_type = request.args.get('fence_type', '').strip() or None
    include_deleted = _parse_bool_arg('include_deleted', False)
    result = AdminService.list_geofences(
        name=name,
        enabled=enabled,
        fence_type=fence_type,
        page=page,
        size=size,
        include_deleted=include_deleted
    )
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/rules/punch-geofences', methods=['POST'])
@token_required
@role_required(['admin'])
def create_punch_geofence():
    data = request.get_json() or {}
    result = AdminService.save_geofence(
        geofence_id=None,
        name=(data.get('name') or '').strip(),
        fence_type=(data.get('fence_type') or '').strip(),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        radius=data.get('radius'),
        polygon_coords=data.get('polygon_coords'),
        enabled=data.get('enabled', 1)
    )
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/rules/punch-geofences/<int:geofence_id>', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_punch_geofence(geofence_id):
    data = request.get_json() or {}
    result = AdminService.save_geofence(
        geofence_id=geofence_id,
        name=(data.get('name') or '').strip(),
        fence_type=(data.get('fence_type') or '').strip(),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        radius=data.get('radius'),
        polygon_coords=data.get('polygon_coords'),
        enabled=data.get('enabled', 1)
    )
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/rules/punch-geofences/<int:geofence_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_punch_geofence(geofence_id):
    result = AdminService.delete_geofence(geofence_id)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/rules/punch-rules', methods=['GET'])
@token_required
@role_required(['admin'])
def list_punch_rules():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    enabled = request.args.get('enabled')
    time_slot_id = request.args.get('time_slot_id', type=int)
    geofence_id = request.args.get('geofence_id', type=int)
    include_deleted = _parse_bool_arg('include_deleted', False)
    result = AdminService.list_punch_rules(
        enabled=enabled,
        time_slot_id=time_slot_id,
        geofence_id=geofence_id,
        page=page,
        size=size,
        include_deleted=include_deleted
    )
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/rules/punch-rules', methods=['POST'])
@token_required
@role_required(['admin'])
def create_punch_rule():
    data = request.get_json() or {}
    result = AdminService.save_punch_rule(
        rule_id=None,
        time_slot_id=data.get('time_slot_id'),
        geofence_id=data.get('geofence_id'),
        priority=data.get('priority', 100),
        time_enabled=data.get('time_enabled', 1),
        location_enabled=data.get('location_enabled', 1),
        enabled=data.get('enabled', 1)
    )
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/rules/punch-rules/<int:rule_id>', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_punch_rule(rule_id):
    data = request.get_json() or {}
    result = AdminService.save_punch_rule(
        rule_id=rule_id,
        time_slot_id=data.get('time_slot_id'),
        geofence_id=data.get('geofence_id'),
        priority=data.get('priority', 100),
        time_enabled=data.get('time_enabled', 1),
        location_enabled=data.get('location_enabled', 1),
        enabled=data.get('enabled', 1)
    )
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/rules/punch-rules/<int:rule_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_punch_rule(rule_id):
    result = AdminService.delete_punch_rule(rule_id)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/attendance-records', methods=['GET'])
@token_required
@role_required(['admin'])
def get_attendance_records():
    """
    获取考勤记录
    ---
    查询参数: username, user_id, start_date, end_date, leave_status, page, size
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    username = request.args.get('username', '').strip() or None
    user_id = request.args.get('user_id', '').strip() or None
    start_date = request.args.get('start_date', '').strip() or None
    end_date = request.args.get('end_date', '').strip() or None
    leave_status = request.args.get('leave_status', '').strip() or None
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)

    result = AdminService.get_attendance_records(
        username=username,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        leave_status=leave_status,
        page=page,
        size=size
    )
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@admin_bp.route('/attendance-records', methods=['POST'])
@token_required
@role_required(['admin'])
def create_attendance_record():
    """
    创建或更新考勤记录
    ---
    请求体: {"id": null, "user_id": "xxx", "punch_date": "xxx", ...}
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    data = request.get_json() or {}
    record_id_raw = data.get('id')
    record_id = int(record_id_raw) if record_id_raw not in (None, '') else None
    user_id = (data.get('user_id') or '').strip()
    punch_date = data.get('punch_date', '').strip() or None
    leave_start_date = data.get('leave_start_date', '') or None
    leave_end_date = data.get('leave_end_date', '') or None
    leave_status = data.get('leave_status', 'pending').strip()

    if not user_id:
        return jsonify({
            'code': 5000,
            'message': '用户ID不能为空'
        }), 400

    result = AdminService.save_attendance_record(
        record_id, user_id, punch_date,
        leave_start_date, leave_end_date, leave_status
    )
    response = jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            **result,
            'migration_hint': '该接口为兼容层，请迁移至 /api/admin/attendance/punch-records 或 /api/admin/attendance/leave-records'
        }
    })
    response.status_code = 200
    return mark_legacy_route(response)


@admin_bp.route('/attendance/punch-records', methods=['POST'])
@token_required
@role_required(['admin'])
def create_punch_record():
    data = request.get_json() or {}
    user_id = (data.get('user_id') or '').strip()
    punch_date = (data.get('punch_date') or '').strip()
    if not user_id:
        return jsonify({'code': 5000, 'message': '用户ID不能为空'}), 400
    result = AdminService.save_punch_record(
        record_id=None,
        user_id=user_id,
        punch_date=punch_date,
        punch_time=data.get('punch_time', '12:00:00'),
        latitude=data.get('latitude', 0.0),
        longitude=data.get('longitude', 0.0)
    )
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/attendance/punch-records/<int:record_id>', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_punch_record(record_id):
    data = request.get_json() or {}
    user_id = (data.get('user_id') or '').strip()
    punch_date = (data.get('punch_date') or '').strip()
    if not user_id:
        return jsonify({'code': 5000, 'message': '用户ID不能为空'}), 400
    result = AdminService.save_punch_record(
        record_id=record_id,
        user_id=user_id,
        punch_date=punch_date,
        punch_time=data.get('punch_time', '12:00:00'),
        latitude=data.get('latitude', 0.0),
        longitude=data.get('longitude', 0.0)
    )
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/attendance/punch-records/<int:record_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_punch_record(record_id):
    result = AdminService.delete_punch_record(record_id)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/attendance/leave-records', methods=['POST'])
@token_required
@role_required(['admin'])
def create_leave_record():
    data = request.get_json() or {}
    user_id = (data.get('user_id') or '').strip()
    if not user_id:
        return jsonify({'code': 5000, 'message': '用户ID不能为空'}), 400
    result = AdminService.save_leave_record(
        record_id=None,
        user_id=user_id,
        leave_start_date=data.get('leave_start_date'),
        leave_end_date=data.get('leave_end_date'),
        leave_status=(data.get('leave_status') or 'pending').strip(),
        leave_type=(data.get('leave_type') or 'personal').strip(),
        leave_reason=data.get('leave_reason')
    )
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/attendance/leave-records/<int:record_id>', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_leave_record(record_id):
    data = request.get_json() or {}
    leave_status = (data.get('leave_status') or 'pending').strip()
    result = AdminService.save_leave_record(
        record_id=record_id,
        user_id='',
        leave_status=leave_status
    )
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/attendance/leave-records/<int:record_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_leave_record(record_id):
    result = AdminService.delete_leave_record(record_id)
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200


@admin_bp.route('/attendance-records/<int:record_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_attendance_record(record_id):
    """
    删除考勤记录
    ---
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    result = AdminService.delete_attendance_record(record_id)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@admin_bp.route('/punch-location', methods=['GET'])
@token_required
@role_required(['admin'])
def get_punch_location():
    """
    获取打卡位置配置
    ---
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    result = AdminService.get_punch_location()
    response = jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'location': result.get('data'),
            'compatibility': result.get('compatibility')
        }
    })
    response.status_code = 200
    return mark_legacy_route(response)


@admin_bp.route('/punch-location', methods=['POST'])
@token_required
@role_required(['admin'])
def set_punch_location():
    """
    设置打卡位置
    ---
    请求体: {"name": "xxx", "latitude": 1.0, "longitude": 1.0, "radius": 100, "enabled": 1}
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    radius = data.get('radius')
    enabled = data.get('enabled', 1)

    result = AdminService.save_punch_location(name, latitude, longitude, radius, enabled)
    response = jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    })
    response.status_code = 200
    return mark_legacy_route(response)


@admin_bp.route('/config', methods=['GET'])
@token_required
@role_required(['admin'])
def get_config():
    """
    获取全局配置
    ---
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    config = ConfigService.get_punch_config()
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': config
    }), 200


@admin_bp.route('/config', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_config():
    """
    更新全局配置
    ---
    请求体: {"global_time_check_enabled": true, ...}
    返回: {"code": 200, "message": "success", "data": {...}}
    """
    data = request.get_json()
    result = ConfigService.update_punch_config(data)
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    }), 200


@admin_bp.route('/dashboard/stats', methods=['GET'])
@token_required
@role_required(['admin'])
def dashboard_stats():
    """
    仪表盘聚合数据
    ---
    返回: {"code": 200, "data": {...}}
    """
    result = AdminService.get_dashboard_stats()
    return jsonify({'code': 200, 'message': 'success', 'data': result}), 200
