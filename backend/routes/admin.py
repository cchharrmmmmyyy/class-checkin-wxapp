from flask import Blueprint, request, jsonify
from db_connection import hash_password
from dao import user_dao, punch_record_dao, location_dao
from utils.auth import token_required, role_required
from config import Config
import random
import string

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def generate_random_password(length=None):
    if length is None:
        length = Config.RANDOM_PASSWORD_LENGTH
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


@admin_bp.route('/users', methods=['GET'])
@token_required
@role_required('admin')
def get_all_users():
    try:
        users = user_dao.get_all_users()
        user_list = [{
            'username': u['username'],
            'user_id': u['user_id'],
            'role': u['role'],
            'class': u['class']
        } for u in users]

        return jsonify({
            'success': True,
            'data': user_list
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户列表失败: {str(e)}'
        }), 500


@admin_bp.route('/users', methods=['POST'])
@token_required
@role_required('admin')
def add_or_update_user():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        role = data.get('role', '').strip()
        class_name = data.get('class', '').strip()
        user_id = data.get('user_id', '').strip()

        if not username or not password or not role or not user_id:
            return jsonify({
                'success': False,
                'message': '用户名、密码、角色和用户ID不能为空'
            }), 400

        valid_roles = ('admin', 'teacher', 'student', 'monitor')
        if role not in valid_roles:
            return jsonify({
                'success': False,
                'message': f'角色必须是 {", ".join(valid_roles)} 之一'
            }), 400

        if role == 'admin':
            if class_name:
                return jsonify({
                    'success': False,
                    'message': '管理员不应设置班级'
                }), 400
        elif not class_name:
            return jsonify({
                'success': False,
                'message': '老师、学生、班委必须设置班级'
            }), 400

        existing_user = user_dao.get_user_by_id(user_id)

        if existing_user:
            user_dao.update_user(username, user_id, password, role, class_name)
            message = '用户更新成功'
        else:
            user_dao.create_user(username, user_id, password, role, class_name)
            message = '用户添加成功'

        return jsonify({
            'success': True,
            'message': message
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'操作失败: {str(e)}'
        }), 500


@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_user(user_id):
    try:
        target = user_dao.get_user_by_id(user_id)

        if not target:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        if target['role'] == 'admin':
            admin_count = user_dao.count_admins()
            if admin_count <= 1:
                return jsonify({
                    'success': False,
                    'message': '不能删除最后一个管理员账户'
                }), 403

        rowcount = user_dao.delete_user(user_id)

        if rowcount == 0:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        return jsonify({
            'success': True,
            'message': '用户删除成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除用户失败: {str(e)}'
        }), 500


@admin_bp.route('/attendance-records', methods=['GET'])
@token_required
@role_required('admin')
def get_attendance_records():
    try:
        username = request.args.get('username', '').strip()
        user_id = request.args.get('user_id', '').strip()
        start_date = request.args.get('start_date', '').strip()
        end_date = request.args.get('end_date', '').strip()
        leave_status = request.args.get('leave_status', '').strip()

        records = punch_record_dao.get_all_attendance_records(
            username=username or None,
            user_id=user_id or None,
            start_date=start_date or None,
            end_date=end_date or None,
            leave_status=leave_status or None
        )

        record_list = [{
            'id': r['id'],
            'username': r['username'],
            'user_id': r['user_id'],
            'punch_date': r['punch_date'],
            'leave_start_date': r['leave_start_date'],
            'leave_end_date': r['leave_end_date'],
            'leave_status': r['leave_status']
        } for r in records]

        return jsonify({
            'success': True,
            'data': record_list
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取考勤记录失败: {str(e)}'
        }), 500


