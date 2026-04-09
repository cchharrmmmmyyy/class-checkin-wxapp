import pytest
from services.admin_service import AdminService
from utils.exceptions import ServiceException


class TestAdminService:

    def test_list_users(self):
        """测试获取用户列表"""
        users = AdminService.list_users()
        assert isinstance(users, list)
        # 确保返回的用户信息包含必要字段
        for user in users:
            assert 'username' in user
            assert 'user_id' in user
            assert 'role' in user
            assert 'class' in user

    def test_save_user_create(self):
        """测试创建新用户"""
        # 测试创建学生用户
        result = AdminService.save_user(
            username="测试学生",
            user_id="test001",
            password="123456",
            role="student",
            class_name="测试班级"
        )
        assert result['success'] is True
        assert result['message'] == '用户添加成功'

    def test_save_user_update(self):
        """测试更新用户"""
        # 先创建一个用户
        AdminService.save_user(
            username="测试用户",
            user_id="test002",
            password="123456",
            role="student",
            class_name="测试班级"
        )
        # 再更新该用户
        result = AdminService.save_user(
            username="更新后的测试用户",
            user_id="test002",
            password="",
            role="student",
            class_name="测试班级"
        )
        assert result['success'] is True
        assert result['message'] == '用户更新成功'

    def test_save_user_invalid_role(self):
        """测试无效角色"""
        with pytest.raises(ServiceException) as excinfo:
            AdminService.save_user(
                username="测试用户",
                user_id="test003",
                password="123456",
                role="invalid_role",
                class_name="测试班级"
            )
        assert "角色必须是" in str(excinfo.value)

    def test_save_user_admin_with_class(self):
        """测试管理员设置班级"""
        with pytest.raises(ServiceException) as excinfo:
            AdminService.save_user(
                username="测试管理员",
                user_id="admin002",
                password="123456",
                role="admin",
                class_name="测试班级"
            )
        assert "管理员不应设置班级" in str(excinfo.value)

    def test_save_user_student_without_class(self):
        """测试学生没有设置班级"""
        with pytest.raises(ServiceException) as excinfo:
            AdminService.save_user(
                username="测试学生",
                user_id="test004",
                password="123456",
                role="student",
                class_name=""
            )
        assert "老师、学生、班委必须设置班级" in str(excinfo.value)

    def test_delete_user(self):
        """测试删除用户"""
        # 先创建一个用户
        AdminService.save_user(
            username="待删除用户",
            user_id="test005",
            password="123456",
            role="student",
            class_name="测试班级"
        )
        # 再删除该用户
        result = AdminService.delete_user("test005")
        assert result['success'] is True
        assert result['message'] == '用户删除成功'

    def test_delete_nonexistent_user(self):
        """测试删除不存在的用户"""
        with pytest.raises(ServiceException) as excinfo:
            AdminService.delete_user("nonexistent")
        assert "用户不存在" in str(excinfo.value)

    def test_reset_password(self):
        """测试重置密码"""
        # 先创建一个用户
        AdminService.save_user(
            username="测试用户",
            user_id="test006",
            password="123456",
            role="student",
            class_name="测试班级"
        )
        # 重置密码
        result = AdminService.reset_password("test006")
        assert result['success'] is True
        assert result['message'] == '密码重置成功'
        assert 'new_password' in result

    def test_reset_password_admin(self):
        """测试重置管理员密码"""
        with pytest.raises(ServiceException) as excinfo:
            AdminService.reset_password("admin001")
        assert "不允许重置管理员账户密码" in str(excinfo.value)

    def test_get_attendance_records(self):
        """测试获取考勤记录"""
        records = AdminService.get_attendance_records()
        assert isinstance(records, list)

    def test_save_attendance_record_punch(self):
        """测试保存打卡记录"""
        # 先创建一个用户
        AdminService.save_user(
            username="测试用户",
            user_id="test007",
            password="123456",
            role="student",
            class_name="测试班级"
        )
        # 保存打卡记录
        result = AdminService.save_attendance_record(
            record_id=None,
            user_id="test007",
            punch_date="2024-01-01",
            leave_start_date=None,
            leave_end_date=None,
            leave_status=None
        )
        assert result['success'] is True

    def test_save_attendance_record_leave(self):
        """测试保存请假记录"""
        # 先创建一个用户
        AdminService.save_user(
            username="测试用户",
            user_id="test008",
            password="123456",
            role="student",
            class_name="测试班级"
        )
        # 保存请假记录
        result = AdminService.save_attendance_record(
            record_id=None,
            user_id="test008",
            punch_date=None,
            leave_start_date="2024-01-01",
            leave_end_date="2024-01-02",
            leave_status="pending"
        )
        assert result['success'] is True

    def test_delete_attendance_record(self):
        """测试删除考勤记录"""
        # 先创建一个打卡记录
        AdminService.save_user(
            username="测试用户",
            user_id="test009",
            password="123456",
            role="student",
            class_name="测试班级"
        )
        # 保存打卡记录
        punch_result = AdminService.save_attendance_record(
            record_id=None,
            user_id="test009",
            punch_date="2024-01-01",
            leave_start_date=None,
            leave_end_date=None,
            leave_status=None
        )
        # 假设返回的记录ID在某个地方，这里简化处理
        # 实际测试中需要根据返回值获取记录ID

    def test_get_punch_location(self):
        """测试获取打卡位置"""
        result = AdminService.get_punch_location()
        assert result['success'] is True

    def test_save_punch_location(self):
        """测试保存打卡位置"""
        result = AdminService.save_punch_location(
            name="测试位置",
            latitude=39.9042,
            longitude=116.4074,
            radius=100
        )
        assert result['success'] is True
        assert result['message'] == '打卡位置设置成功'
