"""AdminAttendanceService 考勤管理行为测试。"""

import pytest
from services.admin_attendance_service import AdminAttendanceService


class TestAttendanceRecords:

    def test_get_attendance_records(self, seed_full_data):
        result = AdminAttendanceService.get_attendance_records(page=1, size=50)
        assert result['total'] >= 1
        assert 'items' in result

    def test_get_attendance_records_filtered(self, seed_full_data):
        result = AdminAttendanceService.get_attendance_records(
            user_id='S2024001', page=1, size=50
        )
        assert result['total'] >= 1
        for item in result['items']:
            assert item['user_id'] == 'S2024001'

    def test_export_csv(self, seed_full_data):
        csv_data, filename = AdminAttendanceService.export_attendance_records_csv()
        assert filename.endswith('.csv')
        assert len(csv_data) > 0
        assert b'ID' in csv_data

    def test_export_csv_empty(self):
        csv_data, filename = AdminAttendanceService.export_attendance_records_csv()
        assert filename.endswith('.csv')


class TestManagePunchRecord:

    def test_create_punch_record(self, seed_users):
        result = AdminAttendanceService.save_punch_record(
            record_id=None, user_id='S2024001', punch_date='2026-05-09'
        )
        assert result['success'] is True
        assert 'id' in result

    def test_update_punch_record(self, seed_users, seed_punches):
        result = AdminAttendanceService.save_punch_record(
            record_id=1, user_id='S2024001', punch_date='2026-05-09', punch_time='09:00:00'
        )
        assert result['success'] is True

    def test_delete_punch_record(self, seed_users, seed_punches):
        result = AdminAttendanceService.delete_punch_record(1)
        assert result['success'] is True


class TestManageLeaveRecord:

    def test_create_leave_record(self, seed_users):
        result = AdminAttendanceService.save_leave_record(
            record_id=None, user_id='S2024001',
            leave_start_date='2026-06-01', leave_end_date='2026-06-03'
        )
        assert result['success'] is True

    def test_delete_leave_record(self, seed_users, seed_leaves):
        result = AdminAttendanceService.delete_leave_record(1)
        assert result['success'] is True


class TestDashboard:

    def test_dashboard_stats(self, seed_full_data):
        stats = AdminAttendanceService.get_dashboard_stats()
        assert 'total_students' in stats
        assert stats['total_students'] >= 1


class TestPunchLocation:

    def test_get_punch_location(self, seed_geofences):
        result = AdminAttendanceService.get_punch_location()
        assert result['success'] is True
        assert result['data'] is not None

    def test_get_punch_location_no_geofence(self):
        result = AdminAttendanceService.get_punch_location()
        assert result['success'] is True
        assert result['data'] is None

    def test_save_punch_location(self, seed_geofences):
        result = AdminAttendanceService.save_punch_location(
            name='新位置', latitude=39.9, longitude=116.3, radius=200
        )
        assert result['success'] is True
