"""
种子数据模块

为开发测试环境提供初始数据填充。仅初始化后的数据库为空时有意义。
"""

from utils.db import get_connection
from utils.password import hash_password
from config import Config


def insert_test_data():
    conn = get_connection()
    cursor = conn.cursor()

    try:
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

        # ===== 全局配置数据 =====
        cursor.execute(
            '''INSERT OR IGNORE INTO punch_config
               (id, global_time_check_enabled, global_location_check_enabled, allow_multi_punch, allow_makeup)
               VALUES (1, 1, 1, 0, 1)'''
        )

        conn.commit()
        print('测试数据插入完成')

    except Exception as e:
        print(f'测试数据插入失败: {e}')
        conn.rollback()
        raise
    finally:
        conn.close()
