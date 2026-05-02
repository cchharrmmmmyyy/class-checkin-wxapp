import json
import random
import sqlite3
import string
from datetime import date

from config import Config
from dao.campus_dao import CampusDAO
from dao.class_dao import ClassDAO
from dao.class_teacher_dao import ClassTeacherDAO
from dao.department_dao import DepartmentDAO
from dao.grade_dao import GradeDAO
from dao.leave_dao import LeaveDAO
from dao.major_dao import MajorDAO
from dao.punch_dao import PunchDAO
from dao.punch_geofence_dao import PunchGeofenceDAO
from dao.punch_rule_dao import PunchRuleDAO
from dao.punch_time_slot_dao import PunchTimeSlotDAO
from dao.user_dao import UserDAO
from utils.db import get_connection
from utils.exceptions import ServiceException

# 创建DAO实例
user_dao = UserDAO()
punch_dao = PunchDAO()
punch_geofence_dao = PunchGeofenceDAO()
leave_dao = LeaveDAO()
campus_dao = CampusDAO()
department_dao = DepartmentDAO()
major_dao = MajorDAO()
grade_dao = GradeDAO()
class_dao = ClassDAO()
class_teacher_dao = ClassTeacherDAO()
punch_time_slot_dao = PunchTimeSlotDAO()
punch_rule_dao = PunchRuleDAO()


def _generate_random_password(length=None):
    if length is None:
        length = Config.RANDOM_PASSWORD_LENGTH
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


