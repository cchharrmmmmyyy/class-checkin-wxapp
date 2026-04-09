from flask import Flask, jsonify, send_from_directory, make_response
from routes import auth_bp, student_bp, teacher_bp, admin_bp, common_bp
from db import check_and_init_database
from config import Config
from utils.auth import role_required, web_token_required
from utils.exceptions import ServiceException


app = Flask(__name__)

app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(common_bp)


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


@app.errorhandler(ServiceException)
def handle_service_exception(e):
    return jsonify({'code': e.code, 'message': e.message}), e.http_status


@app.errorhandler(Exception)
def handle_generic_exception(e):
    return jsonify({'code': 500, 'message': f'服务器内部错误: {str(e)}'}), 500


@app.route('/admin')
@web_token_required
@role_required(['admin'])
def admin_page():
    return send_from_directory('templates', 'admin.html')


@app.route('/login')
def login_page():
    return send_from_directory('templates', 'login.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'code': 200, 'message': 'success', 'data': {'status': 'ok'}})


if __name__ == '__main__':
    check_and_init_database()
    print(f"后端服务启动在 http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)