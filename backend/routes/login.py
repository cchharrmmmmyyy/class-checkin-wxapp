from flask import Blueprint, jsonify, request
from database import execute_query_one, verify_password
from utils.auth import generate_token

login_function = Blueprint('login', __name__, url_prefix='/api')

@login_function.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user_id = data.get('user_id', '').strip()
        password = data.get('password', '').strip()

        if not user_id or not password:
            return jsonify({
                'success': False,
                'message': '学号/工号和密码不能为空'
            }), 400

        if len(user_id) < 6 or len(user_id) > 12:
            return jsonify({
                'success': False,
                'message': '账户/密码错误'
            }), 400

        if len(password) < 6 or len(password) > 20:
            return jsonify({
                'success': False,
                'message': '账户/密码错误'
            }), 400

        sql = "SELECT username, user_id, password, role, class FROM users WHERE user_id = ?"
        user = execute_query_one(sql, (user_id,))

        if user and verify_password(password, user['password']):
            user_role = user['role']
            user_class = user['class']
            username = user['username']

            token = generate_token(user_id, username, user_role, user_class)

            if user_role == 'student':
                redirect_url = '/pages/student/student'
            elif user_role == 'teacher':
                redirect_url = '/pages/teacher/teacher'
            elif user_role == 'monitor':
                redirect_url = '/pages/student/student'
            elif user_role == 'admin':
                redirect_url = '/admin'
            else:
                raise ValueError(f'未知的用户角色: {user_role}')

            return jsonify({
                'success': True,
                'message': '登录成功',
                'token': token,
                'user': {
                    'username': username,
                    'user_id': user_id,
                    'role': user_role,
                    'class': user_class
                },
                'redirect_url': redirect_url
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '学号/工号或密码错误'
            }), 401

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }), 500