from dao import PunchConfigDAO
from utils.exceptions import ServiceException
from utils import error_codes as EC
import json

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

        holiday_ranges = []
        raw_holiday_ranges = getattr(config, 'holiday_ranges', None)
        if isinstance(raw_holiday_ranges, list):
            holiday_ranges = raw_holiday_ranges
        elif isinstance(raw_holiday_ranges, str):
            s = raw_holiday_ranges.strip()
            if s:
                try:
                    decoded = json.loads(s)
                    if isinstance(decoded, list):
                        holiday_ranges = decoded
                except Exception:
                    holiday_ranges = []

        return {
            'global_time_check_enabled': bool(config.global_time_check_enabled),
            'global_location_check_enabled': bool(config.global_location_check_enabled),
            'allow_multi_punch': bool(config.allow_multi_punch),
            'allow_makeup': bool(config.allow_makeup),
            'holiday_ranges': holiday_ranges,
            'updated_at': config.updated_at
        }

    @staticmethod
    def update_punch_config(config_data):
        """更新打卡配置"""
        # 验证配置数据
        required_fields = ['global_time_check_enabled', 'global_location_check_enabled', 'allow_multi_punch', 'allow_makeup']
        for field in required_fields:
            if field not in config_data:
                raise ServiceException(f'缺少必要配置项: {field}', code=EC.JSON_INVALID)
        
        # 验证数据类型（兼容 0/1）
        normalized_bools = {}
        for field in required_fields:
            val = config_data[field]
            if isinstance(val, bool):
                normalized_bools[field] = val
            elif isinstance(val, int) and val in (0, 1):
                normalized_bools[field] = bool(val)
            else:
                raise ServiceException(f'配置项 {field} 必须是布尔值', code=EC.JSON_INVALID)

        payload = dict(normalized_bools)
        if 'holiday_ranges' in config_data:
            holiday_ranges = config_data.get('holiday_ranges')
            if holiday_ranges is None:
                payload['holiday_ranges'] = None
            elif isinstance(holiday_ranges, list):
                payload['holiday_ranges'] = json.dumps(holiday_ranges, ensure_ascii=False)
            elif isinstance(holiday_ranges, str):
                s = holiday_ranges.strip()
                if not s:
                    payload['holiday_ranges'] = '[]'
                else:
                    try:
                        decoded = json.loads(s)
                    except Exception as e:
                        raise ServiceException('holiday_ranges 必须是数组或合法的 JSON 字符串', code=EC.JSON_INVALID) from e
                    if not isinstance(decoded, list):
                        raise ServiceException('holiday_ranges 必须是数组或合法的 JSON 字符串', code=EC.JSON_INVALID)
                    payload['holiday_ranges'] = s
            else:
                raise ServiceException('holiday_ranges 必须是数组或合法的 JSON 字符串', code=EC.JSON_INVALID)

        # 更新配置
        result = punch_config_dao.update(payload)
        if not result:
            raise ServiceException('更新配置失败', code=EC.JSON_INVALID)
        
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
