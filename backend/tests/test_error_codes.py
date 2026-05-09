"""测试 utils/error_codes.py 错误码常量。"""

import pytest


class TestErrorCodesExist:
    """验证所有业务领域错误码常量存在且值合法。"""

    def _get_module(self):
        from utils import error_codes
        return error_codes

    def _get_constants(self, module):
        return {
            name: value
            for name, value in vars(module).items()
            if name.isupper() and isinstance(value, int)
        }

    def test_codes_are_unique(self):
        module = self._get_module()
        constants = self._get_constants(module)
        values = list(constants.values())
        assert len(values) == len(set(values)), "错误码值不唯一"

    def test_all_code_ranges_valid(self):
        module = self._get_module()
        constants = self._get_constants(module)
        for name, value in constants.items():
            assert 0 <= value <= 9999, f"{name}={value} 超出有效范围 0-9999"

    def test_auth_codes_in_1000_range(self):
        module = self._get_module()
        auth_names = [n for n in dir(module) if n.startswith('AUTH_')]
        for name in auth_names:
            value = getattr(module, name)
            assert 1000 <= value <= 1999, f"{name}={value} 不在 1000-1999 范围内"

    def test_punch_codes_in_3000_range(self):
        module = self._get_module()
        punch_names = [n for n in dir(module) if n.startswith('PUNCH_')]
        for name in punch_names:
            value = getattr(module, name)
            assert 3000 <= value <= 3999, f"{name}={value} 不在 3000-3999 范围内"

    def test_leave_codes_in_4000_range(self):
        module = self._get_module()
        leave_names = [n for n in dir(module) if n.startswith('LEAVE_')]
        for name in leave_names:
            value = getattr(module, name)
            assert 4000 <= value <= 4999, f"{name}={value} 不在 4000-4999 范围内"

    def test_makeup_codes_in_5000_range(self):
        module = self._get_module()
        makeup_names = [n for n in dir(module) if n.startswith('MAKEUP_')]
        for name in makeup_names:
            value = getattr(module, name)
            assert 5000 <= value <= 5999, f"{name}={value} 不在 5000-5999 范围内"

    def test_user_codes_in_6000_range(self):
        module = self._get_module()
        user_names = [n for n in dir(module) if n.startswith('USER_')]
        for name in user_names:
            value = getattr(module, name)
            assert 6000 <= value <= 6999, f"{name}={value} 不在 6000-6999 范围内"

    def test_class_codes_in_7000_range(self):
        module = self._get_module()
        class_names = [n for n in dir(module) if n.startswith(('CLASS_', 'CAMPUS_', 'DEPT_', 'MAJOR_', 'GRADE_'))]
        for name in class_names:
            value = getattr(module, name)
            assert 7000 <= value <= 7999, f"{name}={value} 不在 7000-7999 范围内"

    def test_notification_codes_in_8000_range(self):
        module = self._get_module()
        notif_names = [n for n in dir(module) if n.startswith('NOTIFICATION_')]
        for name in notif_names:
            value = getattr(module, name)
            assert 8000 <= value <= 8999, f"{name}={value} 不在 8000-8999 范围内"

    def test_log_codes_in_9000_range(self):
        module = self._get_module()
        log_names = [n for n in dir(module) if n.startswith('LOG_') or n.startswith('ADMIN_')]
        for name in log_names:
            value = getattr(module, name)
            assert 9000 <= value <= 9999, f"{name}={value} 不在 9000-9999 范围内"
