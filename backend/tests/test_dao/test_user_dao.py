import pytest
from utils.db import hash_password, verify_password


class TestUserDAO:
    def test_get_by_id(self, user_dao):
        user = user_dao.get_by_id('admin001')
        assert user is not None
        assert user.user_id == 'admin001'
        assert user.username == 'admin'
        assert user.real_name == '超级管理员'
        assert user.role == 'admin'

    def test_get_by_id_not_found(self, user_dao):
        user = user_dao.get_by_id('nonexistent')
        assert user is None

    def test_get_list(self, user_dao):
        users = user_dao.get_list()
        assert len(users) >= 8
        assert all(u.role in ['admin', 'teacher', 'student', 'monitor'] for u in users)

    def test_get_list_with_where(self, user_dao):
        users = user_dao.get_list(where='role = ?', params=('teacher',))
        assert len(users) == 2
        assert all(u.role == 'teacher' for u in users)

    def test_get_list_with_limit(self, user_dao):
        users = user_dao.get_list(limit=3)
        assert len(users) == 3

    def test_get_list_with_order_by(self, user_dao):
        users = user_dao.get_list(order_by='user_id DESC', limit=3)
        assert len(users) == 3

    def test_create(self, user_dao):
        data = {
            'user_id': 'test_user_001',
            'username': 'test_user',
            'password': 'test_password',
            'real_name': '测试用户',
            'role': 'student',
            'class_name': '计算机2401',
            'student_id': '2024999',
            'phone': '13900000000',
            'email': 'test@test.com'
        }
        result = user_dao.create(data)
        assert result == 'test_user_001'

        user = user_dao.get_by_id('test_user_001')
        assert user is not None
        assert user.username == 'test_user'
        assert user.real_name == '测试用户'
        assert verify_password('test_password', user.password)

    def test_update(self, user_dao):
        user = user_dao.get_by_id('S2024001')
        original_name = user.real_name

        result = user_dao.update('S2024001', {'real_name': '张三改'})
        assert result is True

        user = user_dao.get_by_id('S2024001')
        assert user.real_name == '张三改'

        user_dao.update('S2024001', {'real_name': original_name})

    def test_update_password(self, user_dao):
        data = {
            'user_id': 'test_pwd_user',
            'username': 'test_pwd',
            'password': 'original_password',
            'real_name': '密码测试',
            'role': 'student'
        }
        user_dao.create(data)

        user = user_dao.get_by_id('test_pwd_user')
        assert verify_password('original_password', user.password)

        user_dao.update('test_pwd_user', {'password': 'new_password'})
        user = user_dao.get_by_id('test_pwd_user')
        assert verify_password('new_password', user.password)
        assert not verify_password('original_password', user.password)

    def test_delete(self, user_dao, temp_db):
        data = {
            'user_id': 'test_delete_user',
            'username': 'test_delete',
            'password': 'password',
            'real_name': '删除测试',
            'role': 'student'
        }
        user_dao.create(data)

        result = user_dao.delete('test_delete_user')
        assert result is True

        import sqlite3
        conn = sqlite3.connect(temp_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = 'test_delete_user'")
        row = cursor.fetchone()
        conn.close()
        assert row is not None
        assert row['deleted_at'] is not None

    def test_get_by_username(self, user_dao):
        user = user_dao.get_by_username('admin')
        assert user is not None
        assert user.username == 'admin'

    def test_get_by_username_not_found(self, user_dao):
        user = user_dao.get_by_username('nonexistent_user')
        assert user is None

    def test_get_by_username_excludes_deleted(self, user_dao):
        data = {
            'user_id': 'test_deleted_user',
            'username': 'test_deleted',
            'password': 'password',
            'real_name': '已删除用户',
            'role': 'student'
        }
        user_dao.create(data)
        user_dao.delete('test_deleted_user')

        user = user_dao.get_by_username('test_deleted')
        assert user is None

    def test_get_by_student_id(self, user_dao):
        user = user_dao.get_by_student_id('2024001')
        assert user is not None
        assert user.student_id == '2024001'

    def test_get_by_student_id_not_found(self, user_dao):
        user = user_dao.get_by_student_id('nonexistent')
        assert user is None

    def test_get_list_by_class(self, user_dao):
        users = user_dao.get_list(where='class_name = ?', params=('计算机2401',))
        assert len(users) >= 3
        assert all(u.class_name == '计算机2401' for u in users)

    def test_update_no_fields(self, user_dao):
        result = user_dao.update('S2024001', {})
        assert result is False
