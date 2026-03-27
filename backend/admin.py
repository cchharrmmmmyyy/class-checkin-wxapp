from flask import Blueprint, request, jsonify, send_from_directory
from database import get_db_connection, execute_query, execute_query_one, verify_password, hash_password

# 创建管理员蓝图
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# 管理员登录接口
@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """管理员登录验证"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        user_id = data.get('user_id', '').strip()
        user_password = data.get('password', '').strip()
        
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 执行查询 - 使用 user_id 查询管理员
        cursor.execute(
            "SELECT * FROM users WHERE user_id = ? AND role = 'admin'",
            (user_id,)
        )
        
        # 获取查询结果
        admin = cursor.fetchone()
        conn.close()
        
        # 验证用户 - 使用哈希密码验证
        if admin and verify_password(user_password, admin['password']):
            return jsonify({
                'success': True,
                'message': '登录成功',
                'admin': {
                    'username': admin['username'],
                    'user_id': admin['user_id']
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '工号或密码错误'
            }), 401
    except Exception as e:
        # 处理异常
        return jsonify({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }), 500

# 获取所有用户列表
@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    """获取所有用户信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users ORDER BY role, class, username")
        users = cursor.fetchall()
        conn.close()
        
        # 转换为字典列表
        user_list = []
        for user in users:
            user_list.append({
                'username': user['username'],
                'user_id': user['user_id'],
                'role': user['role'],
                'class': user['class']
            })
        
        return jsonify({
            'success': True,
            'data': user_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户列表失败: {str(e)}'
        }), 500

# 添加或修改用户
@admin_bp.route('/users', methods=['POST'])
def add_or_update_user():
    """添加新用户或修改现有用户"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        role = data.get('role', '').strip()
        class_name = data.get('class', '').strip()
        user_id = data.get('user_id', '').strip()
        
        # 验证必填字段
        if not username or not password or not role or not user_id:
            return jsonify({
                'success': False,
                'message': '用户名、密码、角色和用户ID不能为空'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查用户是否存在
        cursor.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )
        existing_user = cursor.fetchone()
        
        if existing_user:
            # 更新现有用户 - 密码使用哈希存储
            hashed_password = hash_password(password)
            cursor.execute(
                "UPDATE users SET username = ?, password = ?, role = ?, class = ? WHERE user_id = ?",
                (username, hashed_password, role, class_name, user_id)
            )
            message = '用户更新成功'
        else:
            # 添加新用户 - 密码使用哈希存储
            hashed_password = hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password, role, class, user_id) VALUES (?, ?, ?, ?, ?)",
                (username, hashed_password, role, class_name, user_id)
            )
            message = '用户添加成功'
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'操作失败: {str(e)}'
        }), 500

# 删除用户
@admin_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除指定用户"""
    try:
        # 不允许删除管理员账户
        if user_id == 'admin001':
            return jsonify({
                'success': False,
                'message': '不允许删除管理员账户'
            }), 403
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM users WHERE user_id = ?",
            (user_id,)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '用户删除成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除用户失败: {str(e)}'
        }), 500

# 获取考勤记录列表
@admin_bp.route('/attendance-records', methods=['GET'])
def get_attendance_records():
    """获取考勤记录列表，支持筛选"""
    try:
        # 获取查询参数
        username = request.args.get('username', '').strip()
        user_id = request.args.get('user_id', '').strip()
        start_date = request.args.get('start_date', '').strip()
        end_date = request.args.get('end_date', '').strip()
        leave_status = request.args.get('leave_status', '').strip()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建查询语句
        query = "SELECT pr.*, u.username FROM punch_records pr LEFT JOIN users u ON pr.user_id = u.user_id WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id LIKE ?"
            params.append(f"%{user_id}%")
        
        if start_date:
            query += " AND punch_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND punch_date <= ?"
            params.append(end_date)
        
        if leave_status:
            query += " AND leave_status = ?"
            params.append(leave_status)
        
        # 添加排序
        query += " ORDER BY punch_date DESC"
        
        cursor.execute(query, params)
        records = cursor.fetchall()
        conn.close()
        
        # 转换为字典列表
        record_list = []
        for record in records:
            record_list.append({
                'id': record['id'],
                'username': record['username'],
                'user_id': record['user_id'],
                'punch_date': record['punch_date'],
                'leave_start_date': record['leave_start_date'],
                'leave_end_date': record['leave_end_date'],
                'leave_status': record['leave_status']
            })
        
        return jsonify({
            'success': True,
            'data': record_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取考勤记录失败: {str(e)}'
        }), 500

