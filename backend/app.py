from flask import Flask, jsonify, send_from_directory
from routes import admin_bp, student_function, teacher_function, login_function
from init_db import check_and_init_database
from config import Config
from utils.auth import role_required, web_token_required
from utils.exceptions import ServiceException


app = Flask(__name__)

app.register_blueprint(student_function)
app.register_blueprint(teacher_function)
app.register_blueprint(admin_bp)
app.register_blueprint(login_function)


@app.errorhandler(ServiceException)
def handle_service_exception(e):
    return jsonify({'success': False, 'message': e.message, 'code': e.code}), e.http_status


@app.errorhandler(Exception)
def handle_generic_exception(e):
    return jsonify({'success': False, 'message': f'服务器内部错误: {str(e)}'}), 500


@app.route('/admin')
@web_token_required
@role_required('admin')
def admin_page():
    return send_from_directory('templates', 'admin.html')


@app.route('/login')
def login_page():
    return send_from_directory('templates', 'login.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'the server is running'})


if __name__ == '__main__':
    check_and_init_database()
    print(f"后端服务启动在 http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)
