from flask import Flask, send_from_directory, request
from werkzeug.exceptions import HTTPException
from routes import auth_bp, student_bp, teacher_bp, admin_bp, common_bp
from db import check_and_init_database
from config import Config
from utils.exceptions import ServiceException
from utils.api_response import error, success
from utils.jwt import decode_token


app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = Config.SECRET_KEY

app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(common_bp)


@app.errorhandler(ServiceException)
def handle_service_exception(e):
    return error(e.message, e.code, e.http_status)


@app.errorhandler(Exception)
def handle_generic_exception(e):
    if isinstance(e, HTTPException):
        return error(e.description, e.code, e.code)
    if Config.FLASK_DEBUG:
        return error(f'服务器内部错误: {str(e)}', 500, 500)
    return error('服务器内部错误', 500, 500)


@app.route('/admin')
def admin_page():
    token = request.cookies.get('adminToken')
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
        return error('接口不存在', 404, 404)
    return send_from_directory('templates', 'login.html')


check_and_init_database()

if __name__ == '__main__':
    print(f"后端服务启动在 http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)
