"""AdminService 打卡规则管理行为测试（拆前验证）。"""

import pytest
from services.admin_service import AdminService


class TestTimeSlotCRUD:
    """时间段 CRUD。"""

    def test_create_time_slot(self, seed_basic_org):
        result = AdminService.save_time_slot(slot_id=None, name='晚自习', start_time='19:00', end_time='21:00')
        assert result['success'] is True
        assert 'id' in result

    def test_create_time_slot_missing_fields_raises(self, seed_basic_org):
        from utils.exceptions import ServiceException
        with pytest.raises(ServiceException):
            AdminService.save_time_slot(slot_id=None, name='', start_time='', end_time='')

    def test_list_time_slots(self, seed_basic_org):
        result = AdminService.list_time_slots(page=1, size=20)
        assert 'items' in result

    def test_delete_time_slot(self, seed_basic_org):
        slot_id = AdminService.save_time_slot(slot_id=None, name='测试时段', start_time='10:00', end_time='11:00')['id']
        result = AdminService.delete_time_slot(slot_id)
        assert result['success'] is True


class TestGeofenceCRUD:
    """打卡围栏 CRUD。"""

    def test_create_circle_geofence(self, seed_basic_org):
        result = AdminService.save_geofence(
            geofence_id=None, name='测试围栏', fence_type='circle',
            latitude=39.9, longitude=116.3, radius=100
        )
        assert result['success'] is True

    def test_create_geofence_missing_name_raises(self, seed_basic_org):
        from utils.exceptions import ServiceException
        with pytest.raises(ServiceException):
            AdminService.save_geofence(geofence_id=None, name='', fence_type='circle')

    def test_list_geofences(self, seed_basic_org):
        result = AdminService.list_geofences(page=1, size=20)
        assert 'items' in result

    def test_delete_geofence(self, seed_basic_org):
        result = AdminService.save_geofence(
            geofence_id=None, name='待删除围栏', fence_type='circle',
            latitude=39.9, longitude=116.3, radius=100
        )
        fence_id = result['id']
        del_result = AdminService.delete_geofence(fence_id)
        assert del_result['success'] is True


class TestRuleCRUD:
    """打卡规则 CRUD。"""

    def test_create_punch_rule(self, seed_geofences, seed_time_slots):
        result = AdminService.save_punch_rule(
            rule_id=None, time_slot_id=1, geofence_id=1, priority=50
        )
        assert result['success'] is True

    def test_create_rule_missing_refs_raises(self, seed_basic_org):
        from utils.exceptions import ServiceException
        with pytest.raises(ServiceException):
            AdminService.save_punch_rule(rule_id=None, time_slot_id=None, geofence_id=None)

    def test_list_punch_rules(self, seed_geofences, seed_time_slots):
        from services.admin_service import AdminService
        result = AdminService.list_punch_rules(page=1, size=20)
        assert 'items' in result

    def test_delete_punch_rule(self, seed_geofences, seed_time_slots):
        rule_id = AdminService.save_punch_rule(
            rule_id=None, time_slot_id=1, geofence_id=1, priority=50
        )['id']
        result = AdminService.delete_punch_rule(rule_id)
        assert result['success'] is True
