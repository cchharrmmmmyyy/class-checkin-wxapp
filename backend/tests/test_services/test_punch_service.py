import pytest
from services.punch_service import PunchService
from utils.exceptions import ServiceException


class TestPunchService:
    
    def test_punch_success(self, monkeypatch):
        """测试打卡成功"""
        # 模拟punch_geofence_dao.get_enabled_geofences返回空列表（无位置限制）
        def mock_get_enabled_geofences():
            return []
        
        # 模拟punch_dao.get_punch_by_user_and_date返回None（今日未打卡）
        def mock_get_punch_by_user_and_date(user_id, date):
            return None
        
        # 模拟punch_dao.create_punch返回打卡ID
        def mock_create_punch(user_id, date, time, lat, lng, is_makeup=0):
            return 1
        
        # 模拟leave_dao.get_leave_records_by_user返回空列表（无请假记录）
        def mock_get_leave_records_by_user(user_id):
            return []
        
        monkeypatch.setattr('services.punch_service.punch_geofence_dao.get_enabled_geofences', mock_get_enabled_geofences)
        monkeypatch.setattr('services.punch_service.punch_dao.get_punch_by_user_and_date', mock_get_punch_by_user_and_date)
        monkeypatch.setattr('services.punch_service.punch_dao.create_punch', mock_create_punch)
        monkeypatch.setattr('services.punch_service.leave_dao.get_leave_records_by_user', mock_get_leave_records_by_user)
        
        # 测试打卡
        result = PunchService.punch("2024001", 39.9042, 116.4074)
        assert result["success"] is True
        assert result["message"] == "打卡成功"
        assert "punch_id" in result["data"]
    
    def test_punch_out_of_range(self, monkeypatch):
        """测试打卡不在范围内"""
        # 模拟punch_geofence_dao.get_enabled_geofences返回围栏
        def mock_get_enabled_geofences():
            return [{
                'latitude': 39.9042,
                'longitude': 116.4074,
                'radius': 100  # 100米范围
            }]
        
        # 模拟calculate_distance返回大于围栏范围的距离
        def mock_calculate_distance(lat1, lng1, lat2, lng2):
            return 200  # 200米，超出范围
        
        monkeypatch.setattr('services.punch_service.punch_geofence_dao.get_enabled_geofences', mock_get_enabled_geofences)
        monkeypatch.setattr('services.punch_service.calculate_distance', mock_calculate_distance)
        
        # 测试打卡失败（不在范围内）
        with pytest.raises(ServiceException) as excinfo:
            PunchService.punch("2024001", 39.9052, 116.4084)  # 稍微偏移的位置
        assert "不在打卡范围内" in str(excinfo.value)
    
    def test_punch_no_location(self, monkeypatch):
        """测试无位置信息"""
        # 模拟punch_geofence_dao.get_enabled_geofences返回围栏
        def mock_get_enabled_geofences():
            return [{
                'latitude': 39.9042,
                'longitude': 116.4074,
                'radius': 100
            }]
        
        monkeypatch.setattr('services.punch_service.punch_geofence_dao.get_enabled_geofences', mock_get_enabled_geofences)
        
        # 测试打卡失败（无位置信息）
        with pytest.raises(ServiceException) as excinfo:
            PunchService.punch("2024001", None, None)
        assert "无法获取您的位置" in str(excinfo.value)
    
    def test_punch_already_punched(self, monkeypatch):
        """测试今日已打卡"""
        # 模拟punch_geofence_dao.get_enabled_geofences返回空列表
        def mock_get_enabled_geofences():
            return []
        
        # 模拟punch_dao.get_punch_by_user_and_date返回已打卡记录
        def mock_get_punch_by_user_and_date(user_id, date):
            return {"id": 1, "user_id": user_id, "punch_date": date}
        
        # 模拟leave_dao.get_leave_records_by_user返回空列表（无请假记录）
        def mock_get_leave_records_by_user(user_id):
            return []
        
        monkeypatch.setattr('services.punch_service.punch_geofence_dao.get_enabled_geofences', mock_get_enabled_geofences)
        monkeypatch.setattr('services.punch_service.punch_dao.get_punch_by_user_and_date', mock_get_punch_by_user_and_date)
        monkeypatch.setattr('services.punch_service.leave_dao.get_leave_records_by_user', mock_get_leave_records_by_user)
        
        # 测试打卡失败（今日已打卡）
        with pytest.raises(ServiceException) as excinfo:
            PunchService.punch("2024001", 39.9042, 116.4074)
        assert "今日已打卡" in str(excinfo.value)
    
    def test_get_user_punch_records(self, monkeypatch):
        """测试获取用户打卡记录"""
        # 模拟punch_dao.get_punches_by_user返回记录
        def mock_get_punches_by_user(user_id, limit):
            return [
                {"id": 1, "user_id": user_id, "punch_date": "2024-01-01", "punch_time": "08:00:00"},
                {"id": 2, "user_id": user_id, "punch_date": "2024-01-02", "punch_time": "08:30:00"}
            ]
        
        monkeypatch.setattr('services.punch_service.punch_dao.get_punches_by_user', mock_get_punches_by_user)
        
        # 测试获取打卡记录
        records = PunchService.get_user_punch_records("2024001")
        assert len(records) == 2
        assert records[0]["id"] == 1
        assert records[0]["punch_date"] == "2024-01-01"
    
    def test_get_class_punch_records(self):
        """测试获取班级打卡记录"""
        # 测试获取班级打卡记录（暂时返回空列表）
        records = PunchService.get_class_punch_records("2024级计算机1班")
        assert isinstance(records, list)

    def test_punch_with_leave(self, monkeypatch):
        """测试请假期间不允许打卡"""
        from datetime import datetime
        # 模拟punch_geofence_dao.get_enabled_geofences返回空列表
        def mock_get_enabled_geofences():
            return []
        
        # 模拟punch_dao.get_punch_by_user_and_date返回None（今日未打卡）
        def mock_get_punch_by_user_and_date(user_id, date):
            return None
        
        # 模拟leave_dao.get_leave_records_by_user返回已批准的请假记录
        def mock_get_leave_records_by_user(user_id):
            today = datetime.now().strftime('%Y-%m-%d')
            return [{
                "id": 1,
                "user_id": user_id,
                "leave_start_date": today,
                "leave_end_date": today,
                "leave_status": "approved"
            }]
        
        # 模拟punch_dao.create_punch返回打卡ID
        def mock_create_punch(user_id, date, time, lat, lng, is_makeup=0):
            return 1
        
        monkeypatch.setattr('services.punch_service.punch_geofence_dao.get_enabled_geofences', mock_get_enabled_geofences)
        monkeypatch.setattr('services.punch_service.punch_dao.get_punch_by_user_and_date', mock_get_punch_by_user_and_date)
        monkeypatch.setattr('services.punch_service.punch_dao.create_punch', mock_create_punch)
        monkeypatch.setattr('services.punch_service.leave_dao.get_leave_records_by_user', mock_get_leave_records_by_user)
        
        # 测试请假期间打卡
        with pytest.raises(ServiceException) as excinfo:
            PunchService.punch("2024001", 39.9042, 116.4074)
        assert "请假期间不允许打卡" in str(excinfo.value)
