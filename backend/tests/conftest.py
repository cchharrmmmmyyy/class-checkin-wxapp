import os
import sys
import sqlite3
import pytest
import tempfile
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_test_db_file = None


def _create_test_db():
    global _test_db_file
    db_file = os.path.join(tempfile.gettempdir(), f'test_class_checkin_{uuid.uuid4().hex}.db')
    _test_db_file = db_file

    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = OFF')

    schema_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db', 'schema')
    sql_files = [
        '01_campuses.sql', '02_departments.sql', '03_majors.sql', '04_grades.sql',
        '05_classes.sql', '06_users.sql', '07_class_teachers.sql', '08_punch_geofences.sql',
        '09_punch_time_slots.sql', '10_punch_rules.sql', '11_punches.sql', '12_leaves.sql',
        '13_makeup_requests.sql', '14_punch_config.sql', '15_operation_logs.sql', '16_notifications.sql',
        '17_read_views.sql'
    ]

    for sql_file in sql_files:
        file_path = os.path.join(schema_dir, sql_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        cursor.executescript(sql_content)

    cursor.execute('PRAGMA foreign_keys = ON')

    from utils.db import hash_password
    _insert_test_data(cursor, hash_password)

    conn.commit()
    conn.close()
    return db_file


def _insert_test_data(cursor, hash_password):
    sample_campuses = [
        ('主校区', '北京市海淀区中关村大街1号'),
        ('北校区', '北京市海淀区北清路99号'),
    ]
    cursor.executemany('INSERT OR IGNORE INTO campuses (name, address) VALUES (?, ?)', sample_campuses)

    sample_departments = [
        (1, '计算机学院', 'CS'),
        (1, '软件学院', 'SE'),
        (2, '信息工程学院', 'IE'),
    ]
    cursor.executemany('INSERT OR IGNORE INTO departments (campus_id, name, code) VALUES (?, ?, ?)', sample_departments)

    sample_majors = [
        (1, '计算机科学与技术', 'CS001'),
        (1, '软件工程', 'SE001'),
        (2, '电子信息工程', 'EE001'),
    ]
    cursor.executemany('INSERT OR IGNORE INTO majors (department_id, name, code) VALUES (?, ?, ?)', sample_majors)

    sample_grades = [
        (1, 2024, '2024级'),
        (2, 2024, '2024级'),
        (3, 2024, '2024级'),
    ]
    cursor.executemany('INSERT OR IGNORE INTO grades (major_id, year, name) VALUES (?, ?, ?)', sample_grades)

    sample_classes = [
        ('计算机2401', 1),
        ('计算机2402', 1),
        ('软件2401', 2),
        ('电子2401', 3),
    ]
    cursor.executemany('INSERT OR IGNORE INTO classes (class_name, grade_id) VALUES (?, ?)', sample_classes)

    sample_users = [
        ('admin001', 'admin', hash_password('admin123'), '超级管理员', 'admin', None, None, None, None),
        ('T2024001', 'zhang_teacher', hash_password('123456'), '张老师', 'teacher', None, None, '13800001001', 'zhang@test.com'),
        ('T2024002', 'li_teacher', hash_password('123456'), '李老师', 'teacher', None, None, '13800001002', 'li@test.com'),
        ('S2024001', 'zhang_student', hash_password('123456'), '张三', 'student', '计算机2401', '2024001', '13800002001', 'zhang@student.com'),
        ('S2024002', 'li_student', hash_password('123456'), '李四', 'student', '计算机2401', '2024002', '13800002002', 'li@student.com'),
        ('S2024003', 'wang_student', hash_password('123456'), '王五', 'monitor', '计算机2401', '2024003', '13800002003', 'wang@student.com'),
        ('S2024004', 'zhao_student', hash_password('123456'), '赵六', 'student', '软件2401', '2024004', '13800002004', 'zhao@student.com'),
        ('S2024005', 'qian_student', hash_password('123456'), '钱七', 'student', '软件2401', '2024005', '13800002005', 'qian@student.com'),
    ]
    cursor.executemany(
        '''INSERT OR IGNORE INTO users
           (user_id, username, password, real_name, role, class_name, student_id, phone, email)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        sample_users
    )

    sample_class_teachers = [
        ('计算机2401', 'T2024001', '2024-2025-1'),
        ('计算机2401', 'T2024002', '2024-2025-1'),
        ('软件2401', 'T2024001', '2024-2025-1'),
    ]
    cursor.executemany('INSERT OR IGNORE INTO class_teachers (class_name, teacher_id, semester) VALUES (?, ?, ?)', sample_class_teachers)

    sample_geofences = [
        ('教学楼A', 'circle', 39.989, 116.312, 200, None, 1),
        ('图书馆', 'circle', 39.990, 116.313, 150, None, 1),
        ('操场', 'circle', 39.988, 116.311, 300, None, 1),
    ]
    cursor.executemany(
        '''INSERT OR IGNORE INTO punch_geofences
           (name, fence_type, latitude, longitude, radius, polygon_coords, enabled)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        sample_geofences
    )

    sample_time_slots = [
        ('早读', '07:30', '08:00', 1),
        ('上午上课', '08:00', '12:00', 1),
        ('下午上课', '14:00', '18:00', 1),
        ('晚自习', '19:00', '21:00', 1),
    ]
    cursor.executemany('INSERT OR IGNORE INTO punch_time_slots (name, start_time, end_time, enabled) VALUES (?, ?, ?, ?)', sample_time_slots)

    sample_rules = [
        (1, 1, 100, 1, 1, 1),
        (2, 1, 100, 1, 1, 1),
        (2, 2, 90, 1, 1, 1),
        (3, 3, 100, 1, 1, 1),
        (4, 3, 80, 1, 1, 1),
    ]
    cursor.executemany(
        '''INSERT OR IGNORE INTO punch_rules
           (time_slot_id, geofence_id, priority, time_enabled, location_enabled, enabled)
           VALUES (?, ?, ?, ?, ?, ?)''',
        sample_rules
    )

    cursor.execute(
        '''INSERT OR IGNORE INTO punch_config
           (id, global_time_check_enabled, global_location_check_enabled, allow_multi_punch, allow_makeup)
           VALUES (1, 1, 1, 0, 1)'''
    )


@pytest.fixture(scope='function')
def temp_db():
    db_file = _create_test_db()
    yield db_file
    try:
        os.unlink(db_file)
    except:
        pass


@pytest.fixture(scope='function')
def mock_get_connection(temp_db, monkeypatch):
    def _get_connection():
        conn = sqlite3.connect(temp_db)
        conn.row_factory = sqlite3.Row
        return conn

    monkeypatch.setattr('utils.db.get_connection', _get_connection)
    return _get_connection


@pytest.fixture(scope='function')
def campus_dao(mock_get_connection):
    from dao.campus_dao import CampusDAO
    return CampusDAO()


@pytest.fixture(scope='function')
def user_dao(mock_get_connection):
    from dao.user_dao import UserDAO
    return UserDAO()


@pytest.fixture(scope='function')
def punch_config_dao(mock_get_connection):
    from dao.punch_config_dao import PunchConfigDAO
    return PunchConfigDAO()


@pytest.fixture(scope='function')
def punch_dao(mock_get_connection):
    from dao.punch_dao import PunchDAO
    return PunchDAO()


@pytest.fixture(scope='function')
def punch_rule_dao(mock_get_connection):
    from dao.punch_rule_dao import PunchRuleDAO
    return PunchRuleDAO()


@pytest.fixture(scope='function')
def leave_dao(mock_get_connection):
    from dao.leave_dao import LeaveDAO
    return LeaveDAO()


@pytest.fixture(scope='function')
def makeup_request_dao(mock_get_connection):
    from dao.makeup_request_dao import MakeupRequestDAO
    return MakeupRequestDAO()


@pytest.fixture(scope='function')
def grade_dao(mock_get_connection):
    from dao.grade_dao import GradeDAO
    return GradeDAO()


@pytest.fixture(scope='function')
def class_dao(mock_get_connection):
    from dao.class_dao import ClassDAO
    return ClassDAO()
