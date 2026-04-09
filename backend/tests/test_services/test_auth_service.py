import pytest
from services.auth_service import AuthService
from utils.exceptions import ServiceException


class TestAuthService:
    
    def test_login_success(self, monkeypatch):
        """测试登录成功"""
        # 模拟verify_password函数
        def mock_verify_password(password, stored_hash):
            return password == "123456"
        
        # 模拟user_dao.get_by_id返回用户数据
        def mock_get_by_id(user_id):
            class MockUser:
                def __init__(self):
                    self.user_id = "2024001"
                    self.username = "张三"
                    self.password = "hashed_password"
                    self.role = "student"
                    self.class_name = "2024级计算机1班"
                    self.is_first_login = 0
                    self.login_fail_count = 0
                    self.lock_until = None
            return MockUser()
        
        # 模拟execute_update
        def mock_execute_update(sql, params):
            return 1
        
        monkeypatch.setattr('services.auth_service.user_dao.get_by_id', mock_get_by_id)
        monkeypatch.setattr('services.auth_service.execute_update', mock_execute_update)
        monkeypatch.setattr('services.auth_service.verify_password', mock_verify_password)
        
        # 测试登录
        result = AuthService.login("2024001", "123456")
        assert "token" in result
        assert result["user"]["user_id"] == "2024001"
        assert result["user"]["username"] == "张三"
        assert result["user"]["role"] == "student"
        assert result["redirect_url"] == "/pages/student/student"
    
    def test_login_failure(self, monkeypatch):
        """测试登录失败"""
        # 模拟user_dao.get_by_id返回用户数据
        def mock_get_by_id(user_id):
            class MockUser:
                def __init__(self):
                    self.user_id = "2024001"
                    self.username = "张三"
                    self.password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # 123456
                    self.role = "student"
                    self.class_name = "2024级计算机1班"
                    self.is_first_login = 0
                    self.login_fail_count = 0
                    self.lock_until = None
            return MockUser()
        
        # 模拟execute_update
        def mock_execute_update(sql, params):
            return 1
        
        monkeypatch.setattr('services.auth_service.user_dao.get_by_id', mock_get_by_id)
        monkeypatch.setattr('services.auth_service.execute_update', mock_execute_update)
        
        # 测试密码错误
        with pytest.raises(ServiceException) as excinfo:
            AuthService.login("2024001", "wrong_password")
        assert "学号/工号或密码错误" in str(excinfo.value)
    
    def test_login_locked(self, monkeypatch):
        """测试账户被锁定"""
        from datetime import datetime, timedelta
        
        # 模拟user_dao.get_by_id返回锁定的用户
        def mock_get_by_id(user_id):
            class MockUser:
                def __init__(self):
                    self.user_id = "2024001"
                    self.username = "张三"
                    self.password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # 123456
                    self.role = "student"
                    self.class_name = "2024级计算机1班"
                    self.is_first_login = 0
                    self.login_fail_count = 5
                    self.lock_until = datetime.now() + timedelta(hours=1)
            return MockUser()
        
        monkeypatch.setattr('services.auth_service.user_dao.get_by_id', mock_get_by_id)
        
        # 测试账户锁定
        with pytest.raises(ServiceException) as excinfo:
            AuthService.login("2024001", "123456")
        assert "账户已被锁定" in str(excinfo.value)
    
    def test_reset_password(self, monkeypatch):
        """测试重置密码"""
        # 模拟execute_update
        def mock_execute_update(sql, params):
            return 1
        
        monkeypatch.setattr('services.auth_service.execute_update', mock_execute_update)
        
        # 测试重置密码
        result = AuthService.reset_password("2024001", "new_password")
        assert result is True