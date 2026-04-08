import pytest


class TestCampusDAO:
    def test_get_by_id(self, campus_dao):
        campus = campus_dao.get_by_id(1)
        assert campus is not None
        assert campus.name == '主校区'

    def test_get_by_id_not_found(self, campus_dao):
        campus = campus_dao.get_by_id(999)
        assert campus is None

    def test_get_list(self, campus_dao):
        campuses = campus_dao.get_list()
        assert len(campuses) >= 2

    def test_create(self, campus_dao):
        data = {'name': '测试校区', 'address': '测试地址'}
        new_id = campus_dao.create(data)
        assert new_id is not None

        campus = campus_dao.get_by_id(new_id)
        assert campus.name == '测试校区'
        assert campus.address == '测试地址'

    def test_update(self, campus_dao):
        campus = campus_dao.get_by_id(1)
        original_name = campus.name

        result = campus_dao.update(1, {'name': '主校区改', 'address': '新地址'})
        assert result is True

        campus = campus_dao.get_by_id(1)
        assert campus.name == '主校区改'

        campus_dao.update(1, {'name': original_name})

    def test_delete(self, campus_dao):
        new_id = campus_dao.create({'name': '待删除校区', 'address': '地址'})
        result = campus_dao.delete(new_id)
        assert result is True

        campus = campus_dao.get_by_id(new_id)
        assert campus is None


class TestGradeDAO:
    def test_get_by_id(self, grade_dao):
        grade = grade_dao.get_by_id(1)
        assert grade is not None
        assert grade.year == 2024

    def test_get_list(self, grade_dao):
        grades = grade_dao.get_list()
        assert len(grades) >= 3

    def test_create(self, grade_dao):
        data = {'major_id': 1, 'year': 2025, 'name': '2025级'}
        new_id = grade_dao.create(data)
        assert new_id is not None

        grade = grade_dao.get_by_id(new_id)
        assert grade.year == 2025
        assert grade.name == '2025级'

    def test_update(self, grade_dao):
        grade = grade_dao.get_by_id(1)
        original_year = grade.year

        result = grade_dao.update(1, {'major_id': grade.major_id, 'year': 2026, 'name': '2026级'})
        assert result is True

        grade = grade_dao.get_by_id(1)
        assert grade.year == 2026

        grade_dao.update(1, {'major_id': grade.major_id, 'year': original_year, 'name': grade.name})


