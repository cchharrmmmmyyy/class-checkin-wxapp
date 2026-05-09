"""pytest 配置：提供测试用 Flask app、数据库连接、fixtures。"""

import os
import sys
import tempfile

# ---- 必须在导入项目模块前设置环境变量 ----
os.environ.setdefault('JWT_SECRET_KEY', 'test-secret-key-for-testing')
os.environ.setdefault('TOKEN_EXPIRE_HOURS', '24')
os.environ.setdefault('DATABASE_FILE', 'test.db')
os.environ.setdefault('INSERT_TEST_DATA', 'False')
os.environ.setdefault('FLASK_HOST', '127.0.0.1')
os.environ.setdefault('FLASK_PORT', '5000')
os.environ.setdefault('FLASK_DEBUG', 'False')
os.environ.setdefault('RANDOM_PASSWORD_LENGTH', '8')
os.environ.setdefault('PUNCH_RECORDS_LIMIT', '30')

import shutil
import pytest
from pathlib import Path

# 确保 backend 目录在 sys.path 中
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from config import Config
from utils.db import get_connection
from db import init_database
from utils.password import hash_password
from utils.seed_data import insert_test_data

# ---- 常量 ----
SCHEMA_DIR = _backend_dir / 'db' / 'schema'


@pytest.fixture(scope='session')
def db_path():
    """为整个测试 session 创建一个临时数据库文件。"""
    tmpdir = tempfile.mkdtemp()
    db_file = os.path.join(tmpdir, 'test.db')
    old_value = Config.DATABASE_FILE
    Config.DATABASE_FILE = db_file
    yield db_file
    Config.DATABASE_FILE = old_value
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture(scope='session')
def init_schema(db_path):
    """执行所有建表 SQL 初始化数据库结构。"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = OFF')

    sql_files = sorted(Path(SCHEMA_DIR).glob('*.sql'))
    for sql_file in sql_files:
        with open(sql_file, 'r', encoding='utf-8') as f:
            cursor.executescript(f.read())

    conn.commit()
    conn.close()


@pytest.fixture(autouse=True)
def clear_data(db_path, init_schema):
    """每个测试前清空所有表数据（保留表结构）。"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = OFF')

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall() if row[0] not in ('sqlite_sequence',)]
    for table in tables:
        cursor.execute(f'DELETE FROM {table}')

    conn.commit()
    conn.close()


@pytest.fixture
def seed_basic_org():
    """插入基础组织架构数据：1个校区、1个院系、1个专业、1个年级、1个班级。"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO campuses (id, name, address) VALUES (1, '测试校区', '测试地址')")
    cursor.execute("INSERT INTO departments (id, campus_id, name, code) VALUES (1, 1, '测试学院', 'CS')")
    cursor.execute("INSERT INTO majors (id, department_id, name, code) VALUES (1, 1, '计算机科学与技术', 'CS001')")
    cursor.execute("INSERT INTO grades (id, major_id, year, name) VALUES (1, 1, 2024, '2024级')")
    cursor.execute("INSERT INTO classes (class_name, grade_id) VALUES ('计算机2401', 1)")
    conn.commit()
    conn.close()


@pytest.fixture
def seed_users(seed_basic_org):
    """在 seed_basic_org 基础上插入用户数据。"""
    conn = get_connection()
    cursor = conn.cursor()
    users = [
        ('admin001', 'admin', hash_password('admin123'), '超级管理员', 'admin', None, None, None, None),
        ('T2024001', 'zhang_teacher', hash_password('123456'), '张老师', 'teacher', None, None, '13800001001', 'zhang@test.com'),
        ('T2024002', 'li_teacher', hash_password('123456'), '李老师', 'teacher', None, None, '13800001002', 'li@test.com'),
        ('S2024001', 'zhang_student', hash_password('123456'), '张三', 'student', '计算机2401', '2024001', '13800002001', 'zhang@student.com'),
        ('S2024002', 'li_student', hash_password('123456'), '李四', 'student', '计算机2401', '2024002', '13800002002', 'li@student.com'),
        ('S2024003', 'wang_student', hash_password('123456'), '王五', 'monitor', '计算机2401', '2024003', '13800002003', 'wang@student.com'),
    ]
    cursor.executemany(
        '''INSERT INTO users (user_id, username, password, real_name, role, class_name, student_id, phone, email)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        users
    )
    # 教师任课关系
    cursor.execute(
        "INSERT INTO class_teachers (class_name, teacher_id, semester) VALUES (?, ?, ?)",
        ('计算机2401', 'T2024001', '2024-2025-1')
    )
    conn.commit()
    conn.close()


@pytest.fixture
def seed_geofences(seed_basic_org):
    """插入打卡围栏数据。"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO punch_geofences (id, name, fence_type, latitude, longitude, radius, enabled) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (1, '教学楼A', 'circle', 39.989, 116.312, 200, 1)
    )
    conn.commit()
    conn.close()


@pytest.fixture
def seed_time_slots(seed_basic_org):
    """插入时间段数据。"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO punch_time_slots (id, name, start_time, end_time, enabled) VALUES (?, ?, ?, ?, ?)",
        (1, '上午上课', '08:00', '12:00', 1)
    )
    conn.commit()
    conn.close()


@pytest.fixture
def seed_teaching_assignment(seed_users):
    """在 seed_users 基础上插入任课关系。"""
    return  # 已在 seed_users 中插入


@pytest.fixture
def seed_punch_rules(seed_geofences, seed_time_slots):
    """插入打卡规则。"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO punch_rules (id, time_slot_id, geofence_id, priority, time_enabled, location_enabled, enabled) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (1, 1, 1, 100, 1, 1, 1)
    )
    conn.commit()
    conn.close()


@pytest.fixture
def seed_punch_config():
    """插入全局打卡配置。"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO punch_config (id, global_time_check_enabled, global_location_check_enabled, allow_multi_punch, allow_makeup) VALUES (?, ?, ?, ?, ?)",
        (1, 1, 1, 0, 1)
    )
    conn.commit()
    conn.close()


@pytest.fixture
def seed_leaves(seed_users):
    """插入请假记录。"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO leaves (id, user_id, leave_start_date, leave_end_date, leave_type, leave_reason, leave_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (1, 'S2024001', '2026-05-10', '2026-05-12', 'personal', '个人事务', 'pending')
    )
    conn.commit()
    conn.close()


@pytest.fixture
def seed_punches(seed_users):
    """插入打卡记录。"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO punches (id, user_id, punch_date, punch_time, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?)",
        (1, 'S2024001', '2026-05-09', '08:30:00', 39.989, 116.312)
    )
    conn.commit()
    conn.close()


@pytest.fixture
def seed_makeup_requests(seed_users):
    """插入补签申请。"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO makeup_requests (id, user_id, target_date, reason, status) VALUES (?, ?, ?, ?, ?)",
        (1, 'S2024001', '2026-05-08', '忘记打卡', 'pending')
    )
    conn.commit()
    conn.close()


@pytest.fixture
def seed_notifications(seed_users):
    """插入通知。"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notifications (id, receiver_id, title, content, type) VALUES (?, ?, ?, ?, ?)",
        (1, 'S2024001', '测试通知', '这是一条测试通知', 'SYSTEM')
    )
    conn.commit()
    conn.close()


@pytest.fixture
def seed_full_data(seed_punch_config, seed_users, seed_geofences, seed_time_slots,
                   seed_punch_rules, seed_leaves, seed_punches, seed_makeup_requests):
    """全量种子数据组合 fixture。"""
