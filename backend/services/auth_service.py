from datetime import datetime, timedelta
from utils.password import verify_password, hash_password
from utils.db import execute_update
from dao import UserDAO, ClassTeacherDAO
from utils.jwt import generate_token
from utils.exceptions import ServiceException
from utils import error_codes as EC

user_dao = UserDAO()
class_teacher_dao = ClassTeacherDAO()


class AuthService:

    @staticmethod
    def login(user_id, password, ip=None):
        user = user_dao.get_by_id(user_id)
        if not user:
            verify_password(password, 'dummy_hash')
            raise ServiceException('学号/工号或密码错误', code=EC.AUTH_CREDENTIALS_INVALID, http_status=401)

        if user.lock_until and datetime.now() < user.lock_until:
            raise ServiceException('账户已被锁定，请稍后再试', code=EC.AUTH_ACCOUNT_LOCKED, http_status=423)

        if not verify_password(password, user.password):
            fail_count = user.login_fail_count + 1
            lock_until = None

            if fail_count >= 5:
                lock_until = datetime.now() + timedelta(hours=1)

            execute_update(
                "UPDATE users SET login_fail_count = ?, lock_until = ? WHERE user_id = ?",
                (fail_count, lock_until, user_id)
            )

            raise ServiceException('学号/工号或密码错误', code=EC.AUTH_CREDENTIALS_INVALID, http_status=401)

        execute_update(
            "UPDATE users SET login_fail_count = 0, lock_until = NULL, last_login_time = CURRENT_TIMESTAMP, last_login_ip = ? WHERE user_id = ?",
            (ip, user_id)
        )

        user_role = user.role
        user_class = user.class_name
        username = user.username

        if user_role == 'teacher' and not user_class:
            teacher_classes = class_teacher_dao.get_list(
                where="teacher_id = ? AND deleted_at IS NULL",
                params=(user_id,)
            )
            if teacher_classes:
                user_class = teacher_classes[0].class_name

        token = generate_token(user_id, username, user_role, user_class)

        if user_role == 'student':
            redirect_url = '/pages/student/index/index'
        elif user_role == 'teacher':
            redirect_url = '/pages/teacher/classes/classes'
        elif user_role == 'monitor':
            redirect_url = '/pages/student/index/index'
        elif user_role == 'admin':
            redirect_url = '/admin'
        else:
            raise ServiceException(f'未知的用户角色: {user_role}', code=EC.AUTH_ROLE_UNKNOWN)

        return {
            'token': token,
            'user': {
                'username': username,
                'user_id': user_id,
                'role': user_role,
                'class_name': user_class,
                'is_first_login': user.is_first_login
            },
            'redirect_url': redirect_url
        }

    @staticmethod
    def reset_password(user_id, new_password):
        result = execute_update(
            "UPDATE users SET password = ?, is_first_login = 0 WHERE user_id = ?",
            (hash_password(new_password), user_id)
        )
        return result > 0

    @staticmethod
    def change_password(user_id, old_password, new_password):
        user = user_dao.get_by_id(user_id)
        if not user:
            raise ServiceException('用户不存在', code=EC.AUTH_USER_NOT_FOUND, http_status=404)

        if not verify_password(old_password, user.password):
            raise ServiceException('原密码错误', code=EC.AUTH_OLD_PASSWORD_WRONG, http_status=401)

        if len(new_password) < 6 or len(new_password) > 20:
            raise ServiceException('新密码长度必须在6-20个字符之间', code=EC.AUTH_PASSWORD_LENGTH_INVALID)

        execute_update(
            "UPDATE users SET password = ?, is_first_login = 0 WHERE user_id = ?",
            (hash_password(new_password), user_id)
        )

        return {'success': True, 'message': '密码修改成功'}
