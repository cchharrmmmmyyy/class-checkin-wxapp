import pytest
from services.teacher_service import TeacherService
from services.admin_service import AdminService
from utils.exceptions import ServiceException


class TestTeacherService:

    def setup_method(self):
        """测试前的准备工作"""
        # 创建测试班级
        self.test_class = "测试班级"
        # 创建测试学生
        AdminService.save_user(
            username="测试学生1",
            user_id="student001",
            password="123456",
            role="student",
            class_name=self.test_class
        )
        # 创建另一个班级的学生
        AdminService.save_user(
            username="测试学生2",
            user_id="student002",
            password="123456",
            role="student",
            class_name="其他班级"
        )

    def test_appoint_monitor(self):
        """测试任命班委"""
        result = TeacherService.appoint_monitor(
            student_id="student001",
            teacher_class=self.test_class
        )
        assert result['success'] is True
        assert result['message'] == '任命班委成功'
        assert 'data' in result
        assert result['data']['student_id'] == 'student001'

    def test_appoint_monitor_nonexistent_student(self):
        """测试任命不存在的学生为班委"""
        with pytest.raises(ServiceException) as excinfo:
            TeacherService.appoint_monitor(
                student_id="nonexistent",
                teacher_class=self.test_class
            )
        assert "未找到该学生" in str(excinfo.value)

    def test_appoint_monitor_wrong_class(self):
        """测试任命其他班级的学生为班委"""
        with pytest.raises(ServiceException) as excinfo:
            TeacherService.appoint_monitor(
                student_id="student002",
                teacher_class=self.test_class
            )
        assert "该学生不在您的班级中" in str(excinfo.value)

    def test_appoint_monitor_not_student(self):
        """测试任命非学生为班委"""
        # 先创建一个教师用户
        AdminService.save_user(
            username="测试教师",
            user_id="teacher001",
            password="123456",
            role="teacher",
            class_name=self.test_class
        )
        with pytest.raises(ServiceException) as excinfo:
            TeacherService.appoint_monitor(
                student_id="teacher001",
                teacher_class=self.test_class
            )
        assert "只有学生才能被任命为班委" in str(excinfo.value)

    def test_remove_monitor(self):
        """测试移除班委"""
        # 先任命班委
        TeacherService.appoint_monitor(
            student_id="student001",
            teacher_class=self.test_class
        )
        # 再移除班委
        result = TeacherService.remove_monitor(
            student_id="student001",
            teacher_class=self.test_class
        )
        assert result['success'] is True
        assert result['message'] == '移除班委成功'

    def test_remove_monitor_nonexistent_student(self):
        """测试移除不存在的学生的班委职务"""
        with pytest.raises(ServiceException) as excinfo:
            TeacherService.remove_monitor(
                student_id="nonexistent",
                teacher_class=self.test_class
            )
        assert "未找到该学生" in str(excinfo.value)

    def test_remove_monitor_wrong_class(self):
        """测试移除其他班级学生的班委职务"""
        with pytest.raises(ServiceException) as excinfo:
            TeacherService.remove_monitor(
                student_id="student002",
                teacher_class=self.test_class
            )
        assert "该学生不在您的班级中" in str(excinfo.value)

    def test_remove_monitor_not_monitor(self):
        """测试移除非班委学生的班委职务"""
        with pytest.raises(ServiceException) as excinfo:
            TeacherService.remove_monitor(
                student_id="student001",
                teacher_class=self.test_class
            )
        assert "该学生不是班委" in str(excinfo.value)

    def test_get_monitors(self):
        """测试获取班级班委列表"""
        # 任命班委
        TeacherService.appoint_monitor(
            student_id="student001",
            teacher_class=self.test_class
        )
        # 获取班委列表
        monitors = TeacherService.get_monitors(self.test_class)
        assert isinstance(monitors, list)
        assert len(monitors) > 0

    def test_get_students(self):
        """测试获取班级学生列表"""
        students = TeacherService.get_students(self.test_class)
        assert isinstance(students, list)
        # 确保返回的学生信息包含必要字段
        for student in students:
            assert 'username' in student
            assert 'user_id' in student
            assert 'role' in student

    def test_get_class_list(self):
        """测试获取班级列表"""
        classes = TeacherService.get_class_list()
        assert isinstance(classes, list)
        assert self.test_class in classes
