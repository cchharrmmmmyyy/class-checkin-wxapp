from datetime import datetime, timedelta
from db_connection import verify_password, execute_update
from dao import UserDAO
from utils.auth import generate_token
from utils.exceptions import ServiceException

# 创建DAO实例
user_dao = UserDAO()


class AuthService:

    @staticmethod
    def login(user_id, password, ip=None):
        # 获取用户信息
        user = user_dao.get_by_id(user_id)
        if not user:
            # 模拟验证时间，防止暴力破解
            verify_password(password, 'dummy_hash')
            raise ServiceException('学号/工号或密码错误', code=1001, http_status=401)

        # 检查账户是否被锁定
        if user.lock_until and datetime.now() < user.lock_until:
            raise ServiceException('账户已被锁定，请稍后再试', code=1003, http_status=423)

        # 验证密码
        if not verify_password(password, user.password):
            # 增加登录失败次数
            fail_count = user.login_fail_count + 1
            lock_until = None
            
            # 连续失败5次，锁定账户1小时
            if fail_count >= 5:
                lock_until = datetime.now() + timedelta(hours=1)
            
            # 更新登录失败信息
            execute_update(
                "UPDATE users SET login_fail_count = ?, lock_until = ? WHERE user_id = ?",
                (fail_count, lock_until, user_id)
            )
            
            raise ServiceException('学号/工号或密码错误', code=1001, http_status=401)

        # 登录成功，重置登录失败信息
        execute_update(
            "UPDATE users SET login_fail_count = 0, lock_until = NULL, last_login_time = CURRENT_TIMESTAMP, last_login_ip = ? WHERE user_id = ?",
            (ip, user_id)
        )

        user_role = user.role
        user_class = user.class_name
        username = user.username

        token = generate_token(user_id, username, user_role, user_class)

        if user_role == 'student':
            redirect_url = '/pages/student/student'
        elif user_role == 'teacher':
            redirect_url = '/pages/teacher/teacher'
        elif user_role == 'monitor':
            redirect_url = '/pages/student/student'
        elif user_role == 'admin':
            redirect_url = '/admin'
        else:
            raise ServiceException(f'未知的用户角色: {user_role}', code=1002)

        return {
            'token': token,
            'user': {
                'username': username,
                'user_id': user_id,
                'role': user_role,
                'class': user_class,
                'is_first_login': user.is_first_login
            },
            'redirect_url': redirect_url
        }

    @staticmethod
    def reset_password(user_id, new_password):
        """重置密码"""
        from db_connection import hash_password
        result = execute_update(
            "UPDATE users SET password = ?, is_first_login = 0 WHERE user_id = ?",
            (hash_password(new_password), user_id)
        )
        return result > 0

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """修改密码"""
        from db_connection import verify_password, hash_password

        user = user_dao.get_by_id(user_id)
        if not user:
            raise ServiceException('用户不存在', code=1004, http_status=404)

        if not verify_password(old_password, user.password):
            raise ServiceException('原密码错误', code=1005, http_status=401)

        if len(new_password) < 6 or len(new_password) > 20:
            raise ServiceException('新密码长度必须在6-20个字符之间', code=1006)

        execute_update(
            "UPDATE users SET password = ?, is_first_login = 0 WHERE user_id = ?",
            (hash_password(new_password), user_id)
        )

        return {'success': True, 'message': '密码修改成功'}
