from datetime import datetime
import pytest
from models.user import User
from models.punch_config import PunchConfig
from models.campus import Campus


class TestUserModel:
    def test_user_creation(self):
        user = User(
            user_id='test001',
            username='testuser',
            password='hashed_password',
            real_name='测试用户',
            role='student',
            class_name='计算机2401',
            student_id='2024001',
            phone='13800000000',
            email='test@example.com',
            is_first_login=1,
            last_punch_time=None,
            login_fail_count=0,
            lock_until=None,
            last_login_time=None,
            last_login_ip=None,
            created_at=datetime.now(),
            deleted_at=None
        )
        assert user.user_id == 'test001'
        assert user.username == 'testuser'
        assert user.role == 'student'
        assert user.class_name == '计算机2401'

    def test_user_optional_fields(self):
        user = User(
            user_id='test002',
            username='teacher',
            password='pass',
            real_name='老师',
            role='teacher',
            class_name=None,
            student_id=None,
            phone=None,
            email=None,
            is_first_login=0,
            last_punch_time=None,
            login_fail_count=0,
            lock_until=None,
            last_login_time=None,
            last_login_ip=None,
            created_at=datetime.now(),
            deleted_at=None
        )
        assert user.class_name is None
        assert user.student_id is None


class TestPunchConfigModel:
    def test_punch_config_creation(self):
        config = PunchConfig(
            id=1,
            global_time_check_enabled=1,
            global_location_check_enabled=1,
            allow_multi_punch=0,
            allow_makeup=1,
            holiday_ranges=None,
            updated_at=datetime.now()
        )
        assert config.id == 1
        assert config.global_time_check_enabled == 1
        assert config.allow_makeup == 1

    def test_punch_config_with_holiday_ranges(self):
        config = PunchConfig(
            id=1,
            global_time_check_enabled=1,
            global_location_check_enabled=1,
            allow_multi_punch=0,
            allow_makeup=1,
            holiday_ranges='[{"start": "2024-01-01", "end": "2024-01-03"}]',
            updated_at=datetime.now()
        )
        assert config.holiday_ranges is not None


class TestCampusModel:
    def test_campus_creation(self):
        campus = Campus(
            id=1,
            name='主校区',
            address='北京市海淀区',
            created_at=datetime.now()
        )
        assert campus.name == '主校区'
        assert campus.address == '北京市海淀区'
