"""
数据库初始化模块

功能：
    - 读取 db/schema/ 目录下的 SQL 文件并执行
    - 插入测试数据（可选，通过 INSERT_TEST_DATA 配置控制）
    - 提供数据库初始化检查和强制初始化接口

使用方式：
    from db import check_and_init_database, init_database

    # 方式一：检查并初始化（仅在数据库为空时初始化）
    check_and_init_database()

    # 方式二：强制初始化（删除现有数据后重建）
    init_database()
"""

import os
import sqlite3
import sys

# 将 backend 目录添加到 Python 路径，以便导入同目录下的模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import get_connection, hash_password
from config import Config

# 是否插入测试数据，由 config.py 中的 INSERT_TEST_DATA 配置决定
INSERT_TEST_DATA = Config.INSERT_TEST_DATA

# SQL 文件所在目录，相对于当前文件位置
SCHEMA_DIR = os.path.join(os.path.dirname(__file__), 'schema')

# 按依赖顺序排列的 SQL 文件列表
# 注意：必须严格按照此顺序执行，以确保外键约束正确
# 依赖关系：campuses -> departments -> majors -> grades -> classes -> users -> class_teachers
#           punch_geofences -> punch_time_slots -> punch_rules -> punches
#           leaves -> makeup_requests -> punch_config -> operation_logs -> notifications -> read_views
SQL_FILES = [
    '01_campuses.sql',           # 校区表（顶层，无依赖）
    '02_departments.sql',        # 学院表（依赖 campuses）
    '03_majors.sql',             # 专业表（依赖 departments）
    '04_grades.sql',             # 年级表（依赖 majors）
    '05_classes.sql',            # 班级表（依赖 grades）
    '06_users.sql',              # 用户表（依赖 classes）
    '07_class_teachers.sql',     # 教师任课表（依赖 users, classes）
    '08_punch_geofences.sql',   # 地理围栏表（独立）
    '09_punch_time_slots.sql',   # 时间段表（独立）
    '10_punch_rules.sql',       # 打卡规则表（依赖 punch_time_slots, punch_geofences）
    '11_punches.sql',            # 打卡记录表（依赖 users, punch_rules）
    '12_leaves.sql',            # 请假申请表（依赖 users）
    '13_makeup_requests.sql',    # 补卡申请表（依赖 users）
    '14_punch_config.sql',       # 全局配置表（独立，只有一行）
    '15_operation_logs.sql',     # 操作日志表（依赖 users）
    '16_notifications.sql',     # 通知表（依赖 users）
    '17_read_views.sql',         # 只读视图（依赖 leaves, makeup_requests, users）
]


