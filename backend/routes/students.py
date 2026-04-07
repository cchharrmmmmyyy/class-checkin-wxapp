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
    user_id = request.user_info.get('user_id')
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    return jsonify(PunchService.punch(user_id, latitude, longitude)), 200


@student_function.route('/records', methods=['GET'])
@token_required
def get_punch_records():
    user_id = request.user_info.get('user_id')
    records = PunchService.get_user_punch_records(user_id)
    return jsonify({
        'success': True,
        'message': '查询成功',
        'data': records
    }), 200


@student_function.route('/apply-leave', methods=['POST'])
@token_required
@role_required('student', 'monitor')
def apply_leave():
    user_id = request.user_info.get('user_id')
    data = request.get_json()
    leave_start_date = data.get('leave_start_date', '')
    leave_end_date = data.get('leave_end_date', '')

    return jsonify(LeaveService.apply_leave(user_id, leave_start_date, leave_end_date)), 200


@student_function.route('/leave-records', methods=['GET'])
@token_required
def get_leave_records():
    user_id = request.user_info.get('user_id')
    records = LeaveService.get_user_leave_records(user_id)
    return jsonify({
        'success': True,
        'message': '查询成功',
        'data': records
    }), 200


@student_function.route('/class-records/<class_name>', methods=['GET'])
@token_required
@role_required('monitor', 'teacher')
def get_class_punch_records(class_name):
    records = PunchService.get_class_punch_records(class_name)
    return jsonify({
        'success': True,
        'message': '查询成功',
        'data': records
    }), 200
