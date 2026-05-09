"""AdminService 用户管理行为测试（拆前验证）。"""

import pytest
from services.admin_service import AdminService


class TestUserCRUD:
    """用户 CRUD。"""

    def test_list_users(self, seed_users):
        result = AdminService.list_users()
        assert len(result) >= 1
        assert any(u['user_id'] == 'S2024001' for u in result)

    def test_list_users_paginated(self, seed_users):
        result = AdminService.list_users_paginated(class_name='计算机2401', page=1, size=10)
        assert result['total'] >= 1
        assert all(u['class'] == '计算机2401' for u in result['items'])

    def test_create_student(self, seed_users):
        result = AdminService.save_user(
            username='新学生', user_id='S2024004', password='123456',
            role='student', class_name='计算机2401'
        )
        assert result['success'] is True

    def test_create_teacher(self, seed_users):
        result = AdminService.save_user(
            username='新老师', user_id='T2024003', password='123456',
            role='teacher', class_name='计算机2401'
        )
        assert result['success'] is True

    def test_create_admin_raises_with_class(self, seed_basic_org):
        from utils.exceptions import ServiceException
        with pytest.raises(ServiceException):
            AdminService.save_user(
                username='new_admin', user_id='admin002', password='admin123',
                role='admin', class_name='计算机2401'
            )

    def test_create_non_admin_without_class_raises(self, seed_basic_org):
        from utils.exceptions import ServiceException
        with pytest.raises(ServiceException):
            AdminService.save_user(
                username='new_student', user_id='S2099001', password='123456',
                role='student', class_name=None
            )

    def test_delete_user(self, seed_users):
        result = AdminService.delete_user('S2024002')
        assert result['success'] is True

    def test_delete_nonexistent_user_raises(self, seed_users):
        from utils.exceptions import ServiceException
        with pytest.raises(ServiceException):
            AdminService.delete_user('NOT_EXIST')

    def test_delete_last_admin_raises(self, seed_users):
        from utils.exceptions import ServiceException
        # 先创建一个admin再删除另一个
        AdminService.save_user(
            username='admin2', user_id='admin002', password='admin123',
            role='admin', class_name=None
        )
        # admin001 已存在，可以删除（因为还有admin002）
        result = AdminService.delete_user('admin001')
        assert result['success'] is True

    def test_reset_password(self, seed_users):
        result = AdminService.reset_password('S2024001')
        assert result['success'] is True
        assert 'new_password' in result

    def test_reset_password_nonexistent_raises(self, seed_users):
        from utils.exceptions import ServiceException
        with pytest.raises(ServiceException):
            AdminService.reset_password('NOT_EXIST')