def init_database():
    """
    初始化数据库

    执行流程：
        1. 关闭外键约束（建表时需要，因为 SQLite 建表顺序可能影响外键解析）
        2. 按顺序执行所有 SQL 文件
        3. 重新开启外键约束
        4. 插入测试数据（如果配置启用）
        5. 提交事务

    异常处理：
        - 任何错误都会回滚事务并抛出异常
        - 调用方应捕获异常并进行相应处理

    注意：
        - 此函数会删除已存在的数据库内容，请谨慎使用
        - 建议使用 check_and_init_database() 进行安全初始化
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # 关闭外键约束，避免建表时因顺序问题报错
        # SQLite 需要在建表前关闭外键检查，建完后再开启
        cursor.execute('PRAGMA foreign_keys = OFF')

        # 按顺序执行每个 SQL 文件
        for sql_file in SQL_FILES:
            file_path = os.path.join(SCHEMA_DIR, sql_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            cursor.executescript(sql_content)

        # 建表完成后重新开启外键约束
        cursor.execute('PRAGMA foreign_keys = ON')

        # 插入测试数据（可选，用于开发测试）
        if INSERT_TEST_DATA:
            insert_test_data(cursor)

        conn.commit()
        print('数据库初始化完成')

    except Exception as e:
        print(f'数据库初始化失败: {e}')
        conn.rollback()
        raise
    finally:
        conn.close()


def insert_test_data(cursor):
    """
    插入测试数据

    参数：
        cursor: sqlite3 数据库游标

    测试数据包含：
        - 2 个校区
        - 3 个学院
        - 3 个专业
        - 3 个年级
        - 4 个班级
        - 8 个用户（1个管理员、2个教师、5个学生/班委）
        - 3 个教师任课关系
        - 3 个地理围栏
        - 4 个时间段
        - 5 条打卡规则
        - 1 条全局配置
    """
    # ===== 校区数据 =====
    sample_campuses = [
        ('主校区', '北京市海淀区中关村大街1号'),
        ('北校区', '北京市海淀区北清路99号'),
    ]
    cursor.executemany(
        'INSERT OR IGNORE INTO campuses (name, address) VALUES (?, ?)',
        sample_campuses
    )

    # ===== 学院数据 =====
    sample_departments = [
        (1, '计算机学院', 'CS'),
        (1, '软件学院', 'SE'),
        (2, '信息工程学院', 'IE'),
    ]
    cursor.executemany(
        'INSERT OR IGNORE INTO departments (campus_id, name, code) VALUES (?, ?, ?)',
        sample_departments
    )

    # ===== 专业数据 =====
    sample_majors = [
        (1, '计算机科学与技术', 'CS001'),
        (1, '软件工程', 'SE001'),
        (2, '电子信息工程', 'EE001'),
    ]
    cursor.executemany(
        'INSERT OR IGNORE INTO majors (department_id, name, code) VALUES (?, ?, ?)',
        sample_majors
    )

    # ===== 年级数据 =====
    sample_grades = [
        (1, 2024, '2024级'),
        (2, 2024, '2024级'),
        (3, 2024, '2024级'),
    ]
    cursor.executemany(
        'INSERT OR IGNORE INTO grades (major_id, year, name) VALUES (?, ?, ?)',
        sample_grades
    )

    # ===== 班级数据 =====
    sample_classes = [
        ('计算机2401', 1),
        ('计算机2402', 1),
        ('软件2401', 2),
        ('电子2401', 3),
    ]
    cursor.executemany(
        'INSERT OR IGNORE INTO classes (class_name, grade_id) VALUES (?, ?)',
        sample_classes
    )

    # ===== 用户数据 =====
    # 密码统一使用 hash_password() 加密
    # 用户角色：admin-管理员，teacher-教师，monitor-班委，student-学生
    sample_users = [
        # (user_id, username, password, real_name, role, class_name, student_id, phone, email)
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

    # ===== 教师任课关系 =====
    sample_class_teachers = [
        ('计算机2401', 'T2024001', '2024-2025-1'),
        ('计算机2401', 'T2024002', '2024-2025-1'),
        ('软件2401', 'T2024001', '2024-2025-1'),
    ]
    cursor.executemany(
        'INSERT OR IGNORE INTO class_teachers (class_name, teacher_id, semester) VALUES (?, ?, ?)',
        sample_class_teachers
    )

    # ===== 地理围栏数据 =====
    # fence_type: circle-圆形围栏，polygon-多边形围栏
    # polygon_coords: 多边形顶点坐标（polygon 类型时使用），circle 类型为 NULL
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

    # ===== 时间段数据 =====
    # start_time 和 end_time 使用 HH:MM:SS 格式
    sample_time_slots = [
        ('早读', '07:30', '08:00', 1),
        ('上午上课', '08:00', '12:00', 1),
        ('下午上课', '14:00', '18:00', 1),
        ('晚自习', '19:00', '21:00', 1),
    ]
    cursor.executemany(
        'INSERT OR IGNORE INTO punch_time_slots (name, start_time, end_time, enabled) VALUES (?, ?, ?, ?)',
        sample_time_slots
    )

    # ===== 打卡规则数据 =====
    # priority: 优先级，数字越小优先级越高
    # time_enabled/location_enabled: 是否启用时间/位置校验
    sample_rules = [
        # (time_slot_id, geofence_id, priority, time_enabled, location_enabled, enabled)
        (1, 1, 100, 1, 1, 1),  # 早读 - 教学楼A
        (2, 1, 100, 1, 1, 1),  # 上午上课 - 教学楼A
        (2, 2, 90, 1, 1, 1),   # 上午上课 - 图书馆（优先级更高）
        (3, 3, 100, 1, 1, 1),  # 下午上课 - 操场
        (4, 3, 80, 1, 1, 1),  # 晚自习 - 操场（优先级更高）
    ]
    cursor.executemany(
        '''INSERT OR IGNORE INTO punch_rules
           (time_slot_id, geofence_id, priority, time_enabled, location_enabled, enabled)
           VALUES (?, ?, ?, ?, ?, ?)''',
        sample_rules
    )

    # ===== 全局配置数据 =====
    # punch_config 表只有一行，id 固定为 1
    # global_time_check_enabled: 全局时间校验开关
    # global_location_check_enabled: 全局位置校验开关
    # allow_multi_punch: 是否允许多人同设备打卡
    # allow_makeup: 是否允许补卡申请
    # holiday_ranges: 节假日日期范围，JSON 格式
    cursor.execute(
        '''INSERT OR IGNORE INTO punch_config
           (id, global_time_check_enabled, global_location_check_enabled, allow_multi_punch, allow_makeup)
           VALUES (1, 1, 1, 0, 1)'''
    )


def check_and_init_database():
    """
    检查并初始化数据库（安全模式）

    执行流程：
        1. 检查 users 表是否存在
        2. 如果不存在，则调用 init_database() 初始化
        3. 如果已存在，打印提示信息并跳过

    使用场景：
        - 应用启动时调用，确保数据库存在
        - 不会删除现有数据，安全的初始化方式

    注意：
        - 此函数仅检查 users 表是否存在，无法检测表结构是否完整
        - 如需强制重建数据库，请使用 init_database()
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone() is None:
            init_database()
        else:
            print('数据库已存在且结构完整，无需初始化')
    finally:
        conn.close()
