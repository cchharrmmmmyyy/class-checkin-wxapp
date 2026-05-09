from flask import Flask, send_from_directory, request
from werkzeug.exceptions import HTTPException
from routes import (
    auth_bp, student_bp, teacher_bp,
    admin_user_bp, admin_org_bp, admin_teaching_bp,
    admin_rule_bp, admin_attendance_bp, admin_dashboard_bp,
    common_bp
)
from db import check_and_init_database
from config import Config
from utils.exceptions import ServiceException, AuthenticationException
from utils.api_response import error, success
from utils.jwt import decode_token
from utils.seed_data import insert_test_data


app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = Config.SECRET_KEY

app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(admin_user_bp)
app.register_blueprint(admin_org_bp)
app.register_blueprint(admin_teaching_bp)
app.register_blueprint(admin_rule_bp)
app.register_blueprint(admin_attendance_bp)
app.register_blueprint(admin_dashboard_bp)
app.register_blueprint(common_bp)

# 全局异常处理函数，拦截整个应用中未被手动捕获的异常，统一转换为 API 响应格式。
@app.errorhandler(AuthenticationException)# 处理认证异常
def handle_auth_exception(e):
    return error(message=e.message, code=e.code, http_status=e.http_status)


@app.errorhandler(ServiceException)# 处理服务异常
def handle_service_exception(e):
    return error(message=e.message, code=e.code, http_status=e.http_status)

# 拦截所有异常，包括 HTTPException，返回统一的错误响应。
@app.errorhandler(Exception)
def handle_generic_exception(e):
    if isinstance(e, HTTPException):
        return error(message=e.description, code=e.code, http_status=e.code)
    if Config.FLASK_DEBUG:
        return error(message=f'服务器内部错误: {str(e)}', code=500, http_status=500)
    return error(message='服务器内部错误', code=500, http_status=500)


@app.route('/admin')
def admin_page():
    token = request.cookies.get('token')
    if token:
        payload = decode_token(token)
        if payload and payload.get('role') == 'admin':
            return send_from_directory('templates', 'admin.html')
    return send_from_directory('templates', 'login.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    return success({'status': 'ok'})


@app.route('/<path:path>')
def fallback(path):
    if path.startswith('api/'):
        return error(message='接口不存在', code=404, http_status=404)
    return send_from_directory('templates', 'login.html')


check_and_init_database()

if Config.INSERT_TEST_DATA:
    insert_test_data()

if __name__ == '__main__':
    print(f"后端服务启动在 http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)