# 修改考勤记录
@admin_bp.route('/attendance-records', methods=['POST'])
def add_or_update_attendance_record():
    """添加或修改考勤记录"""
    try:
        data = request.get_json()
        record_id = data.get('id', '').strip()
        user_id = data.get('user_id', '').strip()
        punch_date = data.get('punch_date', '').strip()
        leave_start_date = data.get('leave_start_date', '')
        leave_end_date = data.get('leave_end_date', '')
        leave_status = data.get('leave_status', 'pending').strip()
        
        # 验证必填字段
        if not user_id or not punch_date:
            return jsonify({
                'success': False,
                'message': '用户ID和打卡日期不能为空'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取用户名
        cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        username = user['username'] if user else ''
        
        if record_id:
            # 更新现有记录
            cursor.execute(
                "UPDATE punch_records SET user_id = ?, punch_date = ?, leave_start_date = ?, leave_end_date = ?, leave_status = ? WHERE id = ?",
                (user_id, punch_date, leave_start_date, leave_end_date, leave_status, record_id)
            )
            message = '考勤记录更新成功'
        else:
            # 添加新记录
            cursor.execute(
                "INSERT INTO punch_records (user_id, punch_date, leave_start_date, leave_end_date, leave_status) VALUES (?, ?, ?, ?, ?)",
                (user_id, punch_date, leave_start_date, leave_end_date, leave_status)
            )
            message = '考勤记录添加成功'
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'操作考勤记录失败: {str(e)}'
        }), 500

# 删除考勤记录
@admin_bp.route('/attendance-records/<record_id>', methods=['DELETE'])
def delete_attendance_record(record_id):
    """删除指定考勤记录"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM punch_records WHERE id = ?",
            (record_id,)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '考勤记录删除成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除考勤记录失败: {str(e)}'
        }), 500

# 静态文件服务
@admin_bp.route('/admin.html')
def admin_page():
    """提供管理员HTML页面"""
    return send_from_directory('.', 'admin.html')

# 获取打卡位置配置
@admin_bp.route('/punch-location', methods=['GET'])
def get_punch_location():
    """获取打卡位置配置"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM punch_location LIMIT 1")
        location = cursor.fetchone()
        conn.close()
        
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

# 设置打卡位置
@admin_bp.route('/punch-location', methods=['POST'])
def set_punch_location():
    """设置打卡位置"""
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
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM punch_location")
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute(
                "UPDATE punch_location SET name = ?, latitude = ?, longitude = ?, radius = ?, enabled = ? WHERE id = ?",
                (name, latitude, longitude, radius, enabled, existing['id'])
            )
            message = '打卡位置更新成功'
        else:
            cursor.execute(
                "INSERT INTO punch_location (name, latitude, longitude, radius, enabled) VALUES (?, ?, ?, ?, ?)",
                (name, latitude, longitude, radius, enabled)
            )
            message = '打卡位置设置成功'
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'设置打卡位置失败: {str(e)}'
        }), 500

import random
import string

def generate_random_password(length=8):
    """生成随机密码"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@admin_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """重置用户密码为随机密码"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', '').strip()
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': '用户ID不能为空'
            }), 400
        
        if user_id == 'ADMIN001':
            return jsonify({
                'success': False,
                'message': '不允许重置管理员账户密码'
            }), 403
        
        new_password = generate_random_password()
        hashed_password = hash_password(new_password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE users SET password = ? WHERE user_id = ?",
            (hashed_password, user_id)
        )
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        conn.commit()
        conn.close()
        
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
