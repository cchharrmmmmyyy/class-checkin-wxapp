from flask import Blueprint, request, send_file
from io import BytesIO
from services import AdminService
from utils.jwt import token_required, role_required
from utils.api_response import success, error, mark_legacy_route

admin_attendance_bp = Blueprint('admin_attendance', __name__, url_prefix='/api/admin')

# 获取学生打卡记录
@admin_attendance_bp.route('/attendance-records', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def get_attendance_records():
    username = request.args.get('username', '').strip() or None
    user_id = request.args.get('user_id', '').strip() or None
    start_date = request.args.get('start_date', '').strip() or None
    end_date = request.args.get('end_date', '').strip() or None
    leave_status = request.args.get('leave_status', '').strip() or None
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)

    result = AdminService.get_attendance_records(
        username=username, user_id=user_id, start_date=start_date,
        end_date=end_date, leave_status=leave_status, page=page, size=size
    )
    return success(data=result)

# 导出学生打卡记录为CSV文件
@admin_attendance_bp.route('/attendance/csv', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def export_attendance_csv():
    username = request.args.get('username', '').strip() or None
    user_id = request.args.get('user_id', '').strip() or None
    start_date = request.args.get('start_date', '').strip() or None
    end_date = request.args.get('end_date', '').strip() or None
    leave_status = request.args.get('leave_status', '').strip() or None

    csv_bytes, filename = AdminService.export_attendance_records(
        username=username, user_id=user_id, start_date=start_date,
        end_date=end_date, leave_status=leave_status
    )
    return send_file(
        BytesIO(csv_bytes),
        mimetype='text/csv', as_attachment=True, download_name=filename
    )


@admin_attendance_bp.route('/attendance-records', methods=['POST'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def create_attendance_record():
    data = request.get_json() or {}
    record_id_raw = data.get('id')
    record_id = int(record_id_raw) if record_id_raw not in (None, '') else None
    user_id = (data.get('user_id') or '').strip()
    punch_date = data.get('punch_date', '').strip() or None
    leave_start_date = data.get('leave_start_date', '') or None
    leave_end_date = data.get('leave_end_date', '') or None
    leave_status = data.get('leave_status', 'pending').strip()

    if not user_id:
        return error(message='用户ID不能为空', code=5000, http_status=400)

    result = AdminService.save_attendance_record(
        record_id, user_id, punch_date, leave_start_date, leave_end_date, leave_status
    )
    response = success(
        data={**result, 'migration_hint': '该接口为兼容层，请迁移至 /api/admin/attendance/punch-records 或 /api/admin/attendance/leave-records'}
    )
    return mark_legacy_route(response)


@admin_attendance_bp.route('/attendance-records/<int:record_id>', methods=['DELETE'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def delete_attendance_record(record_id):
    result = AdminService.delete_attendance_record(record_id)
    return success(data=result)


# ---- 打卡记录 ----

@admin_attendance_bp.route('/attendance/punch-records', methods=['POST'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def create_punch_record():
    data = request.get_json() or {}
    user_id = (data.get('user_id') or '').strip()
    punch_date = (data.get('punch_date') or '').strip()

    if not user_id:
        return error(message='用户ID不能为空', code=5000, http_status=400)
    if not punch_date:
        return error(message='打卡日期不能为空', code=5001, http_status=400)

    result = AdminService.save_punch_record(
        record_id=None, user_id=user_id, punch_date=punch_date,
        punch_time=data.get('punch_time', '12:00:00'),
        latitude=data.get('latitude', 0.0), longitude=data.get('longitude', 0.0)
    )
    return success(data=result)


@admin_attendance_bp.route('/attendance/punch-records/<int:record_id>', methods=['PUT'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def update_punch_record(record_id):
    data = request.get_json() or {}
    user_id = (data.get('user_id') or '').strip()
    punch_date = (data.get('punch_date') or '').strip()

    if not user_id:
        return error(message='用户ID不能为空', code=5000, http_status=400)
    if not punch_date:
        return error(message='打卡日期不能为空', code=5001, http_status=400)

    result = AdminService.save_punch_record(
        record_id=record_id, user_id=user_id, punch_date=punch_date,
        punch_time=data.get('punch_time', '12:00:00'),
        latitude=data.get('latitude', 0.0), longitude=data.get('longitude', 0.0)
    )
    return success(data=result)


@admin_attendance_bp.route('/attendance/punch-records/<int:record_id>', methods=['DELETE'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def delete_punch_record(record_id):
    result = AdminService.delete_punch_record(record_id)
    return success(data=result)


# ---- 请假记录 ----

@admin_attendance_bp.route('/attendance/leave-records', methods=['POST'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def create_leave_record():
    data = request.get_json() or {}
    user_id = (data.get('user_id') or '').strip()
    leave_start_date = data.get('leave_start_date')
    leave_end_date = data.get('leave_end_date')

    if not user_id:
        return error(message='用户ID不能为空', code=5000, http_status=400)
    if not leave_start_date:
        return error(message='请假开始日期不能为空', code=5002, http_status=400)
    if not leave_end_date:
        return error(message='请假结束日期不能为空', code=5003, http_status=400)

    result = AdminService.save_leave_record(
        record_id=None, user_id=user_id,
        leave_start_date=leave_start_date,
        leave_end_date=leave_end_date,
        leave_status=(data.get('leave_status') or 'pending').strip(),
        leave_type=(data.get('leave_type') or 'personal').strip(),
        leave_reason=data.get('leave_reason')
    )
    return success(data=result)


@admin_attendance_bp.route('/attendance/leave-records/<int:record_id>', methods=['PUT'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def update_leave_record(record_id):
    data = request.get_json() or {}
    leave_status = (data.get('leave_status') or '').strip()

    if not leave_status:
        return error(message='请假状态不能为空', code=5004, http_status=400)

    result = AdminService.save_leave_record(
        record_id=record_id, user_id='', leave_status=leave_status
    )
    return success(data=result)


@admin_attendance_bp.route('/attendance/leave-records/<int:record_id>', methods=['DELETE'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def delete_leave_record(record_id):
    result = AdminService.delete_leave_record(record_id)
    return success(data=result)
