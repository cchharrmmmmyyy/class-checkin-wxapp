from flask import Blueprint, request, jsonify
from datetime import datetime
import sqlite3
from database import get_db_connection, execute_query, execute_query_one

# 创建学生蓝图
student_function = Blueprint('student', __name__, url_prefix='/api/student')

# 在这里可以添加学生相关的路由
@student_function.route('/profile', methods=['GET'])
def get_profile():
    """获取学生资料"""
    return {'message': '学生资料接口'}

@student_function.route('/punch', methods=['POST'])
def submit_punch():
    """提交打卡记录"""
    try:
        data = request.get_json()
        print(f"收到打卡请求数据: {data}")
        
        username = data.get('username', '')
        user_id = data.get('user_id', '')
        role = data.get('role', '')
        class_name = data.get('class', '')
        
        print(f"用户信息: username={username}, user_id={user_id}, role={role}, class={class_name}")
        
        # 获取当前日期
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        print(f"当前日期: {today}")
        
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查今天是否已经打卡
        cursor.execute(
            "SELECT id FROM punch_records WHERE user_id = ? AND punch_date = ?",
            (user_id, today)
        )
        existing_record = cursor.fetchone()
        
        if existing_record:
            print(f"用户 {user_id} 今日已打卡")
            conn.close()
            return jsonify({
                'success': False,
                'message': '今日已打卡',
                'already_punched': True  #添加标志，便于前端处理
            }), 400
        
        # 插入打卡记录
        cursor.execute(
            "INSERT INTO punch_records (username, user_id, punch_date) VALUES (?, ?, ?)",
            (username, user_id, today)
        )
        
        conn.commit()
        conn.close()
        
        print(f"用户 {user_id} 打卡成功")
        return jsonify({
            'success': True,
            'message': '打卡成功',
            'data': {
                'punch_date': today
            }
        }), 200
        
    except Exception as e:
        print(f"打卡过程中发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'打卡失败: {str(e)}'
        }), 500

@student_function.route('/records/<user_id>', methods=['GET'])
def get_punch_records(user_id):
    """获取个人打卡记录"""
    try:
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询个人打卡记录，按日期降序排列
        cursor.execute(
            "SELECT * FROM punch_records WHERE user_id = ? ORDER BY punch_date DESC LIMIT 30",
            (user_id,)
        )
        
        records = cursor.fetchall()
        
        # 转换为字典列表
        records_list = []
        for record in records:
            records_list.append({
                'id': record['id'],
                'user_id': record['user_id'],
                'username': record['username'],
                'punch_date': record['punch_date']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '查询成功',
            'data': records_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500

@student_function.route('/apply-leave', methods=['POST'])
def apply_leave():
    """提交请假申请"""
    try:
        data = request.get_json()
        print(f"收到请假申请数据: {data}")
        
        username = data.get('username', '')
        user_id = data.get('user_id', '')
        leave_start_date = data.get('leave_start_date', '')
        leave_end_date = data.get('leave_end_date', '')
        
        # 验证输入
        if not username or not user_id or not leave_start_date or not leave_end_date or leave_start_date == 'null' or leave_end_date == 'null' or leave_start_date == 'undefined' or leave_end_date == 'undefined':
            return jsonify({
                'success': False,
                'message': '用户名、用户ID、请假开始和结束日期不能为空'
            }), 400
        
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 插入请假记录
        cursor.execute(
            "INSERT INTO punch_records (username, user_id, punch_date, leave_start_date, leave_end_date, leave_status) VALUES (?, ?, ?, ?, ?, 'pending')",
            (username, user_id, leave_start_date, leave_start_date, leave_end_date)
        )
        
        conn.commit()
        conn.close()
        
        print(f"用户 {user_id} 请假申请成功")
        return jsonify({
            'success': True,
            'message': '请假申请提交成功，等待老师批准',
            'data': {
                'leave_start_date': leave_start_date,
                'leave_end_date': leave_end_date
            }
        }), 200
        
    except Exception as e:
        print(f"请假申请过程中发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'请假申请失败: {str(e)}'
        }), 500

@student_function.route('/leave-records', methods=['GET'])
def get_leave_records():
    """获取个人请假记录"""
    try:
        user_id = request.args.get('user_id', '')
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': '用户ID不能为空'
            }), 400
        
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询个人请假记录
        cursor.execute(
            "SELECT * FROM punch_records WHERE user_id = ? AND leave_start_date IS NOT NULL ORDER BY leave_start_date DESC",
            (user_id,)
        )
        
        records = cursor.fetchall()
        
        # 转换为字典列表
        records_list = []
        for record in records:
            records_list.append({
                'id': record['id'],
                'user_id': record['user_id'],
                'username': record['username'],
                'leave_start_date': record['leave_start_date'],
                'leave_end_date': record['leave_end_date'],
                'leave_status': record['leave_status']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '查询成功',
            'data': records_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500

@student_function.route('/class-records/<class_name>', methods=['GET'])
def get_class_punch_records(class_name):
    """获取班级打卡记录"""
    try:
        # 获取今日日期
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取班级所有学生（包括班委）
        cursor.execute("SELECT username, user_id, role FROM users WHERE class = ? AND role IN ('student', 'monitor')", (class_name,))
        students = cursor.fetchall()
        
        # 查询班级今日打卡记录
        cursor.execute(
            "SELECT user_id FROM punch_records WHERE user_id IN (SELECT user_id FROM users WHERE class = ?) AND punch_date = ?",
            (class_name, today)
        )
        
        punched_records = cursor.fetchall()
        punched_user_ids = [record['user_id'] for record in punched_records]
        
        # 查询班级今日请假记录
        cursor.execute(
            "SELECT user_id FROM punch_records WHERE user_id IN (SELECT user_id FROM users WHERE class = ?) AND ? BETWEEN leave_start_date AND leave_end_date AND leave_status = 'approved'",
            (class_name, today)
        )
        
        leave_records = cursor.fetchall()
        leave_user_ids = [record['user_id'] for record in leave_records]
        
        # 构建班级打卡情况
        class_records = []
        for student in students:
            # 检查学生是否已打卡
            punched = student['user_id'] in punched_user_ids
            # 检查学生是否处于请假状态
            on_leave = student['user_id'] in leave_user_ids
            
            # 添加角色信息，如果是班委则标记
            display_name = student['username']
            if student['role'] == 'monitor':
                display_name = student['username'] + ' (班委)'
            
            # 确定打卡状态显示
            punch_status = '请假' if on_leave else ('已打卡' if punched else '未打卡')
            
            class_records.append({
                'username': display_name,
                'user_id': student['user_id'],
                'role': student['role'],
                'punched': punched,
                'on_leave': on_leave,
                'punchTime': punch_status
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '查询成功',
            'data': class_records
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500
