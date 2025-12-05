from flask import Blueprint, request, jsonify, send_from_directory
from database import get_db_connection, execute_query, execute_query_one

# 创建管理员蓝图
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# 管理员登录接口
@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """管理员登录验证"""
    try:
        # 获取请求数据
        data = request.get_json()
        user_name = data.get('username', '').strip()
        user_password = data.get('password', '').strip()
        
        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 执行查询
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND role = 'admin'",
            (user_name,)
        )
        
        # 获取查询结果
        admin = cursor.fetchone()
        conn.close()
        
        # 验证用户
        if admin and admin['password'] == user_password:
            return jsonify({
                'success': True,
                'message': '登录成功',
                'admin': {
                    'username': admin['username'],
                    'user_id': admin['user_id']
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
    except Exception as e:
        # 处理异常
        return jsonify({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }), 500

# 获取所有用户列表
@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    """获取所有用户信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users ORDER BY role, class, username")
        users = cursor.fetchall()
        conn.close()
        
        # 转换为字典列表
        user_list = []
        for user in users:
            user_list.append({
                'username': user['username'],
                'user_id': user['user_id'],
                'password': user['password'],
                'role': user['role'],
                'class': user['class']
            })
        
        return jsonify({
            'success': True,
            'data': user_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户列表失败: {str(e)}'
        }), 500

# 添加或修改用户
@admin_bp.route('/users', methods=['POST'])
def add_or_update_user():
    """添加新用户或修改现有用户"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        role = data.get('role', '').strip()
        class_name = data.get('class', '').strip()
        user_id = data.get('user_id', '').strip()
        
        # 验证必填字段
        if not username or not password or not role or not user_id:
            return jsonify({
                'success': False,
                'message': '用户名、密码、角色和用户ID不能为空'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查用户是否存在
        cursor.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )
        existing_user = cursor.fetchone()
        
        if existing_user:
            # 更新现有用户
            cursor.execute(
                "UPDATE users SET username = ?, password = ?, role = ?, class = ? WHERE user_id = ?",
                (username, password, role, class_name, user_id)
            )
            message = '用户更新成功'
        else:
            # 添加新用户
            cursor.execute(
                "INSERT INTO users (username, password, role, class, user_id) VALUES (?, ?, ?, ?, ?)",
                (username, password, role, class_name, user_id)
            )
            message = '用户添加成功'
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'操作失败: {str(e)}'
        }), 500

# 删除用户
@admin_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除指定用户"""
    try:
        # 不允许删除管理员账户
        if user_id == 'ADMIN001':
            return jsonify({
                'success': False,
                'message': '不允许删除管理员账户'
            }), 403
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM users WHERE user_id = ?",
            (user_id,)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '用户删除成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除用户失败: {str(e)}'
        }), 500

# 静态文件服务
@admin_bp.route('/admin.html')
def admin_page():
    """提供管理员HTML页面"""
    return send_from_directory('../', 'admin.html')
