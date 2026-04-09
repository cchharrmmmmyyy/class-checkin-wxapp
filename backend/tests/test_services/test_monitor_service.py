import pytest
from services.monitor_service import MonitorService
from services.admin_service import AdminService
from services.leave_service import LeaveService
from services.punch_service import PunchService


class TestMonitorService:

    def setup_method(self):
        """测试前的准备工作"""
        # 创建测试班级
        self.test_class = "测试班级"
        # 创建测试学生
        self.student_id = "student001"
        AdminService.save_user(
            username="测试学生",
            user_id=self.student_id,
            password="123456",
            role="student",
            class_name=self.test_class
        )
        # 创建另一个学生
        self.student_id2 = "student002"
        AdminService.save_user(
            username="测试学生2",
            user_id=self.student_id2,
            password="123456",
            role="student",
            class_name=self.test_class
        )

    def test_get_class_attendance(self):
        """测试获取班级考勤情况"""
        attendance = MonitorService.get_class_attendance(self.test_class)
        assert isinstance(attendance, list)
        assert len(attendance) >= 2
        # 确保返回的考勤信息包含必要字段
        for student_attendance in attendance:
            assert 'user_id' in student_attendance
            assert 'username' in student_attendance
            assert 'status' in student_attendance

    def test_get_class_attendance_with_date(self):
        """测试获取指定日期的班级考勤情况"""
        # 测试日期
        test_date = "2024-01-01"
        # 为一个学生创建打卡记录
        PunchService.punch(
            user_id=self.student_id,
            latitude=39.9042,
            longitude=116.4074
        )
        # 获取考勤情况
        attendance = MonitorService.get_class_attendance(self.test_class, test_date)
        assert isinstance(attendance, list)

    def test_get_class_leave_applications(self):
        """测试获取班级请假申请"""
        # 提交请假申请
        LeaveService.apply_leave(
            user_id=self.student_id,
            leave_start_date="2024-01-01",
            leave_end_date="2024-01-02",
            leave_type="personal",
            leave_reason="测试请假"
        )
        # 获取请假申请
        applications = MonitorService.get_class_leave_applications(self.test_class)
        assert isinstance(applications, list)
        # 确保返回的请假申请包含必要字段
        for app in applications:
            assert 'id' in app
            assert 'user_id' in app
            assert 'username' in app
            assert 'leave_start_date' in app
            assert 'leave_end_date' in app
            assert 'leave_status' in app

    def test_get_class_punch_records(self):
        """测试获取班级打卡记录"""
        # 创建打卡记录
        PunchService.punch(
            user_id=self.student_id,
            latitude=39.9042,
            longitude=116.4074
        )
        # 获取打卡记录
        records = MonitorService.get_class_punch_records(self.test_class)
        assert isinstance(records, list)
        # 确保返回的打卡记录包含必要字段
        for record in records:
            assert 'id' in record
            assert 'user_id' in record
            assert 'username' in record
            assert 'punch_date' in record
            assert 'punch_time' in record

    def test_get_class_punch_records_with_date_range(self):
        """测试获取指定日期范围的班级打卡记录"""
        # 测试日期范围
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        # 创建打卡记录
        PunchService.punch(
            user_id=self.student_id,
            latitude=39.9042,
            longitude=116.4074
        )
        # 获取打卡记录
        records = MonitorService.get_class_punch_records(self.test_class, start_date, end_date)
        assert isinstance(records, list)

    def test_get_attendance_summary(self):
        """测试获取考勤汇总"""
        # 测试日期范围
        start_date = "2024-01-01"
        end_date = "2024-01-02"
        # 创建打卡记录
        PunchService.punch(
            user_id=self.student_id,
            latitude=39.9042,
            longitude=116.4074
        )
        # 获取考勤汇总
        summary = MonitorService.get_attendance_summary(self.test_class, start_date, end_date)
        assert isinstance(summary, dict)
        assert 'class_name' in summary
        assert 'start_date' in summary
        assert 'end_date' in summary
        assert 'total_students' in summary
        assert 'attendance_rate' in summary
        assert 'details' in summary
        # 确保返回的详情包含必要字段
        for detail in summary['details']:
            assert 'user_id' in detail
            assert 'username' in detail
            assert 'attendance_days' in detail
            assert 'leave_days' in detail
            assert 'absent_days' in detail
            assert 'attendance_rate' in detail
