"""AdminService 教学安排管理行为测试（拆前验证）。"""

import pytest
from services.admin_service import AdminService


class TestTeachingAssignment:
    """教学安排 CRUD。"""

    def test_list_assignments(self, seed_users):
        result = AdminService.list_teaching_assignments(page=1, size=20)
        assert result['total'] >= 1

    def test_filter_by_class(self, seed_users):
        result = AdminService.list_teaching_assignments(class_name='计算机2401', page=1, size=20)
        assert result['total'] >= 1
        assert all(a['class_name'] == '计算机2401' for a in result['items'])

    def test_create_assignment(self, seed_users):
        result = AdminService.create_teaching_assignment(
            class_name='计算机2401', teacher_id='T2024002', semester='2025-2026-1'
        )
        assert result['success'] is True

    def test_create_assignment_missing_fields_raises(self, seed_users):
        from utils.exceptions import ServiceException
        with pytest.raises(ServiceException):
            AdminService.create_teaching_assignment(class_name='', teacher_id='', semester=None)

    def test_update_assignment(self, seed_users):
        result = AdminService.update_teaching_assignment(
            class_name='计算机2401', teacher_id='T2024001', semester='2025-2026-2'
        )
        assert result['success'] is True

    def test_delete_assignment(self, seed_users):
        result = AdminService.delete_teaching_assignment(
            class_name='计算机2401', teacher_id='T2024001'
        )
        assert result['success'] is True

    def test_delete_nonexistent_assignment_raises(self, seed_users):
        from utils.exceptions import ServiceException
        with pytest.raises(ServiceException):
            AdminService.delete_teaching_assignment(class_name='计算机2401', teacher_id='T2099999')
