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
        
        # 构建班级打卡情况
        class_records = []
        for student in students:
            # 检查学生是否已打卡
            punched = student['user_id'] in punched_user_ids
            
            # 添加角色信息，如果是班委则标记
            display_name = student['username']
            if student['role'] == 'monitor':
                display_name = student['username'] + ' (班委)'
            
            class_records.append({
                'username': display_name,
                'user_id': student['user_id'],
                'role': student['role'],
                'punched': punched,
                'punchTime': '已打卡' if punched else '未打卡'
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