class AdminService:
    @staticmethod
    def _normalize_pagination(page, size):
        if page < 1 or size < 1:
            raise ServiceException('分页参数不合法', code=6001)
        return page, size, (page - 1) * size

    @staticmethod
    def _build_page(items, total, page, size):
        total_pages = (total + size - 1) // size if total else 0
        return {
            'items': items,
            'total': total,
            'page': page,
            'size': size,
            'total_pages': total_pages,
            'has_next': page < total_pages
        }

    @staticmethod
    def _to_time_str(value):
        if value is None:
            return None
        if hasattr(value, 'strftime'):
            return value.strftime('%H:%M:%S')
        return str(value)

    @staticmethod
    def _to_datetime_str(value):
        if value is None:
            return None
        if hasattr(value, 'isoformat'):
            return value.isoformat()
        return str(value)

    @staticmethod
    def _as_bool_int(value, default=1):
        if value is None:
            return default
        return 1 if str(value).lower() in ('1', 'true', 'yes', 'on') else 0

    @staticmethod
    def _load_polygon_coords(value):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                raise ServiceException('polygon_coords 不是合法的 JSON', code=5030)
            return parsed
        return value

    @staticmethod
    def _dump_polygon_coords(value):
        if value is None:
            return None
        if isinstance(value, str):
            # 允许已是字符串的兼容写法
            AdminService._load_polygon_coords(value)
            return value
        return json.dumps(value, ensure_ascii=False)

    @staticmethod
    def _validate_polygon_coords(value):
        coords = AdminService._load_polygon_coords(value)
        if not isinstance(coords, list) or len(coords) < 3:
            raise ServiceException('polygon_coords 至少需要 3 个顶点', code=5031)
        for item in coords:
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                raise ServiceException('polygon_coords 顶点格式必须为 [latitude, longitude]', code=5032)
        return coords

    @staticmethod
    def _serialize_campus(item):
        return {
            'id': item.id,
            'name': item.name,
            'address': item.address,
            'created_at': AdminService._to_datetime_str(item.created_at),
            'deleted_at': None
        }

    @staticmethod
    def _serialize_department(item):
        return {
            'id': item.id,
            'campus_id': item.campus_id,
            'name': item.name,
            'code': item.code,
            'created_at': AdminService._to_datetime_str(item.created_at),
            'deleted_at': None
        }

    @staticmethod
    def _serialize_major(item):
        return {
            'id': item.id,
            'department_id': item.department_id,
            'name': item.name,
            'code': item.code,
            'created_at': AdminService._to_datetime_str(item.created_at),
            'deleted_at': None
        }

    @staticmethod
    def _serialize_grade(item):
        return {
            'id': item.id,
            'major_id': item.major_id,
            'year': item.year,
            'name': item.name,
            'created_at': AdminService._to_datetime_str(item.created_at),
            'deleted_at': None
        }

    @staticmethod
    def _serialize_class(item):
        return {
            'class_name': item.class_name,
            'grade_id': item.grade_id,
            'created_at': AdminService._to_datetime_str(item.created_at),
            'deleted_at': AdminService._to_datetime_str(item.deleted_at)
        }

    @staticmethod
    def _serialize_assignment(item):
        return {
            'class_name': item.class_name,
            'teacher_id': item.teacher_id,
            'semester': item.semester,
            'created_at': AdminService._to_datetime_str(item.created_at),
            'deleted_at': AdminService._to_datetime_str(item.deleted_at)
        }

    @staticmethod
    def _serialize_time_slot(item):
        return {
            'id': item.id,
            'name': item.name,
            'start_time': AdminService._to_time_str(item.start_time),
            'end_time': AdminService._to_time_str(item.end_time),
            'enabled': item.enabled,
            'created_at': AdminService._to_datetime_str(item.created_at),
            'deleted_at': AdminService._to_datetime_str(item.deleted_at)
        }

    @staticmethod
    def _serialize_geofence(item):
        polygon = AdminService._load_polygon_coords(item.polygon_coords) if item.polygon_coords else None
        return {
            'id': item.id,
            'name': item.name,
            'fence_type': item.fence_type,
            'latitude': item.latitude,
            'longitude': item.longitude,
            'radius': item.radius,
            'polygon_coords': polygon,
            'enabled': item.enabled,
            'created_at': AdminService._to_datetime_str(item.created_at),
            'deleted_at': AdminService._to_datetime_str(item.deleted_at)
        }

    @staticmethod
    def _serialize_rule(item):
        return {
            'id': item.id,
            'time_slot_id': item.time_slot_id,
            'geofence_id': item.geofence_id,
            'priority': item.priority,
            'time_enabled': item.time_enabled,
            'location_enabled': item.location_enabled,
            'enabled': item.enabled,
            'created_at': AdminService._to_datetime_str(item.created_at),
            'deleted_at': AdminService._to_datetime_str(item.deleted_at)
        }

    @staticmethod
    def list_users():
        users = user_dao.get_list(where="deleted_at IS NULL")
        return [
            {
                'username': u.username,
                'user_id': u.user_id,
                'role': u.role,
                'class': u.class_name
            }
            for u in users
        ]

    @staticmethod
    def list_users_paginated(class_name=None, role=None, page=1, size=50):
        page, size, offset = AdminService._normalize_pagination(page, size)
        conditions = ["deleted_at IS NULL"]
        params = []

        if class_name:
            conditions.append("class_name = ?")
            params.append(class_name)
        if role:
            conditions.append("role = ?")
            params.append(role)

        where = " AND ".join(conditions)

        total = user_dao.count(where=where, params=tuple(params))

        users = user_dao.get_list(
            where=where,
            params=tuple(params),
            order_by="user_id ASC",
            limit=size,
            offset=offset
        )

        items = [
            {
                'username': u.username,
                'user_id': u.user_id,
                'role': u.role,
                'class': u.class_name
            }
            for u in users
        ]
        return AdminService._build_page(items, total, page, size)

    @staticmethod
    def list_campuses(name=None, page=1, size=20):
        page, size, offset = AdminService._normalize_pagination(page, size)
        where = None
        params = ()
        if name:
            where = 'name LIKE ?'
            params = (f'%{name}%',)
        total = len(campus_dao.get_list(where=where, params=params))
        records = campus_dao.get_list(where=where, params=params, limit=size, offset=offset)
        items = [AdminService._serialize_campus(item) for item in records]
        return AdminService._build_page(items, total, page, size)

    @staticmethod
    def save_campus(campus_id, name, address):
        if not name:
            raise ServiceException('校区名称不能为空', code=5014)
        payload = {'name': name, 'address': address}
        try:
            if campus_id is None:
                new_id = campus_dao.create(payload)
                return {'success': True, 'message': '校区创建成功', 'id': new_id}
            updated = campus_dao.update(campus_id, payload)
            if not updated:
                raise ServiceException('校区不存在', code=5015, http_status=404)
            return {'success': True, 'message': '校区更新成功', 'id': campus_id}
        except sqlite3.IntegrityError:
            raise ServiceException('校区名称已存在或关联数据无效', code=5016)

    @staticmethod
    def delete_campus(campus_id):
        deleted = campus_dao.delete(campus_id)
        if not deleted:
            raise ServiceException('校区不存在', code=5015, http_status=404)
        return {'success': True, 'message': '校区删除成功'}

    @staticmethod
    def list_departments(campus_id=None, name=None, page=1, size=20):
        page, size, offset = AdminService._normalize_pagination(page, size)
        conditions = []
        params = []
        if campus_id is not None:
            conditions.append('campus_id = ?')
            params.append(campus_id)
        if name:
            conditions.append('name LIKE ?')
            params.append(f'%{name}%')
        where = ' AND '.join(conditions) if conditions else None
        params_tuple = tuple(params)
        total = len(department_dao.get_list(where=where, params=params_tuple))
        records = department_dao.get_list(where=where, params=params_tuple, limit=size, offset=offset)
        items = [AdminService._serialize_department(item) for item in records]
        return AdminService._build_page(items, total, page, size)

    @staticmethod
    def save_department(department_id, campus_id, name, code):
        if not campus_id or not name:
            raise ServiceException('campus_id 和 name 不能为空', code=5017)
        if not campus_dao.get_by_id(campus_id):
            raise ServiceException('所属校区不存在', code=5018, http_status=404)
        payload = {'campus_id': campus_id, 'name': name, 'code': code}
        try:
            if department_id is None:
                new_id = department_dao.create(payload)
                return {'success': True, 'message': '院系创建成功', 'id': new_id}
            updated = department_dao.update(department_id, payload)
            if not updated:
                raise ServiceException('院系不存在', code=5019, http_status=404)
            return {'success': True, 'message': '院系更新成功', 'id': department_id}
        except sqlite3.IntegrityError:
            raise ServiceException('院系名称已存在或关联数据无效', code=5020)

    @staticmethod
    def delete_department(department_id):
        deleted = department_dao.delete(department_id)
        if not deleted:
            raise ServiceException('院系不存在', code=5019, http_status=404)
        return {'success': True, 'message': '院系删除成功'}

    @staticmethod
    def list_majors(department_id=None, name=None, page=1, size=20):
        page, size, offset = AdminService._normalize_pagination(page, size)
        conditions = []
        params = []
        if department_id is not None:
            conditions.append('department_id = ?')
            params.append(department_id)
        if name:
            conditions.append('name LIKE ?')
            params.append(f'%{name}%')
        where = ' AND '.join(conditions) if conditions else None
        params_tuple = tuple(params)
        total = len(major_dao.get_list(where=where, params=params_tuple))
        records = major_dao.get_list(where=where, params=params_tuple, limit=size, offset=offset)
        items = [AdminService._serialize_major(item) for item in records]
        return AdminService._build_page(items, total, page, size)

    @staticmethod
    def save_major(major_id, department_id, name, code):
        if not department_id or not name:
            raise ServiceException('department_id 和 name 不能为空', code=5021)
        if not department_dao.get_by_id(department_id):
            raise ServiceException('所属院系不存在', code=5022, http_status=404)
        payload = {'department_id': department_id, 'name': name, 'code': code}
        try:
            if major_id is None:
                new_id = major_dao.create(payload)
                return {'success': True, 'message': '专业创建成功', 'id': new_id}
            updated = major_dao.update(major_id, payload)
            if not updated:
                raise ServiceException('专业不存在', code=5023, http_status=404)
            return {'success': True, 'message': '专业更新成功', 'id': major_id}
        except sqlite3.IntegrityError:
            raise ServiceException('专业名称已存在或关联数据无效', code=5024)

    @staticmethod
    def delete_major(major_id):
        deleted = major_dao.delete(major_id)
        if not deleted:
            raise ServiceException('专业不存在', code=5023, http_status=404)
        return {'success': True, 'message': '专业删除成功'}

    @staticmethod
    def list_grades(major_id=None, year=None, page=1, size=20):
        page, size, offset = AdminService._normalize_pagination(page, size)
        conditions = []
        params = []
        if major_id is not None:
            conditions.append('major_id = ?')
            params.append(major_id)
        if year is not None:
            conditions.append('year = ?')
            params.append(year)
        where = ' AND '.join(conditions) if conditions else None
        params_tuple = tuple(params)
        total = len(grade_dao.get_list(where=where, params=params_tuple))
        records = grade_dao.get_list(where=where, params=params_tuple, limit=size, offset=offset)
        items = [AdminService._serialize_grade(item) for item in records]
        return AdminService._build_page(items, total, page, size)

    @staticmethod
    def save_grade(grade_id, major_id, year, name):
        name = (name or '').strip()
        if grade_id is not None:
            existing = grade_dao.get_by_id(grade_id)
            if not existing:
                raise ServiceException('年级不存在', code=5027, http_status=404)
            if not major_id:
                major_id = existing.major_id
            if not year:
                year = existing.year
            if not name:
                name = (existing.name or '').strip() or f'{year}级'
        else:
            if not name and year:
                name = f'{year}级'

        if not major_id or not year or not name:
            raise ServiceException('major_id、year、name 不能为空', code=5025)
        if not major_dao.get_by_id(major_id):
            raise ServiceException('所属专业不存在', code=5026, http_status=404)
        payload = {'major_id': major_id, 'year': year, 'name': name}
        try:
            if grade_id is None:
                new_id = grade_dao.create(payload)
                return {'success': True, 'message': '年级创建成功', 'id': new_id}
            updated = grade_dao.update(grade_id, payload)
            if not updated:
                raise ServiceException('年级不存在', code=5027, http_status=404)
            return {'success': True, 'message': '年级更新成功', 'id': grade_id}
        except sqlite3.IntegrityError:
            raise ServiceException('同专业下年份重复或关联数据无效', code=5028)

    @staticmethod
    def delete_grade(grade_id):
        deleted = grade_dao.delete(grade_id)
        if not deleted:
            raise ServiceException('年级不存在', code=5027, http_status=404)
        return {'success': True, 'message': '年级删除成功'}

    @staticmethod
    def list_classes(grade_id=None, class_name=None, page=1, size=20, include_deleted=False):
        page, size, offset = AdminService._normalize_pagination(page, size)
        conditions = []
        params = []
        if grade_id is not None:
            conditions.append('grade_id = ?')
            params.append(grade_id)
        if class_name:
            conditions.append('class_name LIKE ?')
            params.append(f'%{class_name}%')
        if not include_deleted:
            conditions.append('deleted_at IS NULL')
        where = ' AND '.join(conditions) if conditions else None
        params_tuple = tuple(params)
        total = len(class_dao.get_list(where=where, params=params_tuple))
        records = class_dao.get_list(where=where, params=params_tuple, limit=size, offset=offset)
        items = [AdminService._serialize_class(item) for item in records]
        return AdminService._build_page(items, total, page, size)

    @staticmethod
    def save_class(target_class_name, class_name, grade_id):
        if not class_name or not grade_id:
            raise ServiceException('class_name 和 grade_id 不能为空', code=5029)
        if not grade_dao.get_by_id(grade_id):
            raise ServiceException('所属年级不存在', code=5030, http_status=404)
        conn = get_connection()
        try:
            cursor = conn.cursor()
            if target_class_name is None:
                cursor.execute(
                    'INSERT INTO classes (class_name, grade_id) VALUES (?, ?)',
                    (class_name, grade_id)
                )
                conn.commit()
                return {'success': True, 'message': '班级创建成功', 'class_name': class_name}

            cursor.execute('SELECT class_name FROM classes WHERE class_name = ?', (target_class_name,))
            if cursor.fetchone() is None:
                raise ServiceException('班级不存在', code=5031, http_status=404)
            cursor.execute(
                'UPDATE classes SET class_name = ?, grade_id = ?, deleted_at = NULL WHERE class_name = ?',
                (class_name, grade_id, target_class_name)
            )
            conn.commit()
            return {'success': True, 'message': '班级更新成功', 'class_name': class_name}
        except sqlite3.IntegrityError:
            raise ServiceException('班级名称重复或关联数据无效', code=5032)
        finally:
            conn.close()

    @staticmethod
    def delete_class(class_name):
        deleted = class_dao.delete(class_name)
        if not deleted:
            raise ServiceException('班级不存在', code=5031, http_status=404)
        return {'success': True, 'message': '班级删除成功'}

    @staticmethod
    def list_teaching_assignments(class_name=None, teacher_id=None, semester=None, page=1, size=20, include_deleted=False):
        page, size, offset = AdminService._normalize_pagination(page, size)
        conditions = []
        params = []
        if class_name:
            conditions.append('class_name = ?')
            params.append(class_name)
        if teacher_id:
            conditions.append('teacher_id = ?')
            params.append(teacher_id)
        if semester:
            conditions.append('semester = ?')
            params.append(semester)
        if not include_deleted:
            conditions.append('deleted_at IS NULL')
        where = ' AND '.join(conditions) if conditions else None
        params_tuple = tuple(params)
        total = len(class_teacher_dao.get_list(where=where, params=params_tuple))
        records = class_teacher_dao.get_list(where=where, params=params_tuple, limit=size, offset=offset)
        items = [AdminService._serialize_assignment(item) for item in records]
        return AdminService._build_page(items, total, page, size)

    @staticmethod
    def create_teaching_assignment(class_name, teacher_id, semester=None):
        if not class_name or not teacher_id:
            raise ServiceException('class_name 和 teacher_id 不能为空', code=5033)
        target_class = class_dao.get_by_id(class_name)
        if not target_class or target_class.deleted_at:
            raise ServiceException('班级不存在或已删除', code=5034, http_status=404)
        teacher = user_dao.get_by_id(teacher_id)
        if not teacher or teacher.deleted_at or teacher.role != 'teacher':
            raise ServiceException('教师不存在或角色不正确', code=5035, http_status=404)

        existing = class_teacher_dao.get_by_id(class_name, teacher_id)
        if existing and not existing.deleted_at:
            raise ServiceException('该教师已绑定到该班级', code=5036, http_status=409)

        conn = get_connection()
        try:
            cursor = conn.cursor()
            if existing and existing.deleted_at:
                cursor.execute(
                    'UPDATE class_teachers SET semester = ?, deleted_at = NULL WHERE class_name = ? AND teacher_id = ?',
                    (semester, class_name, teacher_id)
                )
            else:
                cursor.execute(
                    'INSERT INTO class_teachers (class_name, teacher_id, semester) VALUES (?, ?, ?)',
                    (class_name, teacher_id, semester)
                )
            conn.commit()
        finally:
            conn.close()

        return {
            'success': True,
            'message': '任课关系创建成功',
            'assignment': {'class_name': class_name, 'teacher_id': teacher_id, 'semester': semester, 'active': True}
        }

    @staticmethod
    def delete_teaching_assignment(class_name, teacher_id):
        existing = class_teacher_dao.get_by_id(class_name, teacher_id)
        if not existing or existing.deleted_at:
            raise ServiceException('任课关系不存在', code=5037, http_status=404)
        class_teacher_dao.delete(class_name, teacher_id)
        return {'success': True, 'message': '任课关系移除成功'}

    @staticmethod
    def update_teaching_assignment(class_name, teacher_id, semester):
        existing = class_teacher_dao.get_by_id(class_name, teacher_id)
        if not existing or existing.deleted_at:
            raise ServiceException('任课关系不存在', code=5037, http_status=404)
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE class_teachers SET semester = ? WHERE class_name = ? AND teacher_id = ?',
                (semester, class_name, teacher_id)
            )
            conn.commit()
        finally:
            conn.close()
            
        return {
            'success': True,
            'message': '任课关系更新成功',
            'assignment': {'class_name': class_name, 'teacher_id': teacher_id, 'semester': semester}
        }

    @staticmethod
    def list_time_slots(name=None, enabled=None, page=1, size=20, include_deleted=False):
        page, size, offset = AdminService._normalize_pagination(page, size)
        conditions = []
        params = []
        if name:
            conditions.append('name LIKE ?')
            params.append(f'%{name}%')
        if enabled is not None:
            conditions.append('enabled = ?')
            params.append(AdminService._as_bool_int(enabled))
        if not include_deleted:
            conditions.append('deleted_at IS NULL')
        where = ' AND '.join(conditions) if conditions else None
        params_tuple = tuple(params)
        total = len(punch_time_slot_dao.get_list(where=where, params=params_tuple))
        records = punch_time_slot_dao.get_list(where=where, params=params_tuple, limit=size, offset=offset)
        items = [AdminService._serialize_time_slot(item) for item in records]
        return AdminService._build_page(items, total, page, size)

    @staticmethod
    def save_time_slot(slot_id, name, start_time, end_time, enabled=1):
        if not name or not start_time or not end_time:
            raise ServiceException('name、start_time、end_time 不能为空', code=5038)
        payload = {
            'name': name,
            'start_time': start_time,
            'end_time': end_time,
            'enabled': AdminService._as_bool_int(enabled)
        }
        if slot_id is None:
            new_id = punch_time_slot_dao.create(payload)
            return {'success': True, 'message': '时段创建成功', 'id': new_id}

        current = punch_time_slot_dao.get_by_id(slot_id)
        if not current or current.deleted_at:
            raise ServiceException('时段不存在', code=5039, http_status=404)
        punch_time_slot_dao.update(slot_id, payload)
        return {'success': True, 'message': '时段更新成功', 'id': slot_id}

    @staticmethod
    def delete_time_slot(slot_id):
        deleted = punch_time_slot_dao.delete(slot_id)
        if not deleted:
            raise ServiceException('时段不存在', code=5039, http_status=404)
        return {'success': True, 'message': '时段删除成功'}

    @staticmethod
    def list_geofences(name=None, enabled=None, fence_type=None, page=1, size=20, include_deleted=False):
        page, size, offset = AdminService._normalize_pagination(page, size)
        conditions = []
        params = []
        if name:
            conditions.append('name LIKE ?')
            params.append(f'%{name}%')
        if enabled is not None:
            conditions.append('enabled = ?')
            params.append(AdminService._as_bool_int(enabled))
        if fence_type:
            conditions.append('fence_type = ?')
            params.append(fence_type)
        if not include_deleted:
            conditions.append('deleted_at IS NULL')
        where = ' AND '.join(conditions) if conditions else None
        params_tuple = tuple(params)
        total = len(punch_geofence_dao.get_list(where=where, params=params_tuple))
        records = punch_geofence_dao.get_list(where=where, params=params_tuple, limit=size, offset=offset)
        items = [AdminService._serialize_geofence(item) for item in records]
        return AdminService._build_page(items, total, page, size)

    @staticmethod
    def save_geofence(geofence_id, name, fence_type, latitude=None, longitude=None, radius=None, polygon_coords=None, enabled=1):
        if not name or not fence_type:
            raise ServiceException('name 和 fence_type 不能为空', code=5040)
        if fence_type not in ('circle', 'polygon'):
            raise ServiceException('fence_type 仅支持 circle 或 polygon', code=5041)

        payload = {
            'name': name,
            'fence_type': fence_type,
            'enabled': AdminService._as_bool_int(enabled)
        }
        if fence_type == 'circle':
            if latitude is None or longitude is None or radius is None:
                raise ServiceException('circle 围栏必须提供 latitude、longitude、radius', code=5042)
            payload.update({
                'latitude': latitude,
                'longitude': longitude,
                'radius': radius,
                'polygon_coords': None
            })
        else:
            coords = AdminService._validate_polygon_coords(polygon_coords)
            payload.update({
                'latitude': None,
                'longitude': None,
                'radius': None,
                'polygon_coords': AdminService._dump_polygon_coords(coords)
            })

        if geofence_id is None:
            new_id = punch_geofence_dao.create(payload)
            return {'success': True, 'message': '围栏创建成功', 'id': new_id}

        current = punch_geofence_dao.get_by_id(geofence_id)
        if not current or current.deleted_at:
            raise ServiceException('围栏不存在', code=5043, http_status=404)
        punch_geofence_dao.update(geofence_id, payload)
        return {'success': True, 'message': '围栏更新成功', 'id': geofence_id}

    @staticmethod
    def delete_geofence(geofence_id):
        deleted = punch_geofence_dao.delete(geofence_id)
        if not deleted:
            raise ServiceException('围栏不存在', code=5043, http_status=404)
        return {'success': True, 'message': '围栏删除成功'}

    @staticmethod
    def _ensure_rule_refs(time_slot_id, geofence_id):
        slot = punch_time_slot_dao.get_by_id(time_slot_id)
        if not slot or slot.deleted_at:
            raise ServiceException('关联时段不存在', code=5044, http_status=404)
        fence = punch_geofence_dao.get_by_id(geofence_id)
        if not fence or fence.deleted_at:
            raise ServiceException('关联围栏不存在', code=5045, http_status=404)

    @staticmethod
    def _validate_rule_priority_conflict(priority, rule_id=None):
        conflicts = punch_rule_dao.get_list(where='priority = ? AND deleted_at IS NULL', params=(priority,))
        for item in conflicts:
            if rule_id is None or item.id != rule_id:
                raise ServiceException('priority 冲突，请使用唯一优先级', code=5046, http_status=409)

    @staticmethod
    def list_punch_rules(enabled=None, time_slot_id=None, geofence_id=None, page=1, size=20, include_deleted=False):
        page, size, offset = AdminService._normalize_pagination(page, size)
        conditions = []
        params = []
        if enabled is not None:
            conditions.append('enabled = ?')
            params.append(AdminService._as_bool_int(enabled))
        if time_slot_id is not None:
            conditions.append('time_slot_id = ?')
            params.append(time_slot_id)
        if geofence_id is not None:
            conditions.append('geofence_id = ?')
            params.append(geofence_id)
        if not include_deleted:
            conditions.append('deleted_at IS NULL')
        where = ' AND '.join(conditions) if conditions else None
        params_tuple = tuple(params)
        total = len(punch_rule_dao.get_list(where=where, params=params_tuple))
        records = punch_rule_dao.get_list(where=where, params=params_tuple, limit=size, offset=offset)
        items = [AdminService._serialize_rule(item) for item in records]
        return AdminService._build_page(items, total, page, size)

    @staticmethod
    def save_punch_rule(rule_id, time_slot_id, geofence_id, priority=100, time_enabled=1, location_enabled=1, enabled=1):
        if time_slot_id is None or geofence_id is None:
            raise ServiceException('time_slot_id 和 geofence_id 不能为空', code=5047)
        AdminService._ensure_rule_refs(time_slot_id, geofence_id)
        AdminService._validate_rule_priority_conflict(priority, rule_id)
        payload = {
            'time_slot_id': time_slot_id,
            'geofence_id': geofence_id,
            'priority': priority,
            'time_enabled': AdminService._as_bool_int(time_enabled),
            'location_enabled': AdminService._as_bool_int(location_enabled),
            'enabled': AdminService._as_bool_int(enabled)
        }
        if rule_id is None:
            new_id = punch_rule_dao.create(payload)
            return {'success': True, 'message': '规则创建成功', 'id': new_id}

        current = punch_rule_dao.get_by_id(rule_id)
        if not current or current.deleted_at:
            raise ServiceException('规则不存在', code=5048, http_status=404)
        punch_rule_dao.update(rule_id, payload)
        return {'success': True, 'message': '规则更新成功', 'id': rule_id}

    @staticmethod
    def delete_punch_rule(rule_id):
        deleted = punch_rule_dao.delete(rule_id)
        if not deleted:
            raise ServiceException('规则不存在', code=5048, http_status=404)
        return {'success': True, 'message': '规则删除成功'}

    @staticmethod
    def save_user(username, user_id, password, role, class_name):
        valid_roles = ('admin', 'teacher', 'student', 'monitor')
        if role not in valid_roles:
            raise ServiceException(f'角色必须是 {"、".join(valid_roles)} 之一', code=5001)

        if role == 'admin':
            if class_name:
                raise ServiceException('管理员不应设置班级', code=5002)
        elif not class_name:
            raise ServiceException('老师、学生、班委必须设置班级', code=5003)

        existing_user = user_dao.get_by_id(user_id)

        if existing_user:
            data = {
                'username': username,
                'role': role,
                'class_name': class_name
            }
            if password:
                data['password'] = password
            user_dao.update(user_id, data)
            message = '用户更新成功'
        else:
            data = {
                'user_id': user_id,
                'username': username,
                'password': password,
                'real_name': username,  # 使用username作为real_name
                'role': role,
                'class_name': class_name,
                'student_id': user_id  # 使用user_id作为student_id
            }
            user_dao.create(data)
            message = '用户添加成功'

        return {'success': True, 'message': message}

    @staticmethod
    def delete_user(user_id):
        target = user_dao.get_by_id(user_id)

        if not target or target.deleted_at:
            raise ServiceException('用户不存在', code=5004, http_status=404)

        if target.role == 'admin':
            admins = user_dao.get_list(where="role = 'admin' AND deleted_at IS NULL")
            if len(admins) <= 1:
                raise ServiceException('不能删除最后一个管理员账户', code=5005, http_status=403)

        success = user_dao.delete(user_id)

        if not success:
            raise ServiceException('用户不存在', code=5006, http_status=404)

        return {'success': True, 'message': '用户删除成功'}

    @staticmethod
    def reset_password(user_id):
        target_user = user_dao.get_by_id(user_id)

        if not target_user or target_user.deleted_at:
            raise ServiceException('用户不存在', code=5007, http_status=404)

        if target_user.role == 'admin':
            raise ServiceException('不允许重置管理员账户密码', code=5008, http_status=403)

        new_password = _generate_random_password()
        user_dao.update(user_id, {'password': new_password})

        return {
            'success': True,
            'message': '密码重置成功',
            'new_password': new_password
        }

    @staticmethod
    def get_attendance_records(username=None, user_id=None, start_date=None, end_date=None, leave_status=None, page=1, size=50):
        page, size, offset = AdminService._normalize_pagination(page, size)
        # 构建条件
        punch_conditions = []
        punch_params = []
        leave_conditions = []
        leave_params = []

        if user_id:
            punch_conditions.append("user_id = ?")
            punch_params.append(user_id)
            leave_conditions.append("user_id = ?")
            leave_params.append(user_id)

        if start_date:
            punch_conditions.append("punch_date >= ?")
            punch_params.append(start_date)
            leave_conditions.append("leave_start_date >= ?")
            leave_params.append(start_date)

        if end_date:
            punch_conditions.append("punch_date <= ?")
            punch_params.append(end_date)
            leave_conditions.append("leave_end_date <= ?")
            leave_params.append(end_date)

        if leave_status:
            leave_conditions.append("leave_status = ?")
            leave_params.append(leave_status)

        # 查询打卡记录
        punch_where = " AND ".join(punch_conditions) if punch_conditions else "1=1"
        punches = punch_dao.get_list(where=punch_where, params=tuple(punch_params))

        # 查询请假记录
        leave_where = " AND ".join(leave_conditions) if leave_conditions else "1=1"
        leaves = leave_dao.get_list(where=leave_where, params=tuple(leave_params))

        # 合并记录
        all_records = []

        # 添加打卡记录
        for punch in punches:
            user = user_dao.get_by_id(punch.user_id)
            all_records.append({
                'id': punch.id,
                'username': user.username if user else '',
                'user_id': punch.user_id,
                'punch_date': punch.punch_date,
                'leave_start_date': None,
                'leave_end_date': None,
                'leave_status': None
            })

        # 添加请假记录
        for leave in leaves:
            user = user_dao.get_by_id(leave.user_id)
            all_records.append({
                'id': leave.id,
                'username': user.username if user else '',
                'user_id': leave.user_id,
                'punch_date': None,
                'leave_start_date': leave.leave_start_date,
                'leave_end_date': leave.leave_end_date,
                'leave_status': leave.leave_status
            })

        # 按日期排序
        all_records.sort(key=lambda x: x['punch_date'] or x['leave_start_date'], reverse=True)

        total = len(all_records)
        items = all_records[offset:offset + size]

        return AdminService._build_page(items, total, page, size)

    @staticmethod
    def save_punch_record(record_id, user_id, punch_date, punch_time='12:00:00', latitude=0.0, longitude=0.0):
        if not user_id:
            raise ServiceException('用户ID不能为空', code=5009)
        if not punch_date:
            raise ServiceException('打卡日期不能为空', code=5010)
        target_user = user_dao.get_by_id(user_id)
        if not target_user or target_user.deleted_at:
            raise ServiceException('用户不存在', code=5011, http_status=404)
        payload = {
            'user_id': user_id,
            'punch_date': punch_date,
            'punch_time': punch_time or '12:00:00',
            'latitude': latitude if latitude is not None else 0.0,
            'longitude': longitude if longitude is not None else 0.0
        }
        if record_id:
            target = punch_dao.get_by_id(record_id)
            if not target:
                raise ServiceException('打卡记录不存在', code=5012, http_status=404)
            punch_dao.update(record_id, payload)
            return {'success': True, 'message': '打卡记录更新成功', 'id': record_id}
        new_id = punch_dao.create(payload)
        return {'success': True, 'message': '打卡记录添加成功', 'id': new_id}

    @staticmethod
    def save_leave_record(record_id, user_id, leave_start_date=None, leave_end_date=None, leave_status='pending', leave_type='personal', leave_reason=None):
        if record_id:
            target = leave_dao.get_by_id(record_id)
            if not target or target.deleted_at:
                raise ServiceException('请假记录不存在', code=5013, http_status=404)
            valid_statuses = ('pending', 'approved', 'rejected')
            if leave_status not in valid_statuses:
                raise ServiceException(f'请假状态必须是 {"、".join(valid_statuses)} 之一', code=5014)
            leave_dao.update(record_id, {'leave_status': leave_status, 'approved_by': None})
            return {'success': True, 'message': '请假记录更新成功', 'id': record_id}

        if not user_id or not leave_start_date or not leave_end_date:
            raise ServiceException('用户ID和请假起止日期不能为空', code=5015)
        target_user = user_dao.get_by_id(user_id)
        if not target_user or target_user.deleted_at:
            raise ServiceException('用户不存在', code=5011, http_status=404)
        data = {
            'user_id': user_id,
            'leave_start_date': leave_start_date,
            'leave_end_date': leave_end_date,
            'leave_type': leave_type or 'personal',
            'leave_reason': leave_reason
        }
        new_id = leave_dao.create(data)
        if leave_status and leave_status != 'pending':
            leave_dao.update(new_id, {'leave_status': leave_status, 'approved_by': None})
        return {'success': True, 'message': '请假记录添加成功', 'id': new_id}

    @staticmethod
    def save_attendance_record(record_id, user_id, punch_date, leave_start_date, leave_end_date, leave_status):
        # 兼容层：保留历史接口，但写入已拆分到语义单一方法
        has_punch = bool(punch_date)
        has_leave = bool(leave_start_date and leave_end_date)

        if not has_punch and not has_leave:
            raise ServiceException('打卡日期和请假日期不能同时为空', code=5016)

        if has_punch and has_leave:
            raise ServiceException('打卡记录和请假记录不能同时存在', code=5017)

        if has_punch:
            return AdminService.save_punch_record(
                record_id=record_id,
                user_id=user_id,
                punch_date=punch_date
            )
        return AdminService.save_leave_record(
            record_id=record_id,
            user_id=user_id,
            leave_start_date=leave_start_date,
            leave_end_date=leave_end_date,
            leave_status=leave_status
        )

    @staticmethod
    def delete_punch_record(record_id):
        deleted = punch_dao.delete(record_id)
        if not deleted:
            raise ServiceException('打卡记录不存在', code=5012, http_status=404)
        return {'success': True, 'message': '打卡记录删除成功'}

    @staticmethod
    def delete_leave_record(record_id):
        deleted = leave_dao.delete(record_id)
        if not deleted:
            raise ServiceException('请假记录不存在', code=5013, http_status=404)
        return {'success': True, 'message': '请假记录删除成功'}

    @staticmethod
    def delete_attendance_record(record_id):
        # 兼容层：删除仍支持旧路径
        try:
            return AdminService.delete_punch_record(record_id)
        except ServiceException:
            return AdminService.delete_leave_record(record_id)

    @staticmethod
    def get_punch_location():
        geofences = punch_geofence_dao.get_enabled_geofences()

        if not geofences:
            return {'success': True, 'data': None}

        # 返回第一个启用的围栏
        geofence = geofences[0]
        return {
            'success': True,
            'data': {
                'id': geofence.id,
                'name': geofence.name,
                'latitude': geofence.latitude,
                'longitude': geofence.longitude,
                'radius': geofence.radius,
                'enabled': geofence.enabled,
                'fence_type': geofence.fence_type,
                'polygon_coords': AdminService._load_polygon_coords(geofence.polygon_coords) if geofence.polygon_coords else None
            },
            'compatibility': {
                'legacy': True,
                'replacement': '/api/admin/rules/punch-geofences',
                'sunset_date': '2026-07-31'
            }
        }

    @staticmethod
    def save_punch_location(name, latitude, longitude, radius, enabled=1):
        if not name or latitude is None or longitude is None or radius is None:
            raise ServiceException('位置名称、经纬度半径不能为空', code=5049)

        # 禁用所有现有围栏
        existing_geofences = punch_geofence_dao.get_list()
        for geofence in existing_geofences:
            punch_geofence_dao.update(geofence.id, {'enabled': 0})

        # 创建新的围栏
        data = {
            'name': name,
            'fence_type': 'circle',  # 默认圆形围栏
            'latitude': latitude,
            'longitude': longitude,
            'radius': radius,
            'enabled': enabled
        }
        punch_geofence_dao.create(data)

        return {
            'success': True,
            'message': '打卡位置设置成功',
            'compatibility': {
                'legacy': True,
                'replacement': '/api/admin/rules/punch-geofences',
                'sunset_date': '2026-07-31'
            }
        }

    @staticmethod
    def get_dashboard_stats():
        today = date.today().isoformat()

        total_students = user_dao.count_by_role('student')
        present_today = punch_dao.count_by_date(today)
        on_leave_today = leave_dao.count_approved_by_date(today)
        absent_today = total_students - present_today - on_leave_today
        pending_leaves = leave_dao.count_pending()

        geofence = punch_geofence_dao.get_first_enabled()
        geofence_data = None
        if geofence:
            geofence_data = {
                'id': geofence.id,
                'name': geofence.name,
                'latitude': geofence.latitude,
                'longitude': geofence.longitude,
                'radius': geofence.radius,
                'enabled': geofence.enabled
            }

        return {
            'total_students': total_students,
            'present_today': present_today,
            'on_leave_today': on_leave_today,
            'absent_today': absent_today,
            'pending_leaves': pending_leaves,
            'geofence': geofence_data
        }
