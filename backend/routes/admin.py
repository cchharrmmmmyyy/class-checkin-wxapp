from flask import Blueprint, request, jsonify, send_from_directory
from database import execute_query, execute_query_one, execute_update, hash_password
from utils.auth import token_required, role_required
import random
import string

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def generate_random_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@admin_bp.route('/users', methods=['GET'])
@token_required
@role_required('admin')
def get_all_users():
    try:
        users = execute_query("SELECT * FROM users ORDER BY role, class, username")

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

        hashed_password = hash_password(password)

        existing_user = execute_query_one(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )

        if existing_user:
            execute_update(
                "UPDATE users SET username = ?, password = ?, role = ?, class = ? WHERE user_id = ?",
                (username, hashed_password, role, class_name, user_id)
            )
            message = '用户更新成功'
        else:
            execute_update(
                "INSERT INTO users (username, password, role, class, user_id) VALUES (?, ?, ?, ?, ?)",
                (username, hashed_password, role, class_name, user_id)
            )
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
        target = execute_query_one(
            "SELECT role FROM users WHERE user_id = ?",
            (user_id,)
        )

        if not target:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        if target['role'] == 'admin':
            admin_count = execute_query_one(
                "SELECT COUNT(*) as cnt FROM users WHERE role = 'admin'"
            )
            if admin_count['cnt'] <= 1:
                return jsonify({
                    'success': False,
                    'message': '不能删除最后一个管理员账户'
                }), 403

        rowcount = execute_update(
            "DELETE FROM users WHERE user_id = ?",
            (user_id,)
        )

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

        query = "SELECT pr.*, u.username FROM punch_records pr LEFT JOIN users u ON pr.user_id = u.user_id WHERE 1=1"
        params = []

        if username:
            query += " AND u.username LIKE ?"
            params.append(f"%{username}%")

        if user_id:
            query += " AND pr.user_id LIKE ?"
            params.append(f"%{user_id}%")

        date_filter = "COALESCE(pr.punch_date, pr.leave_start_date)"
        if start_date:
            query += f" AND {date_filter} >= ?"
            params.append(start_date)

        if end_date:
            query += f" AND {date_filter} <= ?"
            params.append(end_date)

        if leave_status:
            query += " AND pr.leave_status = ?"
            params.append(leave_status)

        query += f" ORDER BY {date_filter} DESC"

        records = execute_query(query, params)

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
            execute_update(
                "UPDATE punch_records SET user_id = ?, punch_date = ?, leave_start_date = ?, leave_end_date = ?, leave_status = ? WHERE id = ?",
                (user_id, punch_date, leave_start_date, leave_end_date, leave_status, record_id)
            )
            message = '考勤记录更新成功'
        else:
            execute_update(
                "INSERT INTO punch_records (user_id, punch_date, leave_start_date, leave_end_date, leave_status) VALUES (?, ?, ?, ?, ?)",
                (user_id, punch_date, leave_start_date, leave_end_date, leave_status)
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
        rowcount = execute_update(
            "DELETE FROM punch_records WHERE id = ?",
            (record_id,)
        )

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
        location = execute_query_one("SELECT * FROM punch_location LIMIT 1")

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

        existing = execute_query_one("SELECT id FROM punch_location")

        if existing:
            execute_update(
                "UPDATE punch_location SET name = ?, latitude = ?, longitude = ?, radius = ?, enabled = ? WHERE id = ?",
                (name, latitude, longitude, radius, enabled, existing['id'])
            )
            message = '打卡位置更新成功'
        else:
            execute_update(
                "INSERT INTO punch_location (name, latitude, longitude, radius, enabled) VALUES (?, ?, ?, ?, ?)",
                (name, latitude, longitude, radius, enabled)
            )
            message = '打卡位置设置成功'

        return jsonify({
            'success': True,
            'message': message
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

        target_user = execute_query_one(
            "SELECT role FROM users WHERE user_id = ?",
            (user_id,)
        )

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
        hashed_password = hash_password(new_password)

        rowcount = execute_update(
            "UPDATE users SET password = ? WHERE user_id = ?",
            (hashed_password, user_id)
        )

        if rowcount == 0:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

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