from flask import Blueprint, jsonify, request
from services import AuthService

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

        result = AuthService.login(user_id, password)

        if not result:
            return jsonify({
                'success': False,
                'message': '学号/工号或密码错误'
            }), 401

        return jsonify({
            'success': True,
            'message': '登录成功',
            'token': result['token'],
            'user': result['user'],
            'redirect_url': result['redirect_url']
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }), 500
