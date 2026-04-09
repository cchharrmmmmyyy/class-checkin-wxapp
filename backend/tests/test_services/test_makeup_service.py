import pytest
from services.makeup_service import MakeupService
from utils.exceptions import ServiceException


class TestMakeupService:
    
    def test_apply_makeup_success(self, monkeypatch):
        """测试补卡申请成功"""
        # 模拟makeup_request_dao.get_by_user_and_date返回None（未申请过补卡）
        def mock_get_by_user_and_date(user_id, date):
            return None
        
        # 模拟makeup_request_dao.create返回申请ID
        def mock_create(user_id, date, reason):
            return 1
        
        # 模拟punch_dao.get_punch_by_user_and_date返回None（当日无打卡记录）
        def mock_get_punch_by_user_and_date(user_id, date):
            return None
        
        monkeypatch.setattr('services.makeup_service.makeup_request_dao.get_by_user_and_date', mock_get_by_user_and_date)
        monkeypatch.setattr('services.makeup_service.makeup_request_dao.create', mock_create)
        monkeypatch.setattr('services.makeup_service.punch_dao.get_punch_by_user_and_date', mock_get_punch_by_user_and_date)
        
        # 测试补卡申请 - 使用最近3天内的日期
        from datetime import datetime, timedelta
        recent_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        result = MakeupService.apply_makeup("2024001", recent_date, "忘记打卡")
        assert result["success"] is True
        assert result["message"] == "补卡申请提交成功，等待老师批准"
        assert result["data"]["punch_date"] == recent_date
        assert "request_id" in result["data"]
    
    def test_apply_makeup_missing_date(self):
        """测试补卡申请缺少日期"""
        # 测试缺少日期
        with pytest.raises(ServiceException) as excinfo:
            MakeupService.apply_makeup("2024001", None, "忘记打卡")
        assert "补卡日期不能为空" in str(excinfo.value)
    
    def test_apply_makeup_missing_reason(self):
        """测试补卡申请缺少原因"""
        # 测试缺少原因
        with pytest.raises(ServiceException) as excinfo:
            MakeupService.apply_makeup("2024001", "2024-01-10", None)
        assert "补卡原因不能为空" in str(excinfo.value)
    
    def test_apply_makeup_future_date(self):
        """测试补卡日期是未来日期"""
        # 测试未来日期
        with pytest.raises(ServiceException) as excinfo:
            MakeupService.apply_makeup("2024001", "2030-01-10", "忘记打卡")
        assert "补卡日期不能是未来日期" in str(excinfo.value)
    
    def test_apply_makeup_already_applied(self, monkeypatch):
        """测试该日期已经申请过补卡"""
        # 模拟makeup_request_dao.get_by_user_and_date返回已申请记录
        def mock_get_by_user_and_date(user_id, date):
            return {"id": 1, "user_id": user_id, "punch_date": date}
        
        # 模拟punch_dao.get_punch_by_user_and_date返回None（当日无打卡记录）
        def mock_get_punch_by_user_and_date(user_id, date):
            return None
        
        monkeypatch.setattr('services.makeup_service.makeup_request_dao.get_by_user_and_date', mock_get_by_user_and_date)
        monkeypatch.setattr('services.makeup_service.punch_dao.get_punch_by_user_and_date', mock_get_punch_by_user_and_date)
        
        # 测试已申请过补卡 - 使用最近3天内的日期
        from datetime import datetime, timedelta
        recent_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        with pytest.raises(ServiceException) as excinfo:
            MakeupService.apply_makeup("2024001", recent_date, "忘记打卡")
        assert "该日期已经申请过补卡" in str(excinfo.value)
    
    def test_get_user_makeup_records(self, monkeypatch):
        """测试获取用户补卡记录"""
        # 模拟makeup_request_dao.get_by_user返回记录
        def mock_get_by_user(user_id):
            return [
                {"id": 1, "user_id": user_id, "punch_date": "2024-01-10", "reason": "忘记打卡", "status": "pending", "created_at": "2024-01-11 10:00:00"},
                {"id": 2, "user_id": user_id, "punch_date": "2024-01-15", "reason": "生病请假", "status": "approved", "created_at": "2024-01-16 10:00:00"}
            ]
        
        monkeypatch.setattr('services.makeup_service.makeup_request_dao.get_by_user', mock_get_by_user)
        
        # 测试获取补卡记录
        records = MakeupService.get_user_makeup_records("2024001")
        assert len(records) == 2
        assert records[0]["id"] == 1
        assert records[0]["status"] == "pending"
    
    def test_get_pending_makeup_applications(self, monkeypatch):
        """测试获取待审批的补卡申请"""
        # 模拟makeup_request_dao.get_pending_by_class返回申请
        def mock_get_pending_by_class(class_name):
            return [
                {"id": 1, "username": "张三", "user_id": "2024001", "punch_date": "2024-01-10", "reason": "忘记打卡", "status": "pending", "created_at": "2024-01-11 10:00:00"},
                {"id": 2, "username": "李四", "user_id": "2024002", "punch_date": "2024-01-15", "reason": "生病请假", "status": "pending", "created_at": "2024-01-16 10:00:00"}
            ]
        
        monkeypatch.setattr('services.makeup_service.makeup_request_dao.get_pending_by_class', mock_get_pending_by_class)
        
        # 测试获取待审批申请
        applications = MakeupService.get_pending_makeup_applications("2024级计算机1班")
        assert len(applications) == 2
        assert applications[0]["username"] == "张三"
    
    def test_approve_makeup_success(self, monkeypatch):
        """测试审批补卡成功"""
        # 模拟makeup_request_dao.get_by_id_and_class返回申请
        def mock_get_by_id_and_class(request_id, class_name):
            return {
                "id": request_id,
                "user_id": "2024001",
                "punch_date": "2024-01-10",
                "status": "pending"
            }
        
        # 模拟makeup_request_dao.update_status返回成功
        def mock_update_status(request_id, status):
            return 1
        
        # 模拟PunchDAO.create_punch返回成功
        def mock_create_punch(user_id, date, time, lat, lng):
            return 1
        
        monkeypatch.setattr('services.makeup_service.makeup_request_dao.get_by_id_and_class', mock_get_by_id_and_class)
        monkeypatch.setattr('services.makeup_service.makeup_request_dao.update_status', mock_update_status)
        
        # 模拟dao.PunchDAO
        class MockPunchDAO:
            def create_punch(self, user_id, date, time, lat, lng, is_makeup=0):
                return 1
        
        monkeypatch.setattr('dao.PunchDAO', MockPunchDAO)
        
        # 模拟services.makeup_service.punch_dao.create_punch
        def mock_create_punch(user_id, date, time, lat, lng, is_makeup=0):
            return 1
        
        monkeypatch.setattr('services.makeup_service.punch_dao.create_punch', mock_create_punch)
        
        # 测试批准补卡
        result = MakeupService.approve_makeup(1, "2024级计算机1班", "approved")
        assert result["success"] is True
        assert result["message"] == "补卡审批成功"
        assert result["data"]["status"] == "approved"
    
    def test_approve_makeup_invalid_status(self):
        """测试审批状态无效"""
        # 测试无效状态
        with pytest.raises(ServiceException) as excinfo:
            MakeupService.approve_makeup(1, "2024级计算机1班", "invalid")
        assert "审批状态只能是approved或rejected" in str(excinfo.value)
    
    def test_approve_makeup_not_found(self, monkeypatch):
        """测试补卡申请不存在"""
        # 模拟makeup_request_dao.get_by_id_and_class返回None
        def mock_get_by_id_and_class(request_id, class_name):
            return None
        
        monkeypatch.setattr('services.makeup_service.makeup_request_dao.get_by_id_and_class', mock_get_by_id_and_class)
        
        # 测试申请不存在
        with pytest.raises(ServiceException) as excinfo:
            MakeupService.approve_makeup(1, "2024级计算机1班", "approved")
        assert "未找到该补卡申请或该申请不属于您的班级" in str(excinfo.value)
    
    def test_approve_makeup_already_processed(self, monkeypatch):
        """测试补卡申请已处理"""
        # 模拟makeup_request_dao.get_by_id_and_class返回已处理的申请
        def mock_get_by_id_and_class(request_id, class_name):
            return {
                "id": request_id,
                "user_id": "2024001",
                "status": "approved"
            }
        
        monkeypatch.setattr('services.makeup_service.makeup_request_dao.get_by_id_and_class', mock_get_by_id_and_class)
        
        # 测试已处理的申请
        with pytest.raises(ServiceException) as excinfo:
            MakeupService.approve_makeup(1, "2024级计算机1班", "approved")
        assert "该补卡申请已处于approved状态，无法重复审批" in str(excinfo.value)

    def test_apply_makeup_over_time_limit(self, monkeypatch):
        """测试超过补卡时限（3天）"""
        # 模拟makeup_request_dao.get_by_user_and_date返回None（未申请过补卡）
        def mock_get_by_user_and_date(user_id, date):
            return None
        
        # 模拟makeup_request_dao.create返回申请ID
        def mock_create(user_id, date, reason):
            return 1
        
        monkeypatch.setattr('services.makeup_service.makeup_request_dao.get_by_user_and_date', mock_get_by_user_and_date)
        monkeypatch.setattr('services.makeup_service.makeup_request_dao.create', mock_create)
        
        # 测试超过3天的补卡申请
        from datetime import datetime, timedelta
        past_date = (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d')
        
        with pytest.raises(ServiceException) as excinfo:
            MakeupService.apply_makeup("2024001", past_date, "忘记打卡")
        assert "只能补近3天的卡" in str(excinfo.value)

    def test_apply_makeup_with_existing_punch(self, monkeypatch):
        """测试当日已有打卡记录不能补卡"""
        # 模拟makeup_request_dao.get_by_user_and_date返回None（未申请过补卡）
        def mock_get_by_user_and_date(user_id, date):
            return None
        
        # 模拟makeup_request_dao.create返回申请ID
        def mock_create(user_id, date, reason):
            return 1
        
        # 模拟punch_dao.get_punch_by_user_and_date返回已有的打卡记录
        def mock_get_punch_by_user_and_date(user_id, date):
            return {"id": 1, "user_id": user_id, "punch_date": date}
        
        monkeypatch.setattr('services.makeup_service.makeup_request_dao.get_by_user_and_date', mock_get_by_user_and_date)
        monkeypatch.setattr('services.makeup_service.makeup_request_dao.create', mock_create)
        monkeypatch.setattr('services.makeup_service.punch_dao.get_punch_by_user_and_date', mock_get_punch_by_user_and_date)
        
        # 测试已有打卡记录的补卡申请 - 使用最近3天内的日期
        from datetime import datetime, timedelta
        recent_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        with pytest.raises(ServiceException) as excinfo:
            MakeupService.apply_makeup("2024001", recent_date, "忘记打卡")
        assert "当日已有打卡记录，不能补卡" in str(excinfo.value)
