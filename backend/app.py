from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 导入学生模块
from student import student_function

# 导入教师模块
from teacher import teacher_function

# 导入管理员模块
from admin import admin_bp

# 导入数据库模块
from database import init_database, execute_query_one, get_db_connection

# 注册学生蓝图
#什么是蓝图？
"""
蓝图（Blueprint）是Flask中用于组织路由和视图函数的工具，
相当于一个"路由集合"。它允许你将不同功能模块的路由分开管理，
使代码结构更清晰、易于维护。
"""
app.register_blueprint(student_function)

# 注册教师蓝图
app.register_blueprint(teacher_function)

# 注册管理员蓝图
app.register_blueprint(admin_bp)

# 添加管理员页面路由
@app.route('/admin')
def admin_page():
    """管理员页面"""
    return send_from_directory('.', 'admin.html')

# 检查并初始化数据库，只在需要时初始化
def check_and_init_database():
    """检查并初始化数据库，只在需要时初始化"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone() is None:#获取查询结果的第一行，如果没有结果则返回 None
            init_database()  # 调用真正的初始化函数
        else:
            # 检查punch_records表是否有leave_status字段
            cursor.execute("PRAGMA table_info(punch_records)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]# 提取所有列名到列表
            
            if 'leave_status' not in column_names:
                print("更新数据库表结构")
                init_database()  # 调用初始化函数，添加leave_status字段
            else:
                print("数据库已存在且结构完整，无需初始化")
    finally:
        conn.close()


@app.route('/api/login', methods=['POST'])
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
        
        # 查询数据库验证用户（只支持学号/工号查询）
        sql = "SELECT username, user_id, password, role, class FROM users WHERE user_id = ?"
        user = execute_query_one(sql, (user_id,))
        
        # 验证用户
        if user and user['password'] == password:
            user_role = user['role']
            user_class = user['class']
            
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
                'user': {
                    'username': user['username'],
                    'user_id': user['user_id'],
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



@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'message': '后端服务运行正常'})

if __name__ == '__main__':
    check_and_init_database()
    print("后端服务启动在 http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)