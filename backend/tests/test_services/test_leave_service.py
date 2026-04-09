import pytest
from services.leave_service import LeaveService
from utils.exceptions import ServiceException


class TestLeaveService:
    
    def test_apply_leave_success(self, monkeypatch):
        """测试请假申请成功"""
        # 模拟leave_dao.create_leave_record返回成功
        def mock_create_leave_record(user_id, start_date, end_date):
            return 1
        
        # 模拟leave_dao.get_leave_records_by_user返回空列表（无请假记录）
        def mock_get_leave_records_by_user(user_id):
            return []
        
        monkeypatch.setattr('services.leave_service.leave_dao.create_leave_record', mock_create_leave_record)
        monkeypatch.setattr('services.leave_service.leave_dao.get_leave_records_by_user', mock_get_leave_records_by_user)
        
        # 测试请假申请 - 使用未来日期
        result = LeaveService.apply_leave("2024001", "2027-01-10", "2027-01-12")
        assert result["success"] is True
        assert result["message"] == "请假申请提交成功，等待老师批准"
        assert result["data"]["leave_start_date"] == "2027-01-10"
        assert result["data"]["leave_end_date"] == "2027-01-12"
    
    def test_apply_leave_missing_dates(self):
        """测试请假申请缺少日期"""
        # 测试缺少开始日期
        with pytest.raises(ServiceException) as excinfo:
            LeaveService.apply_leave("2024001", None, "2024-01-12")
        assert "请假开始和结束日期不能为空" in str(excinfo.value)
        
        # 测试缺少结束日期
        with pytest.raises(ServiceException) as excinfo:
            LeaveService.apply_leave("2024001", "2024-01-10", None)
        assert "请假开始和结束日期不能为空" in str(excinfo.value)
    
    def test_apply_leave_past_date(self):
        """测试请假开始日期是过去日期"""
        # 测试过去日期
        with pytest.raises(ServiceException) as excinfo:
            LeaveService.apply_leave("2024001", "2023-01-10", "2023-01-12")
        assert "请假开始日期不能是过去日期" in str(excinfo.value)
    
    def test_apply_leave_end_before_start(self):
        """测试请假结束日期早于开始日期"""
        # 测试结束日期早于开始日期
        with pytest.raises(ServiceException) as excinfo:
            LeaveService.apply_leave("2024001", "2024-01-12", "2024-01-10")
        assert "请假结束日期不能早于开始日期" in str(excinfo.value)
    
    def test_get_user_leave_records(self, monkeypatch):
        """测试获取用户请假记录"""
        # 模拟leave_dao.get_leave_records_by_user返回记录
        def mock_get_leave_records_by_user(user_id):
            return [
                {"id": 1, "user_id": user_id, "username": "张三", "leave_start_date": "2024-01-10", "leave_end_date": "2024-01-12", "leave_status": "pending"},
                {"id": 2, "user_id": user_id, "username": "张三", "leave_start_date": "2024-02-01", "leave_end_date": "2024-02-03", "leave_status": "approved"}
            ]
        
        monkeypatch.setattr('services.leave_service.leave_dao.get_leave_records_by_user', mock_get_leave_records_by_user)
        
        # 测试获取请假记录
        records = LeaveService.get_user_leave_records("2024001")
        assert len(records) == 2
        assert records[0]["id"] == 1
        assert records[0]["leave_status"] == "pending"
    
    def test_get_pending_applications(self, monkeypatch):
        """测试获取待审批的请假申请"""
        # 模拟leave_dao.get_pending_leave_applications_by_class返回申请
        def mock_get_pending_leave_applications_by_class(class_name):
            return [
                {"id": 1, "username": "张三", "user_id": "2024001", "leave_start_date": "2024-01-10", "leave_end_date": "2024-01-12", "leave_status": "pending"},
                {"id": 2, "username": "李四", "user_id": "2024002", "leave_start_date": "2024-01-15", "leave_end_date": "2024-01-17", "leave_status": "pending"}
            ]
        
        monkeypatch.setattr('services.leave_service.leave_dao.get_pending_leave_applications_by_class', mock_get_pending_leave_applications_by_class)
        
        # 测试获取待审批申请
        applications = LeaveService.get_pending_applications("2024级计算机1班")
        assert len(applications) == 2
        assert applications[0]["username"] == "张三"
    
    def test_approve_leave_success(self, monkeypatch):
        """测试审批请假成功"""
        # 模拟leave_dao.get_leave_record_by_id_and_class返回申请
        def mock_get_leave_record_by_id_and_class(leave_id, class_name):
            return {
                "id": leave_id,
                "user_id": "2024001",
                "leave_status": "pending"
            }
        
        # 模拟leave_dao.update_leave_status返回成功
        def mock_update_leave_status(leave_id, status):
            return 1
        
        monkeypatch.setattr('services.leave_service.leave_dao.get_leave_record_by_id_and_class', mock_get_leave_record_by_id_and_class)
        monkeypatch.setattr('services.leave_service.leave_dao.update_leave_status', mock_update_leave_status)
        
        # 测试批准请假
        result = LeaveService.approve_leave(1, "2024级计算机1班", "approved")
        assert result["success"] is True
        assert result["message"] == "请假审批成功"
        assert result["data"]["status"] == "approved"
    
    def test_approve_leave_invalid_status(self):
        """测试审批状态无效"""
        # 测试无效状态
        with pytest.raises(ServiceException) as excinfo:
            LeaveService.approve_leave(1, "2024级计算机1班", "invalid")
        assert "审批状态只能是approved或rejected" in str(excinfo.value)
    
    def test_approve_leave_not_found(self, monkeypatch):
        """测试请假申请不存在"""
        # 模拟leave_dao.get_leave_record_by_id_and_class返回None
        def mock_get_leave_record_by_id_and_class(leave_id, class_name):
            return None
        
        monkeypatch.setattr('services.leave_service.leave_dao.get_leave_record_by_id_and_class', mock_get_leave_record_by_id_and_class)
        
        # 测试申请不存在
        with pytest.raises(ServiceException) as excinfo:
            LeaveService.approve_leave(1, "2024级计算机1班", "approved")
        assert "未找到该请假申请或该申请不属于您的班级" in str(excinfo.value)
    
    def test_approve_leave_already_processed(self, monkeypatch):
        """测试请假申请已处理"""
        # 模拟leave_dao.get_leave_record_by_id_and_class返回已处理的申请
        def mock_get_leave_record_by_id_and_class(leave_id, class_name):
            return {
                "id": leave_id,
                "user_id": "2024001",
                "leave_status": "approved"
            }
        
        monkeypatch.setattr('services.leave_service.leave_dao.get_leave_record_by_id_and_class', mock_get_leave_record_by_id_and_class)
        
        # 测试已处理的申请
        with pytest.raises(ServiceException) as excinfo:
            LeaveService.approve_leave(1, "2024级计算机1班", "approved")
        assert "该请假申请已处于approved状态，无法重复审批" in str(excinfo.value)

    def test_apply_leave_overlap(self, monkeypatch):
        """测试请假天数重叠检测"""
        # 模拟leave_dao.create_leave_record返回成功
        def mock_create_leave_record(user_id, start_date, end_date):
            return 1
        
        # 模拟leave_dao.get_leave_records_by_user返回已有的请假记录
        def mock_get_leave_records_by_user(user_id):
            return [{
                "id": 1,
                "user_id": user_id,
                "leave_start_date": "2027-01-10",
                "leave_end_date": "2027-01-12",
                "leave_status": "approved"
            }]
        
        monkeypatch.setattr('services.leave_service.leave_dao.create_leave_record', mock_create_leave_record)
        monkeypatch.setattr('services.leave_service.leave_dao.get_leave_records_by_user', mock_get_leave_records_by_user)
        
        # 测试申请重叠的请假
        with pytest.raises(ServiceException) as excinfo:
            LeaveService.apply_leave("2024001", "2027-01-11", "2027-01-13")
        assert "该时间段内已存在请假记录" in str(excinfo.value)
