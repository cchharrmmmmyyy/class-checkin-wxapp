import pytest
from services.config_service import ConfigService
from utils.exceptions import ServiceException


class TestConfigService:
    
    def test_get_punch_config(self, monkeypatch):
        """测试获取打卡配置"""
        # 模拟punch_config_dao.get_config返回配置数据
        def mock_get_config():
            class MockConfig:
                def __init__(self):
                    self.id = 1
                    self.global_time_check_enabled = True
                    self.global_location_check_enabled = True
                    self.allow_multi_punch = False
                    self.allow_makeup = True
                    self.holiday_ranges = []
                    self.updated_at = None
            return MockConfig()
        
        monkeypatch.setattr('services.config_service.punch_config_dao.get_config', mock_get_config)
        
        # 测试获取配置
        config = ConfigService.get_punch_config()
        assert config['global_time_check_enabled'] is True
        assert config['global_location_check_enabled'] is True
        assert config['allow_multi_punch'] is False
        assert config['allow_makeup'] is True
        assert config['holiday_ranges'] == []
    
    def test_get_punch_config_default(self, monkeypatch):
        """测试获取默认打卡配置"""
        # 模拟punch_config_dao.get_config返回None
        def mock_get_config():
            return None
        
        monkeypatch.setattr('services.config_service.punch_config_dao.get_config', mock_get_config)
        
        # 测试获取默认配置
        config = ConfigService.get_punch_config()
        assert config['global_time_check_enabled'] is True
        assert config['global_location_check_enabled'] is True
        assert config['allow_multi_punch'] is False
        assert config['allow_makeup'] is True
        assert config['holiday_ranges'] == []

    def test_get_punch_config_holiday_ranges_json_string(self, monkeypatch):
        """测试 holiday_ranges 为 JSON 字符串时能正确返回数组"""
        def mock_get_config():
            class MockConfig:
                def __init__(self):
                    self.id = 1
                    self.global_time_check_enabled = True
                    self.global_location_check_enabled = True
                    self.allow_multi_punch = False
                    self.allow_makeup = True
                    self.holiday_ranges = '[["2026-01-01","2026-01-03"]]'
                    self.updated_at = None
            return MockConfig()

        monkeypatch.setattr('services.config_service.punch_config_dao.get_config', mock_get_config)
        config = ConfigService.get_punch_config()
        assert config['holiday_ranges'] == [["2026-01-01", "2026-01-03"]]
    
    def test_update_punch_config(self, monkeypatch):
        """测试更新打卡配置"""
        captured = {}

        def mock_update(data):
            captured.update(data)
            return True
        
        # 模拟punch_config_dao.get_config返回更新后的配置
        def mock_get_config():
            class MockConfig:
                def __init__(self):
                    self.id = 1
                    self.global_time_check_enabled = False
                    self.global_location_check_enabled = False
                    self.allow_multi_punch = True
                    self.allow_makeup = False
                    self.holiday_ranges = []
                    self.updated_at = None
            return MockConfig()
        
        monkeypatch.setattr('services.config_service.punch_config_dao.update', mock_update)
        monkeypatch.setattr('services.config_service.punch_config_dao.get_config', mock_get_config)
        
        # 测试更新配置
        config_data = {
            'global_time_check_enabled': False,
            'global_location_check_enabled': False,
            'allow_multi_punch': True,
            'allow_makeup': False,
            'holiday_ranges': [["2026-01-01", "2026-01-03"]]
        }
        result = ConfigService.update_punch_config(config_data)
        assert result['success'] is True
        assert result['message'] == '配置更新成功'
        assert result['data']['global_time_check_enabled'] is False
        assert isinstance(captured.get('holiday_ranges'), str)
        assert captured.get('holiday_ranges') == '[["2026-01-01", "2026-01-03"]]'
    
    def test_update_punch_config_missing_fields(self):
        """测试更新打卡配置缺少必要字段"""
        # 测试缺少必要字段
        config_data = {
            'global_time_check_enabled': False
            # 缺少其他必要字段
        }
        with pytest.raises(ServiceException) as excinfo:
            ConfigService.update_punch_config(config_data)
        assert "缺少必要配置项" in str(excinfo.value)
    
    def test_update_punch_config_invalid_type(self):
        """测试更新打卡配置数据类型错误"""
        # 测试数据类型错误
        config_data = {
            'global_time_check_enabled': "false",  # 应该是布尔值
            'global_location_check_enabled': True,
            'allow_multi_punch': True,
            'allow_makeup': False
        }
        with pytest.raises(ServiceException) as excinfo:
            ConfigService.update_punch_config(config_data)
        assert "必须是布尔值" in str(excinfo.value)

    def test_update_punch_config_accepts_int_bool(self, monkeypatch):
        """测试更新打卡配置兼容 0/1"""
        captured = {}

        def mock_update(data):
            captured.update(data)
            return True

        def mock_get_config():
            class MockConfig:
                def __init__(self):
                    self.id = 1
                    self.global_time_check_enabled = 1
                    self.global_location_check_enabled = 0
                    self.allow_multi_punch = 0
                    self.allow_makeup = 1
                    self.holiday_ranges = '[]'
                    self.updated_at = None
            return MockConfig()

        monkeypatch.setattr('services.config_service.punch_config_dao.update', mock_update)
        monkeypatch.setattr('services.config_service.punch_config_dao.get_config', mock_get_config)

        result = ConfigService.update_punch_config({
            'global_time_check_enabled': 1,
            'global_location_check_enabled': 0,
            'allow_multi_punch': 0,
            'allow_makeup': 1
        })
        assert result['success'] is True
        assert captured['global_time_check_enabled'] is True
        assert captured['global_location_check_enabled'] is False
    
    def test_is_time_check_enabled(self, monkeypatch):
        """测试检查是否启用时间验证"""
        # 模拟get_punch_config返回配置
        def mock_get_punch_config():
            return {
                'global_time_check_enabled': True
            }
        
        monkeypatch.setattr('services.config_service.ConfigService.get_punch_config', mock_get_punch_config)
        
        # 测试时间验证
        assert ConfigService.is_time_check_enabled() is True
    
    def test_is_location_check_enabled(self, monkeypatch):
        """测试检查是否启用位置验证"""
        # 模拟get_punch_config返回配置
        def mock_get_punch_config():
            return {
                'global_location_check_enabled': True
            }
        
        monkeypatch.setattr('services.config_service.ConfigService.get_punch_config', mock_get_punch_config)
        
        # 测试位置验证
        assert ConfigService.is_location_check_enabled() is True
    
    def test_is_multi_punch_allowed(self, monkeypatch):
        """测试检查是否允许多次打卡"""
        # 模拟get_punch_config返回配置
        def mock_get_punch_config():
            return {
                'allow_multi_punch': False
            }
        
        monkeypatch.setattr('services.config_service.ConfigService.get_punch_config', mock_get_punch_config)
        
        # 测试多次打卡
        assert ConfigService.is_multi_punch_allowed() is False
    
    def test_is_makeup_allowed(self, monkeypatch):
        """测试检查是否允许补卡"""
        # 模拟get_punch_config返回配置
        def mock_get_punch_config():
            return {
                'allow_makeup': True
            }
        
        monkeypatch.setattr('services.config_service.ConfigService.get_punch_config', mock_get_punch_config)
        
        # 测试补卡
        assert ConfigService.is_makeup_allowed() is True
    
    def test_get_holiday_ranges(self, monkeypatch):
        """测试获取假期范围"""
        # 模拟get_punch_config返回配置
        def mock_get_punch_config():
            return {
                'holiday_ranges': ['2024-01-01', '2024-02-10']
            }
        
        monkeypatch.setattr('services.config_service.ConfigService.get_punch_config', mock_get_punch_config)
        
        # 测试假期范围
        assert ConfigService.get_holiday_ranges() == ['2024-01-01', '2024-02-10']
    
    def test_is_holiday(self, monkeypatch):
        """测试检查指定日期是否为假期"""
        # 模拟get_holiday_ranges方法
        def mock_get_holiday_ranges():
            return []
        
        monkeypatch.setattr('services.config_service.ConfigService.get_holiday_ranges', mock_get_holiday_ranges)
        
        # 测试假期判断（暂时返回False）
        assert ConfigService.is_holiday('2024-01-01') is False
