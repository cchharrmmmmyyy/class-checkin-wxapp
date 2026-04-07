from flask import Blueprint, request, jsonify
from datetime import datetime
from dao import user_dao, punch_record_dao, location_dao, leave_dao
from utils.geo import calculate_distance
from utils.auth import token_required, role_required
from config import Config

student_function = Blueprint('student', __name__, url_prefix='/api/students')


@student_function.route('/profile', methods=['GET'])
@token_required
def get_profile():
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
def submit_punch():
    try:
        user_id = request.user_info.get('user_id')
        role = request.user_info.get('role')
        class_name = request.user_info.get('class', '暂无班级')
        data = request.get_json()
        print(f"收到打卡请求数据: {data}")
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        print(f"用户信息: user_id={user_id}, role={role}, class={class_name}, lat={latitude}, lng={longitude}")

        punch_location = location_dao.get_enabled_punch_location()
        if punch_location and latitude is not None and longitude is not None:
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

        existing_record = punch_record_dao.get_punch_record_by_user_and_date(user_id, today)

        if existing_record:
            print(f"用户 {user_id} 今日已打卡")
            return jsonify({
                'success': False,
                'message': '今日已打卡',
                'already_punched': True
            }), 400

        punch_record_dao.create_punch_record(user_id, today)
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
def get_punch_records():
    user_id = request.user_info.get('user_id')

    try:
        records = punch_record_dao.get_punch_records_by_user(user_id, Config.PUNCH_RECORDS_LIMIT)

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
def apply_leave():
    try:
        user_id = request.user_info.get('user_id')

        data = request.get_json()
        print(f"收到请假申请数据: {data}")

        leave_start_date = data.get('leave_start_date', '')
        leave_end_date = data.get('leave_end_date', '')

        if not user_id or not leave_start_date or not leave_end_date or leave_start_date == 'null' or leave_end_date == 'null' or leave_start_date == 'undefined' or leave_end_date == 'undefined':
            return jsonify({
                'success': False,
                'message': '用户ID、请假开始和结束日期不能为空'
            }), 400

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

        leave_dao.create_leave_record(user_id, leave_start_date, leave_end_date)

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
def get_leave_records():
    user_id = request.user_info.get('user_id')

    try:
        records = leave_dao.get_leave_records_by_user(user_id)

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
    try:
        today = datetime.now().strftime('%Y-%m-%d')

        students = user_dao.get_users_by_class(class_name)
        student_ids = [s['user_id'] for s in students]

        if student_ids:
            punched_user_ids = punch_record_dao.get_punch_user_ids_for_date(student_ids, today)
            leave_user_ids = punch_record_dao.get_leave_user_ids_for_date(student_ids, today)
        else:
            punched_user_ids = []
            leave_user_ids = []

        class_records = []
        for student in students:
            punched = student['user_id'] in punched_user_ids
            on_leave = student['user_id'] in leave_user_ids

            display_name = student['username']
            if student['role'] == 'monitor':
                display_name = student['username'] + ' (班委)'

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
