from flask import Flask, jsonify, send_from_directory
from routes import admin_bp, student_function, teacher_function, login_function
from database import check_and_init_database
from config import Config


app = Flask(__name__)

app.register_blueprint(student_function)
app.register_blueprint(teacher_function)
app.register_blueprint(admin_bp)
app.register_blueprint(login_function)


@app.route('/admin')
def admin_page():
    return send_from_directory('.', 'admin.html')

@app.route('/login')
def login_page():
    return send_from_directory('.', 'login.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'the server is running'})

if __name__ == '__main__':
    check_and_init_database()
    print(f"后端服务启动在 http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)