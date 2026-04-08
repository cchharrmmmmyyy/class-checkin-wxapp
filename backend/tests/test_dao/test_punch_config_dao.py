import pytest


class TestPunchConfigDAO:
    def test_get_config(self, punch_config_dao):
        config = punch_config_dao.get_config()
        assert config is not None
        assert config.id == 1
        assert config.global_time_check_enabled == 1
        assert config.global_location_check_enabled == 1
        assert config.allow_multi_punch == 0
        assert config.allow_makeup == 1

    def test_update_config(self, punch_config_dao):
        data = {
            'global_time_check_enabled': 0,
            'global_location_check_enabled': 0,
            'allow_multi_punch': 1,
            'allow_makeup': 0,
            'holiday_ranges': '[{"start": "2024-05-01", "end": "2024-05-03"}]'
        }
        result = punch_config_dao.update(data)
        assert result is True

        config = punch_config_dao.get_config()
        assert config.global_time_check_enabled == 0
        assert config.global_location_check_enabled == 0
        assert config.allow_multi_punch == 1
        assert config.allow_makeup == 0
        assert config.holiday_ranges == '[{"start": "2024-05-01", "end": "2024-05-03"}]'

        data_restore = {
            'global_time_check_enabled': 1,
            'global_location_check_enabled': 1,
            'allow_multi_punch': 0,
            'allow_makeup': 1,
            'holiday_ranges': None
        }
        punch_config_dao.update(data_restore)

    def test_update_single_field(self, punch_config_dao):
        config_before = punch_config_dao.get_config()
        original_time_check = config_before.global_time_check_enabled

        data = {
            'global_time_check_enabled': 1 - original_time_check,
            'global_location_check_enabled': config_before.global_location_check_enabled,
            'allow_multi_punch': config_before.allow_multi_punch,
            'allow_makeup': config_before.allow_makeup
        }
        punch_config_dao.update(data)

        config_after = punch_config_dao.get_config()
        assert config_after.global_time_check_enabled == 1 - original_time_check

        restore_data = {
            'global_time_check_enabled': original_time_check,
            'global_location_check_enabled': config_before.global_location_check_enabled,
            'allow_multi_punch': config_before.allow_multi_punch,
            'allow_makeup': config_before.allow_makeup
        }
        punch_config_dao.update(restore_data)
