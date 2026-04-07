from flask import Flask, jsonify, send_from_directory
from routes import admin_bp, student_function, teacher_function, login_function
from database import check_and_init_database


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
    print("后端服务启动在 http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)