@admin_bp.route('/attendance-records', methods=['POST'])
@token_required
@role_required('admin')
def add_or_update_attendance_record():
    try:
        data = request.get_json()
        record_id = data.get('id', '').strip()
        user_id = data.get('user_id', '').strip()
        punch_date = data.get('punch_date', '').strip()
        leave_start_date = data.get('leave_start_date', '')
        leave_end_date = data.get('leave_end_date', '')
        leave_status = data.get('leave_status', 'pending').strip()

        if not user_id:
            return jsonify({
                'success': False,
                'message': '用户ID不能为空'
            }), 400

        has_punch = bool(punch_date)
        has_leave = bool(leave_start_date and leave_end_date)

        if not has_punch and not has_leave:
            return jsonify({
                'success': False,
                'message': '打卡日期和请假日期不能同时为空'
            }), 400

        if has_punch and has_leave:
            return jsonify({
                'success': False,
                'message': '打卡记录和请假记录不能同时存在'
            }), 400

        if has_leave:
            valid_statuses = ('pending', 'approved', 'rejected')
            if leave_status not in valid_statuses:
                return jsonify({
                    'success': False,
                    'message': f'请假状态必须是 {", ".join(valid_statuses)} 之一'
                }), 400

        if record_id:
            punch_record_dao.update_punch_record(
                record_id, user_id, punch_date or None,
                leave_start_date or None, leave_end_date or None, leave_status
            )
            message = '考勤记录更新成功'
        else:
            punch_record_dao.create_attendance_record(
                user_id, punch_date or None,
                leave_start_date or None, leave_end_date or None, leave_status
            )
            message = '考勤记录添加成功'

        return jsonify({
            'success': True,
            'message': message
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'操作考勤记录失败: {str(e)}'
        }), 500


@admin_bp.route('/attendance-records/<int:record_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_attendance_record(record_id):
    try:
        rowcount = punch_record_dao.delete_punch_record(record_id)

        if rowcount == 0:
            return jsonify({
                'success': False,
                'message': '考勤记录不存在'
            }), 404

        return jsonify({
            'success': True,
            'message': '考勤记录删除成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除考勤记录失败: {str(e)}'
        }), 500


@admin_bp.route('/punch-location', methods=['GET'])
@token_required
@role_required('admin')
def get_punch_location():
    try:
        location = location_dao.get_punch_location()

        if location:
            return jsonify({
                'success': True,
                'data': {
                    'id': location['id'],
                    'name': location['name'],
                    'latitude': location['latitude'],
                    'longitude': location['longitude'],
                    'radius': location['radius'],
                    'enabled': location['enabled']
                }
            })
        else:
            return jsonify({
                'success': True,
                'data': None
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取打卡位置失败: {str(e)}'
        }), 500


@admin_bp.route('/punch-location', methods=['POST'])
@token_required
@role_required('admin')
def set_punch_location():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        radius = data.get('radius')
        enabled = data.get('enabled', 1)

        if not name or latitude is None or longitude is None or radius is None:
            return jsonify({
                'success': False,
                'message': '位置名称、经纬度半径不能为空'
            }), 400

        location_dao.upsert_punch_location(name, latitude, longitude, radius, enabled)

        return jsonify({
            'success': True,
            'message': '打卡位置设置成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'设置打卡位置失败: {str(e)}'
        }), 500


@admin_bp.route('/reset-password', methods=['POST'])
@token_required
@role_required('admin')
def reset_password():
    try:
        data = request.get_json()
        user_id = data.get('user_id', '').strip()

        if not user_id:
            return jsonify({
                'success': False,
                'message': '用户ID不能为空'
            }), 400

        target_user = user_dao.get_user_by_id(user_id)

        if not target_user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        if target_user['role'] == 'admin':
            return jsonify({
                'success': False,
                'message': '不允许重置管理员账户密码'
            }), 403

        new_password = generate_random_password()
        user_dao.reset_password(user_id, new_password)

        return jsonify({
            'success': True,
            'message': '密码重置成功',
            'new_password': new_password
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'重置密码失败: {str(e)}'
        }), 500
