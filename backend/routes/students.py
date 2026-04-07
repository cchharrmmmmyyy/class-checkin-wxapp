from flask import Blueprint, request, jsonify
from services import PunchService, LeaveService
from utils.auth import token_required, role_required

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
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        result = PunchService.punch(user_id, latitude, longitude)

        if not result.get('success'):
            status = 400
        else:
            status = 200

        return jsonify(result), status

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'打卡失败: {str(e)}'
        }), 500


@student_function.route('/records', methods=['GET'])
@token_required
def get_punch_records():
    try:
        user_id = request.user_info.get('user_id')
        records = PunchService.get_user_punch_records(user_id)
        return jsonify({
            'success': True,
            'message': '查询成功',
            'data': records
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
        leave_start_date = data.get('leave_start_date', '')
        leave_end_date = data.get('leave_end_date', '')

        if not leave_start_date or not leave_end_date:
            return jsonify({
                'success': False,
                'message': '请假开始和结束日期不能为空'
            }), 400

        result = LeaveService.apply_leave(user_id, leave_start_date, leave_end_date)

        if not result.get('success'):
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'请假申请失败: {str(e)}'
        }), 500


@student_function.route('/leave-records', methods=['GET'])
@token_required
def get_leave_records():
    try:
        user_id = request.user_info.get('user_id')
        records = LeaveService.get_user_leave_records(user_id)
        return jsonify({
            'success': True,
            'message': '查询成功',
            'data': records
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
        records = PunchService.get_class_punch_records(class_name)
        return jsonify({
            'success': True,
            'message': '查询成功',
            'data': records
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500
