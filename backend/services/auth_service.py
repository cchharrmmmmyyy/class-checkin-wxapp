from datetime import datetime
from db_connection import verify_password
from dao import user_dao
from utils.auth import generate_token


class AuthService:

    @staticmethod
    def login(user_id, password):
        user = user_dao.get_user_by_id(user_id)
        if not user or not verify_password(password, user['password']):
            return None

        user_role = user['role']
        user_class = user['class']
        username = user['username']

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
            raise ValueError(f'未知的用户角色: {user_role}')

        return {
            'token': token,
            'user': {
                'username': username,
                'user_id': user_id,
                'role': user_role,
                'class': user_class
            },
            'redirect_url': redirect_url
        }
