import pytest
from services.statistics_service import StatisticsService
from services.punch_service import PunchService
from services.leave_service import LeaveService


class TestStatisticsService:

    def test_get_class_statistics(self, mock_get_connection):
        """测试获取班级统计数据"""
        class_name = "计算机2401"
        start_date = "2024-01-01"
        end_date = "2024-01-07"
        
        statistics = StatisticsService.get_class_statistics(class_name, start_date, end_date)
        
        assert isinstance(statistics, dict)
        assert 'class_name' in statistics
        assert 'start_date' in statistics
        assert 'end_date' in statistics
        assert 'total_students' in statistics
        assert 'total_days' in statistics
        assert 'total_punches' in statistics
        assert 'total_leaves' in statistics
        assert 'total_absents' in statistics
        assert 'attendance_rate' in statistics
        assert 'students' in statistics
        assert statistics['class_name'] == class_name
        assert statistics['total_students'] > 0
        assert len(statistics['students']) == statistics['total_students']
        
        for student in statistics['students']:
            assert 'user_id' in student
            assert 'username' in student
            assert 'real_name' in student
            assert 'punches' in student
            assert 'leaves' in student
            assert 'absents' in student
            assert 'attendance_rate' in student

    def test_get_student_statistics(self, mock_get_connection):
        """测试获取学生个人统计数据"""
        user_id = "S2024001"
        start_date = "2024-01-01"
        end_date = "2024-01-07"
        
        statistics = StatisticsService.get_student_statistics(user_id, start_date, end_date)
        
        assert isinstance(statistics, dict)
        assert 'user_id' in statistics
        assert 'username' in statistics
        assert 'real_name' in statistics
        assert 'class_name' in statistics
        assert 'start_date' in statistics
        assert 'end_date' in statistics
        assert 'total_days' in statistics
        assert 'punches' in statistics
        assert 'leaves' in statistics
        assert 'absents' in statistics
        assert 'attendance_rate' in statistics
        assert 'punch_records' in statistics
        assert 'leave_records' in statistics
        assert statistics['user_id'] == user_id

    def test_get_attendance_alerts(self, mock_get_connection):
        """测试获取考勤预警名单"""
        class_name = "计算机2401"
        threshold = 0.8
        
        alerts = StatisticsService.get_attendance_alerts(class_name, threshold)
        
        assert isinstance(alerts, list)
        for alert in alerts:
            assert 'user_id' in alert
            assert 'username' in alert
            assert 'real_name' in alert
            assert 'attendance_rate' in alert
            assert 'punches' in alert
            assert 'leaves' in alert
            assert 'absents' in alert
            assert 'threshold' in alert
            assert alert['attendance_rate'] < threshold

    def test_get_attendance_trend(self, mock_get_connection):
        """测试获取班级考勤趋势"""
        class_name = "计算机2401"
        days = 7
        
        trend = StatisticsService.get_attendance_trend(class_name, days)
        
        assert isinstance(trend, dict)
        assert 'class_name' in trend
        assert 'start_date' in trend
        assert 'end_date' in trend
        assert 'days' in trend
        assert 'daily_data' in trend
        assert trend['class_name'] == class_name
        assert trend['days'] == days
        assert len(trend['daily_data']) == days
        
        for daily in trend['daily_data']:
            assert 'date' in daily
            assert 'present_count' in daily
            assert 'leave_count' in daily
            assert 'absent_count' in daily
            assert 'attendance_rate' in daily

    def test_get_daily_statistics(self, mock_get_connection):
        """测试获取班级当日考勤统计"""
        class_name = "计算机2401"
        date = "2024-01-15"
        
        statistics = StatisticsService.get_daily_statistics(class_name, date)
        
        assert isinstance(statistics, dict)
        assert 'class_name' in statistics
        assert 'date' in statistics
        assert 'total_students' in statistics
        assert 'present' in statistics
        assert 'leave' in statistics
        assert 'absent' in statistics
        assert 'attendance_rate' in statistics
        assert 'details' in statistics
        assert statistics['class_name'] == class_name
        assert statistics['date'] == date
        assert statistics['total_students'] > 0
        assert len(statistics['details']) == statistics['total_students']
        
        for detail in statistics['details']:
            assert 'user_id' in detail
            assert 'username' in detail
            assert 'real_name' in detail
            assert 'status' in detail
            assert detail['status'] in ['present', 'leave', 'absent']

    def test_get_daily_statistics_with_punch(self, mock_get_connection):
        """测试获取有打卡记录的当日考勤统计"""
        class_name = "计算机2401"
        date = "2024-01-16"
        
        statistics = StatisticsService.get_daily_statistics(class_name, date)
        
        assert isinstance(statistics, dict)
        assert 'class_name' in statistics
        assert 'date' in statistics
        assert 'total_students' in statistics

    def test_get_daily_statistics_with_leave(self, mock_get_connection):
        """测试获取有请假记录的当日考勤统计"""
        class_name = "计算机2401"
        user_id = "S2024002"
        date = "2024-01-17"
        
        from dao.leave_dao import LeaveDAO
        leave_dao = LeaveDAO()
        leaves = leave_dao.get_list(where="user_id = ?", params=(user_id,))
        
        statistics = StatisticsService.get_daily_statistics(class_name, date)
        
        assert isinstance(statistics, dict)
