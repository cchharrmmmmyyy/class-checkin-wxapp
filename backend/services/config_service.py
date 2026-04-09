from dao import PunchConfigDAO
from utils.exceptions import ServiceException

# 创建DAO实例
punch_config_dao = PunchConfigDAO()


class ConfigService:

    @staticmethod
    def get_punch_config():
        """获取打卡配置"""
        config = punch_config_dao.get_config()
        if not config:
            # 返回默认配置
            return {
                'global_time_check_enabled': True,
                'global_location_check_enabled': True,
                'allow_multi_punch': False,
                'allow_makeup': True,
                'holiday_ranges': []
            }
        
        return {
            'global_time_check_enabled': config.global_time_check_enabled,
            'global_location_check_enabled': config.global_location_check_enabled,
            'allow_multi_punch': config.allow_multi_punch,
            'allow_makeup': config.allow_makeup,
            'holiday_ranges': config.holiday_ranges or [],
            'updated_at': config.updated_at
        }

    @staticmethod
    def update_punch_config(config_data):
        """更新打卡配置"""
        # 验证配置数据
        required_fields = ['global_time_check_enabled', 'global_location_check_enabled', 'allow_multi_punch', 'allow_makeup']
        for field in required_fields:
            if field not in config_data:
                raise ServiceException(f'缺少必要配置项: {field}', code=2001)
        
        # 验证数据类型
        for field in required_fields:
            if not isinstance(config_data[field], bool):
                raise ServiceException(f'配置项 {field} 必须是布尔值', code=2002)
        
        # 更新配置
        result = punch_config_dao.update(config_data)
        if not result:
            raise ServiceException('更新配置失败', code=2003)
        
        return {
            'success': True,
            'message': '配置更新成功',
            'data': ConfigService.get_punch_config()
        }

    @staticmethod
    def is_time_check_enabled():
        """检查是否启用时间验证"""
        config = ConfigService.get_punch_config()
        return config['global_time_check_enabled']

    @staticmethod
    def is_location_check_enabled():
        """检查是否启用位置验证"""
        config = ConfigService.get_punch_config()
        return config['global_location_check_enabled']

    @staticmethod
    def is_multi_punch_allowed():
        """检查是否允许多次打卡"""
        config = ConfigService.get_punch_config()
        return config['allow_multi_punch']

    @staticmethod
    def is_makeup_allowed():
        """检查是否允许补卡"""
        config = ConfigService.get_punch_config()
        return config['allow_makeup']

    @staticmethod
    def get_holiday_ranges():
        """获取假期范围"""
        config = ConfigService.get_punch_config()
        return config['holiday_ranges']

    @staticmethod
    def is_holiday(date):
        """检查指定日期是否为假期"""
        holiday_ranges = ConfigService.get_holiday_ranges()
        # 这里可以实现假期判断逻辑
        # 暂时返回False
        return False