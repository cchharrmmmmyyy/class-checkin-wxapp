import uuid
from flask import Flask, jsonify, send_from_directory, request, g, redirect
from werkzeug.exceptions import HTTPException
from routes import auth_bp, student_bp, teacher_bp, admin_bp, common_bp, compat_bp
from db import check_and_init_database
from config import Config
from utils.exceptions import ServiceException
from utils.api_response import error, success


app = Flask(__name__, static_folder='static', static_url_path='/static')

app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(common_bp)
app.register_blueprint(compat_bp)


@app.before_request
def assign_trace_id():
    # 优先透传上游请求的 trace_id，便于链路串联
    g.trace_id = request.headers.get('X-Trace-Id') or str(uuid.uuid4())


@app.after_request
def normalize_response(response):
    if response.is_json:
        body = response.get_json(silent=True)
        if isinstance(body, dict) and 'code' in body and 'message' in body:
            if 'data' not in body:
                body['data'] = None
            if 'trace_id' not in body and getattr(g, 'trace_id', None):
                body['trace_id'] = g.trace_id
            response.set_data(app.json.dumps(body))

    response.headers['X-Trace-Id'] = getattr(g, 'trace_id', '')
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


@app.errorhandler(ServiceException)
def handle_service_exception(e):
    return error(e.message, e.code, e.http_status)


@app.errorhandler(Exception)
def handle_generic_exception(e):
    if isinstance(e, HTTPException):
        return error(e.description, e.code, e.code)
    return error(f'服务器内部错误: {str(e)}', 500, 500)


@app.route('/')
def index():
    return send_from_directory('templates', 'login.html')


@app.route('/admin')
def admin_page():
    token = request.args.get('token') or request.cookies.get('adminToken')
    if not token:
        return redirect('/login?reason=missing_token')

    try:
        from utils.auth import decode_token
        payload = decode_token(token)
        if not payload:
            response = redirect('/login?reason=token_invalid')
            response.delete_cookie('adminToken')
            return response
        if payload.get('role') != 'admin':
            response = redirect('/login?reason=permission_denied')
            response.delete_cookie('adminToken')
            return response
    except Exception:
        response = redirect('/login?reason=token_invalid')
        response.delete_cookie('adminToken')
        return response

    response = send_from_directory('templates', 'admin.html')
    response.set_cookie('adminToken', token, httponly=True)
    return response


@app.route('/login')
def login_page():
    return send_from_directory('templates', 'login.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    return success({'status': 'ok'})


if __name__ == '__main__':
    check_and_init_database()
    print(f"后端服务启动在 http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)
