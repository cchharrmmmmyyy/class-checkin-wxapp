from flask import Blueprint, request, jsonify
from datetime import datetime
import sqlite3
from database import get_db_connection, execute_query, execute_query_one

# 创建教师蓝图
teacher_function = Blueprint('teacher', __name__, url_prefix='/api/teacher')

# 任命班委接口
@teacher_function.route('/appoint-monitor', methods=['POST'])
def appoint_monitor():
    """任命班委"""
    try:
        data = request.get_json()
        print(f"收到任命班委请求数据: {data}")
        
        student_id = data.get('student_id', '').strip()
        teacher_id = data.get('teacher_id', '').strip()
        class_name = data.get('class_name', '').strip()  # 新增班级名称参数
        
        print(f"解析参数: student_id={student_id}, teacher_id={teacher_id}, class_name={class_name}")
        
        # 验证输入
        if not student_id:
            return jsonify({
                'success': False,
                'message': '学生学号不能为空'
            }), 400
            
        if not teacher_id:
            return jsonify({
                'success': False,
                'message': '教师工号不能为空'
            }), 400
        
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 验证教师身份
        cursor.execute(
            "SELECT username, user_id, role, class FROM users WHERE user_id = ?",
            (teacher_id,)
        )
        teacher = cursor.fetchone()
        
        print(f"查询到的教师信息: {dict(teacher) if teacher else 'None'}")
        
        if not teacher or teacher['role'] != 'teacher':
            conn.close()
            print(f"教师身份验证失败: not_found={not teacher}, role={teacher['role'] if teacher else 'None'}")
            return jsonify({
                'success': False,
                'message': '教师身份验证失败'
            }), 403
        
        # 验证学生身份并获取班级信息
        cursor.execute(
            "SELECT username, user_id, role, class FROM users WHERE user_id = ?",
            (student_id,)
        )
        student = cursor.fetchone()
        
        print(f"查询到的学生信息: {dict(student) if student else 'None'}")
        
        if not student:
            conn.close()
            return jsonify({
                'success': False,
                'message': '未找到该学生'
            }), 404
            
        # 检查学生是否与教师在同一班级
        print(f"班级比较: 学生班级={student['class']}, 教师班级={teacher['class']}")
        if student['class'] != teacher['class']:
            conn.close()
            return jsonify({
                'success': False,
                'message': '该学生不在您的班级中'
            }), 403
        
        # 检查该学生是否已经是班委
        if student['role'] == 'monitor':
            conn.close()
            return jsonify({
                'success': False,
                'message': '该学生已经是班委'
            }), 400
        
        # 将指定学生角色改为班委（不再替换现有班委）
        cursor.execute(
            "UPDATE users SET role = 'monitor' WHERE user_id = ?",
            (student_id,)
        )
        
        conn.commit()
        conn.close()
        
        print(f"教师 {teacher['username']} 任命学生 {student['username']} 为班委")
        
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
        print(f"任命班委过程中发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'任命班委失败: {str(e)}'
        }), 500

# 获取班级班委信息接口
@teacher_function.route('/class-monitor/<class_name>', methods=['GET'])
def get_class_monitor(class_name):
    """获取班级班委信息"""
    try:
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询班级所有班委信息
        cursor.execute(
            "SELECT username, user_id FROM users WHERE class = ? AND role = 'monitor'",
            (class_name,)
        )
        monitors = cursor.fetchall()
        
        conn.close()
        
        # 转换为字典列表
        monitors_list = []
        for monitor in monitors:
            monitors_list.append({
                'username': monitor['username'],
                'user_id': monitor['user_id']
            })
        
        if monitors_list:
            return jsonify({
                'success': True,
                'message': '查询成功',
                'data': monitors_list
            }), 200
        else:
            return jsonify({
                'success': True,
                'message': '该班级暂无班委',
                'data': []
            }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询班委信息失败: {str(e)}'
        }), 500

# 获取教师班级学生列表接口
@teacher_function.route('/class-students/<class_name>', methods=['GET'])
def get_class_students(class_name):
    """获取教师班级学生列表"""
    try:
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询班级所有学生
        cursor.execute(
            "SELECT username, user_id, role FROM users WHERE class = ? AND role IN ('student', 'monitor')",
            (class_name,)
        )
        students = cursor.fetchall()
        
        # 转换为字典列表
        students_list = []
        for student in students:
            students_list.append({
                'username': student['username'],
                'user_id': student['user_id'],
                'role': student['role']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '查询成功',
            'data': students_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询学生列表失败: {str(e)}'
        }), 500

# 获取班级列表接口
@teacher_function.route('/class-list', methods=['GET'])
def get_class_list():
    """获取所有班级列表"""
    try:
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询所有班级
        cursor.execute(
            "SELECT DISTINCT class FROM users WHERE role = 'student' AND class != '' ORDER BY class"
        )
        classes = cursor.fetchall()
        
        conn.close()
        
        # 提取班级名称
        class_list = [c['class'] for c in classes]
        
        return jsonify({
            'success': True,
            'message': '查询成功',
            'data': class_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取班级列表失败: {str(e)}'
        }), 500

