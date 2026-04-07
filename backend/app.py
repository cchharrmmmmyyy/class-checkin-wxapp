from flask import Flask, jsonify, send_from_directory
from students import student_function
from teachers import teacher_function
from admin import admin_bp
from database import check_and_init_database
from login import login_function


app = Flask(__name__)

#注册蓝图
app.register_blueprint(student_function)
app.register_blueprint(teacher_function)
app.register_blueprint(admin_bp)
app.register_blueprint(login_function)


# 添加管理员页面路由
@app.route('/admin')
def admin_page():
    """管理员页面"""
    return send_from_directory('.', 'admin.html')

@app.route('/login')
def login_page():
    """管理员登录页面"""
    return send_from_directory('.', 'login.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'message': 'the server is running'})

if __name__ == '__main__':
    check_and_init_database()
    print("后端服务启动在 http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)