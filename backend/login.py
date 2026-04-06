"""
登录模块
负责处理用户登录请求，验证学号/工号和密码,生成JWT令牌并返回重定向路由
"""

from flask import Blueprint,jsonify
from flask import request
from database import  execute_query_one, verify_password
from utils.auth import generate_token



login_function = Blueprint('login', __name__, url_prefix='/api')
@login_function.route('/login', methods=['POST'])
def login():
    """
    登录接口
    接收学号/工号和密码，验证后返回登录结果和重定向路由
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', '').strip()
        password = data.get('password', '').strip()
        
        # 验证输入
        if not user_id or not password:
            return jsonify({
                'success': False,
                'message': '学号/工号和密码不能为空'
            }), 400
        
        if (len(user_id) < 6 or len(user_id) > 12):#不过多暴露学号/工号长度，一定程度防止爆破
            return jsonify({
                'success': False,
                'message': '账户/密码错误'
            }), 400
        
        if (len(password) < 6 or len(password) > 20):
            return jsonify({
                'success': False,
                'message': '账户/密码错误'
            }), 400
        
        # 查询数据库验证用户（只支持学号/工号查询），防止SQL注入，使用参数化查询
        sql = "SELECT username, user_id, password, role, class FROM users WHERE user_id = ?"
        user = execute_query_one(sql, (user_id,))
        
        # 验证用户 - 使用哈希密码验证
        if user and verify_password(password, user['password']):
            user_role = user['role']
            user_class = user['class']
            username = user['username']
            
            # 生成JWT令牌
            token = generate_token(user_id, username, user_role, user_class)
            
            # 根据用户角色决定重定向路由
            if user_role == 'student':
                redirect_url = '/pages/student/student'
            elif user_role == 'teacher':
                redirect_url = '/pages/teacher/teacher'
            elif user_role == 'monitor':
                redirect_url = '/pages/student/student'  # 班委也重定向到学生页面
            else:
                # 遇到未知角色，抛出异常
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
   