class TestClassDAO:
    def test_get_by_id(self, class_dao):
        cls = class_dao.get_by_id('计算机2401')
        assert cls is not None
        assert cls.class_name == '计算机2401'
        assert cls.grade_id == 1

    def test_get_by_id_not_found(self, class_dao):
        cls = class_dao.get_by_id('不存在的班级')
        assert cls is None

    def test_get_list(self, class_dao):
        classes = class_dao.get_list()
        assert len(classes) >= 4

    def test_create(self, class_dao):
        data = {'class_name': '测试班级2401', 'grade_id': 1}
        result = class_dao.create(data)
        assert result == '测试班级2401'

        cls = class_dao.get_by_id('测试班级2401')
        assert cls is not None
        assert cls.grade_id == 1

    def test_update(self, class_dao):
        cls = class_dao.get_by_id('计算机2401')
        original_grade_id = cls.grade_id

        result = class_dao.update('计算机2401', {'grade_id': 2})
        assert result is True

        cls = class_dao.get_by_id('计算机2401')
        assert cls.grade_id == 2

        class_dao.update('计算机2401', {'grade_id': original_grade_id})

    def test_delete(self, class_dao, temp_db):
        class_dao.create({'class_name': '待删除班级', 'grade_id': 1})
        result = class_dao.delete('待删除班级')
        assert result is True

        import sqlite3
        conn = sqlite3.connect(temp_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM classes WHERE class_name = '待删除班级'")
        row = cursor.fetchone()
        conn.close()
        assert row is not None
        assert row['deleted_at'] is not None


class TestPunchDAO:
    def test_get_by_id(self, punch_dao):
        punches = punch_dao.get_list(limit=1)
        if punches:
            punch = punch_dao.get_by_id(punches[0].id)
            assert punch is not None

    def test_get_list(self, punch_dao):
        punches = punch_dao.get_list()
        assert isinstance(punches, list)

    def test_create(self, punch_dao):
        data = {
            'user_id': 'S2024001',
            'punch_date': '2024-03-15',
            'punch_time': '08:00:00',
            'latitude': 39.989,
            'longitude': 116.312,
            'matched_rule_id': 1,
            'is_makeup': 0,
            'device_id': 'test_device'
        }
        new_id = punch_dao.create(data)
        assert new_id is not None

        punch = punch_dao.get_by_id(new_id)
        assert punch.user_id == 'S2024001'
        assert punch.matched_rule_id == 1

    def test_update(self, punch_dao):
        data = {
            'user_id': 'S2024001',
            'punch_date': '2024-03-15',
            'punch_time': '08:00:00',
            'latitude': 39.989,
            'longitude': 116.312,
            'matched_rule_id': 1
        }
        new_id = punch_dao.create(data)

        result = punch_dao.update(new_id, {
            'user_id': 'S2024001',
            'punch_date': '2024-03-15',
            'punch_time': '09:00:00',
            'latitude': 39.989,
            'longitude': 116.312,
            'matched_rule_id': 2
        })
        assert result is True

        punch = punch_dao.get_by_id(new_id)
        assert punch.punch_time == '09:00:00'


class TestPunchRuleDAO:
    def test_get_by_id(self, punch_rule_dao):
        rule = punch_rule_dao.get_by_id(1)
        assert rule is not None
        assert rule.time_slot_id == 1

    def test_get_list(self, punch_rule_dao):
        rules = punch_rule_dao.get_list()
        assert len(rules) >= 5

    def test_get_list_by_time_slot(self, punch_rule_dao):
        rules = punch_rule_dao.get_list(where='time_slot_id = ?', params=(1,))
        assert all(r.time_slot_id == 1 for r in rules)

    def test_create(self, punch_rule_dao):
        data = {
            'time_slot_id': 1,
            'geofence_id': 1,
            'priority': 50,
            'time_enabled': 1,
            'location_enabled': 1,
            'enabled': 1
        }
        new_id = punch_rule_dao.create(data)
        assert new_id is not None

        rule = punch_rule_dao.get_by_id(new_id)
        assert rule.priority == 50

    def test_update(self, punch_rule_dao):
        data = {
            'time_slot_id': 1,
            'geofence_id': 1,
            'priority': 50,
            'time_enabled': 1,
            'location_enabled': 1,
            'enabled': 1
        }
        new_id = punch_rule_dao.create(data)

        result = punch_rule_dao.update(new_id, {
            'time_slot_id': 1,
            'geofence_id': 1,
            'priority': 60,
            'time_enabled': 1,
            'location_enabled': 1,
            'enabled': 1
        })
        assert result is True

        rule = punch_rule_dao.get_by_id(new_id)
        assert rule.priority == 60


class TestLeaveDAO:
    def test_get_by_id(self, leave_dao):
        leaves = leave_dao.get_list(limit=1)
        if leaves:
            leave = leave_dao.get_by_id(leaves[0].id)
            assert leave is not None

    def test_get_list(self, leave_dao):
        leaves = leave_dao.get_list()
        assert isinstance(leaves, list)

    def test_create(self, leave_dao):
        data = {
            'user_id': 'S2024001',
            'leave_start_date': '2024-03-20',
            'leave_end_date': '2024-03-22',
            'leave_type': '事假',
            'leave_reason': '家中有事'
        }
        new_id = leave_dao.create(data)
        assert new_id is not None

        leave = leave_dao.get_by_id(new_id)
        assert leave.user_id == 'S2024001'
        assert leave.leave_type == '事假'

    def test_update_status(self, leave_dao):
        data = {
            'user_id': 'S2024001',
            'leave_start_date': '2024-03-25',
            'leave_end_date': '2024-03-26',
            'leave_type': '病假',
            'leave_reason': '身体不适'
        }
        new_id = leave_dao.create(data)

        result = leave_dao.update(new_id, {
            'leave_status': 'approved',
            'approved_by': 'T2024001'
        })
        assert result is True

        leave = leave_dao.get_by_id(new_id)
        assert leave.leave_status == 'approved'
        assert leave.approved_by == 'T2024001'
