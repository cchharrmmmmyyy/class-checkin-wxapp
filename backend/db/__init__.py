"""
数据库初始化模块（仅负责建表）

导出 check_and_init_database 和 init_database 供应用入口调用。
"""

import os

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), 'schema')

SQL_FILES = [
    '01_campuses.sql',
    '02_departments.sql',
    '03_majors.sql',
    '04_grades.sql',
    '05_classes.sql',
    '06_users.sql',
    '07_class_teachers.sql',
    '08_punch_geofences.sql',
    '09_punch_time_slots.sql',
    '10_punch_rules.sql',
    '11_punches.sql',
    '12_leaves.sql',
    '13_makeup_requests.sql',
    '14_punch_config.sql',
    '15_operation_logs.sql',
    '16_notifications.sql',
    '17_read_views.sql',
]

from utils.db import get_connection


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('PRAGMA foreign_keys = OFF')

        for sql_file in SQL_FILES:
            file_path = os.path.join(SCHEMA_DIR, sql_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            cursor.executescript(sql_content)

        conn.commit()
        print('数据库初始化完成')

    except Exception as e:
        print(f'数据库初始化失败: {e}')
        conn.rollback()
        raise
    finally:
        conn.close()


def check_and_init_database():
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
