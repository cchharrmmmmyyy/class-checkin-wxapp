from database import execute_query
from flask import Blueprint, request, jsonify
from datetime import datetime
from utils.geo import calculate_distance
from database import  execute_query_one, execute_update

from utils.auth import token_required, role_required

# 创建学生蓝图
student_function = Blueprint('student', __name__, url_prefix='/api/students')


@student_function.route('/profile', methods=['GET'])
@token_required
def get_profile(): # 获取学生资料
    """获取学生资料，包含学号、用户名、角色、班级"""
    user_info = request.user_info
    return jsonify({
        'success': True,
        'user': {
            'user_id': user_info.get('user_id'),
            'username': user_info.get('username'),
            'role': user_info.get('role'),
            'class': user_info.get('class')
        }
    })

@student_function.route('/punch', methods=['POST'])
@token_required
@role_required('student', 'monitor')
def submit_punch():# 提交打卡记录，包含位置信息，待优化查询流程
    """提交打卡记录"""
    try:
        user_id = request.user_info.get('user_id')
        role = request.user_info.get('role')
        class_name = request.user_info.get('class', '暂无班级')
        data = request.get_json()
        print(f"收到打卡请求数据: {data}")
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        print(f"用户信息: user_id={user_id}, role={role}, class={class_name}, lat={latitude}, lng={longitude}")

        #位置验证：检查用户是否在打卡范围内
        punch_location = execute_query_one("SELECT * FROM punch_location")  
        if punch_location and punch_location['enabled'] and latitude is not None and longitude is not None:# 检查打卡点是否存在且启用，且用户位置信息存在
            target_lat = punch_location['latitude']
            target_lng = punch_location['longitude']
            radius = punch_location['radius']
            distance = calculate_distance(latitude, longitude, target_lat, target_lng)
            print(f"距离打卡点 {punch_location['name']} {distance:.2f} 米")
            
            if distance > radius:
                print(f"用户 {user_id} 打卡失败：超出允许范围")
                return jsonify({
                    'success': False,
                    'message': f'不在打卡范围内，距离打卡点 {int(distance)} 米',
                    'out_of_range': True
                }), 400
        elif punch_location and punch_location['enabled']:
            print(f"用户 {user_id} 打卡失败：未获取到位置")
            return jsonify({
                'success': False,
                'message': '无法获取您的位置，请确保定位服务已开启',
                'no_location': True
            }), 400
        
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        print(f"当前日期: {today}")
        
        existing_record = execute_query_one(
            "SELECT id FROM punch_records WHERE user_id = ? AND punch_date = ?",
            (user_id, today)
        )
        
        if existing_record:
            print(f"用户 {user_id} 今日已打卡")
            return jsonify({
                'success': False,
                'message': '今日已打卡',
                'already_punched': True
            }), 400
        
        execute_update(
            "INSERT INTO punch_records (user_id, punch_date) VALUES (?, ?)",
            (user_id, today)
        )
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

@student_function.route('/records', methods=['GET'])
@token_required
def get_punch_records():# 获取个人打卡记录
    """获取个人打卡记录,按时间倒序排列,最多30条"""
    user_id = request.user_info.get('user_id')

    try:
        records = execute_query(
            "SELECT pr.*, u.username FROM punch_records pr LEFT JOIN users u ON pr.user_id = u.user_id WHERE pr.user_id = ? ORDER BY pr.punch_date DESC LIMIT 30",
            (user_id,)
        )
        
        records_list = []
        for record in records:
            records_list.append({
                'id': record['id'],
                'user_id': record['user_id'],
                'username': record['username'],
                'punch_date': record['punch_date']
            })
        
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
@token_required
@role_required('student', 'monitor')
def apply_leave():# 提交请假申请
    """提交请假申请"""
    try:
        user_id = request.user_info.get('user_id')
        
        data = request.get_json()
        print(f"收到请假申请数据: {data}")
        
        leave_start_date = data.get('leave_start_date', '')
        leave_end_date = data.get('leave_end_date', '')
        
        # 验证输入
        if not user_id or not leave_start_date or not leave_end_date or leave_start_date == 'null' or leave_end_date == 'null' or leave_start_date == 'undefined' or leave_end_date == 'undefined':
            return jsonify({
                'success': False,
                'message': '用户ID、请假开始和结束日期不能为空'
            }), 400
        
        # 验证日期逻辑
        today = datetime.now().strftime('%Y-%m-%d')
        if leave_start_date < today:
            return jsonify({
                'success': False,
                'message': '请假开始日期不能是过去日期'
            }), 400
        
        if leave_end_date < leave_start_date:
            return jsonify({
                'success': False,
                'message': '请假结束日期不能早于开始日期'
            }), 400
        
        execute_update(
            "INSERT INTO punch_records (user_id, punch_date, leave_start_date, leave_end_date, leave_status) VALUES (?, ?, ?, ?, 'pending')",
            (user_id, None, leave_start_date, leave_end_date)
        )
        
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
@token_required
def get_leave_records():# 获取个人请假记录
    """获取个人请假记录"""
    user_id = request.user_info.get('user_id')

    try:
        records = execute_query(
            "SELECT pr.*, u.username FROM punch_records pr LEFT JOIN users u ON pr.user_id = u.user_id WHERE pr.user_id = ? AND pr.leave_start_date IS NOT NULL ORDER BY pr.leave_start_date DESC",
            (user_id,)
        )
        
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
@token_required
@role_required('monitor', 'teacher')
def get_class_punch_records(class_name):
    """获取班级打卡记录"""
    try:
        # 获取今日日期
        today = datetime.now().strftime('%Y-%m-%d')
        
        students = execute_query("SELECT username, user_id, role FROM users WHERE class = ? AND role IN ('student', 'monitor')", (class_name,))
        student_ids = [s['user_id'] for s in students]

        if student_ids:
            placeholders = ','.join('?' * len(student_ids))

            punched_records = execute_query(
                f"SELECT user_id FROM punch_records WHERE user_id IN ({placeholders}) AND punch_date = ?",
                student_ids + [today]
            )
            punched_user_ids = [r['user_id'] for r in punched_records]

            leave_records = execute_query(
                f"SELECT user_id FROM punch_records WHERE user_id IN ({placeholders}) AND ? BETWEEN leave_start_date AND leave_end_date AND leave_status = 'approved'",
                student_ids + [today]
            )
            leave_user_ids = [r['user_id'] for r in leave_records]
        else:
            punched_user_ids = []
            leave_user_ids = []
        
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
            
            # 确定打卡状态显示（已打卡优先于请假）
            punch_status = '已打卡' if punched else ('请假' if on_leave else '未打卡')
            
            class_records.append({
                'username': display_name,
                'user_id': student['user_id'],
                'role': student['role'],
                'punched': punched,
                'on_leave': on_leave,
                'punchTime': punch_status
            })
        
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