# 移除班委接口
@teacher_function.route('/remove-monitor', methods=['POST'])
def remove_monitor():
    """移除班委"""
    try:
        data = request.get_json()
        print(f"收到移除班委请求数据: {data}")
        
        student_id = data.get('student_id', '').strip()
        teacher_id = data.get('teacher_id', '').strip()
        
        print(f"解析参数: student_id={student_id}, teacher_id={teacher_id}")
        
        # 验证输入
        if not student_id:
            return jsonify({
                'success': False,
                'message': '学生学号不能为空'
            }), 400
            
        if not teacher_id:
            return jsonify({
                'success': False,
                'message': '教师工号不能为空'
            }), 400
        
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 验证教师身份
        cursor.execute(
            "SELECT username, user_id, role, class FROM users WHERE user_id = ?",
            (teacher_id,)
        )
        teacher = cursor.fetchone()
        
        print(f"查询到的教师信息: {dict(teacher) if teacher else 'None'}")
        
        if not teacher or teacher['role'] != 'teacher':
            conn.close()
            print(f"教师身份验证失败: not_found={not teacher}, role={teacher['role'] if teacher else 'None'}")
            return jsonify({
                'success': False,
                'message': '教师身份验证失败'
            }), 403
        
        # 验证学生身份并获取班级信息
        cursor.execute(
            "SELECT username, user_id, role, class FROM users WHERE user_id = ?",
            (student_id,)
        )
        student = cursor.fetchone()
        
        print(f"查询到的学生信息: {dict(student) if student else 'None'}")
        
        if not student:
            conn.close()
            return jsonify({
                'success': False,
                'message': '未找到该学生'
            }), 404
            
        # 检查学生是否与教师在同一班级
        print(f"班级比较: 学生班级={student['class']}, 教师班级={teacher['class']}")
        if student['class'] != teacher['class']:
            conn.close()
            return jsonify({
                'success': False,
                'message': '该学生不在您的班级中'
            }), 403
        
        # 检查该学生是否是班委
        if student['role'] != 'monitor':
            conn.close()
            return jsonify({
                'success': False,
                'message': '该学生不是班委'
            }), 400
        
        # 将学生角色改为普通学生
        cursor.execute(
            "UPDATE users SET role = 'student' WHERE user_id = ?",
            (student_id,)
        )
        
        conn.commit()
        conn.close()
        
        print(f"教师 {teacher['username']} 移除学生 {student['username']} 的班委职务")
        
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
        print(f"移除班委过程中发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'移除班委失败: {str(e)}'
        }), 500

@teacher_function.route('/leave-applications', methods=['GET'])
def get_leave_applications():
    """获取待审批请假申请"""
    try:
        class_name = request.args.get('class_name', '')
        
        if not class_name:
            return jsonify({
                'success': False,
                'message': '班级名称不能为空'
            }), 400
        
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询班级待审批请假申请，只查询有请假日期的记录
        cursor.execute(
            "SELECT * FROM punch_records WHERE leave_status = 'pending' AND leave_start_date IS NOT NULL AND leave_end_date IS NOT NULL AND user_id IN (SELECT user_id FROM users WHERE class = ?) ORDER BY id DESC",
            (class_name,)
        )
        
        applications = cursor.fetchall()
        
        # 转换为字典列表
        applications_list = []
        for app in applications:
            applications_list.append({
                'id': app['id'],
                'username': app['username'],
                'user_id': app['user_id'],
                'leave_start_date': app['leave_start_date'],
                'leave_end_date': app['leave_end_date'],
                'leave_status': app['leave_status']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '查询成功',
            'data': applications_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500

@teacher_function.route('/approve-leave', methods=['POST'])
def approve_leave():
    """审批请假申请"""
    try:
        data = request.get_json()
        print(f"收到请假审批数据: {data}")
        
        leave_id = data.get('id', '')
        status = data.get('status', '')
        teacher_id = data.get('teacher_id', '')
        
        # 验证输入
        if not leave_id or not status or not teacher_id:
            return jsonify({
                'success': False,
                'message': '请假ID、审批状态和教师ID不能为空'
            }), 400
        
        # 验证审批状态
        if status not in ['approved', 'rejected']:
            return jsonify({
                'success': False,
                'message': '审批状态只能是approved或rejected'
            }), 400
        
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 验证教师身份
        cursor.execute(
            "SELECT username, role, class FROM users WHERE user_id = ?",
            (teacher_id,)
        )
        teacher = cursor.fetchone()
        
        if not teacher or teacher['role'] != 'teacher':
            conn.close()
            return jsonify({
                'success': False,
                'message': '教师身份验证失败'
            }), 403
        
        # 验证请假申请是否存在且属于该班级
        cursor.execute(
            "SELECT * FROM punch_records WHERE id = ? AND user_id IN (SELECT user_id FROM users WHERE class = ?)",
            (leave_id, teacher['class'])
        )
        leave_application = cursor.fetchone()
        
        if not leave_application:
            conn.close()
            return jsonify({
                'success': False,
                'message': '未找到该请假申请或该申请不属于您的班级'
            }), 404
        
        # 更新请假状态
        cursor.execute(
            "UPDATE punch_records SET leave_status = ? WHERE id = ?",
            (status, leave_id)
        )
        
        conn.commit()
        conn.close()
        
        print(f"教师 {teacher['username']} 审批请假申请 {leave_id} 为 {status}")
        
        return jsonify({
            'success': True,
            'message': '请假审批成功',
            'data': {
                'leave_id': leave_id,
                'status': status
            }
        }), 200
        
    except Exception as e:
        print(f"请假审批过程中发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'请假审批失败: {str(e)}'
        }), 500