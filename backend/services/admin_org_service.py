"""组织架构管理服务：校区/院系/专业/年级/班级 CRUD。"""

import sqlite3

from dao.campus_dao import CampusDAO
from dao.department_dao import DepartmentDAO
from dao.major_dao import MajorDAO
from dao.grade_dao import GradeDAO
from dao.class_dao import ClassDAO
from utils.db import get_connection
from utils.exceptions import ServiceException
from utils.serializers import to_datetime_str
from utils.pagination import paginate, normalize_pagination

campus_dao = CampusDAO()
department_dao = DepartmentDAO()
major_dao = MajorDAO()
grade_dao = GradeDAO()
class_dao = ClassDAO()


def _serialize_campus(item):
    return {
        'id': item.id,
        'name': item.name,
        'address': item.address,
        'created_at': to_datetime_str(item.created_at),
        'deleted_at': None,
    }


def _serialize_department(row):
    return {
        'id': row['id'],
        'campus_id': row['campus_id'],
        'name': row['name'],
        'code': row['code'],
        'campus_name': row['campus_name'],
        'created_at': to_datetime_str(row['created_at']),
        'deleted_at': None,
    }


def _serialize_major(row):
    return {
        'id': row['id'],
        'department_id': row['department_id'],
        'name': row['name'],
        'code': row['code'],
        'department_name': row['department_name'],
        'campus_id': row['campus_id'],
        'campus_name': row['campus_name'],
        'created_at': to_datetime_str(row['created_at']),
        'deleted_at': None,
    }


def _serialize_grade(row):
    return {
        'id': row['id'],
        'major_id': row['major_id'],
        'year': row['year'],
        'name': row['name'],
        'major_name': row['major_name'],
        'department_id': row['department_id'],
        'department_name': row['department_name'],
        'campus_id': row['campus_id'],
        'campus_name': row['campus_name'],
        'created_at': to_datetime_str(row['created_at']),
        'deleted_at': None,
    }


def _serialize_class(row):
    return {
        'class_name': row['class_name'],
        'grade_id': row['grade_id'],
        'grade_name': row['grade_name'],
        'major_name': row['major_name'],
        'created_at': to_datetime_str(row['created_at']),
        'deleted_at': to_datetime_str(row['deleted_at']) if row['deleted_at'] else None,
    }


class AdminOrgService:

    # ---- 校区 ----

    @staticmethod
    def list_campuses(name=None, page=1, size=20):
        page, size, offset = normalize_pagination(page, size)
        where = None
        params = ()
        if name:
            where = 'name LIKE ?'
            params = (f'%{name}%',)
        total = len(campus_dao.get_list(where=where, params=params))
        records = campus_dao.get_list(where=where, params=params, limit=size, offset=offset)
        items = [_serialize_campus(item) for item in records]
        return paginate(items, total, page, size)

    @staticmethod
    def save_campus(campus_id, name, address):
        if not name:
            raise ServiceException('校区名称不能为空', code=7003)
        payload = {'name': name, 'address': address}
        try:
            if campus_id is None:
                new_id = campus_dao.create(payload)
                return {'success': True, 'message': '校区创建成功', 'id': new_id}
            updated = campus_dao.update(campus_id, payload)
            if not updated:
                raise ServiceException('校区不存在', code=7004, http_status=404)
            return {'success': True, 'message': '校区更新成功', 'id': campus_id}
        except sqlite3.IntegrityError:
            raise ServiceException('校区名称已存在或关联数据无效', code=7005)

    @staticmethod
    def delete_campus(campus_id):
        deleted = campus_dao.delete(campus_id)
        if not deleted:
            raise ServiceException('校区不存在', code=7004, http_status=404)
        return {'success': True, 'message': '校区删除成功'}

    # ---- 院系 ----

    @staticmethod
    def list_departments(campus_id=None, name=None, page=1, size=20):
        page, size, offset = normalize_pagination(page, size)
        conditions = []
        params = []
        if campus_id is not None:
            conditions.append('d.campus_id = ?')
            params.append(campus_id)
        if name:
            conditions.append('d.name LIKE ?')
            params.append(f'%{name}%')

        base_sql = 'FROM departments d JOIN campuses c ON c.id = d.campus_id'
        where_clause = ''
        if conditions:
            where_clause = ' WHERE ' + ' AND '.join(conditions)

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f'SELECT COUNT(*) {base_sql}{where_clause}', tuple(params))
            total = cursor.fetchone()[0]

            cursor.execute(
                f'SELECT d.*, c.name AS campus_name'
                f' {base_sql}{where_clause}'
                f' ORDER BY d.id'
                f' LIMIT {size} OFFSET {offset}',
                tuple(params),
            )
            items = [_serialize_department(row) for row in cursor.fetchall()]
            return paginate(items, total, page, size)
        finally:
            conn.close()

    @staticmethod
    def save_department(department_id, campus_id, name, code):
        if not campus_id or not name:
            raise ServiceException('campus_id 和 name 不能为空', code=7006)
        if not campus_dao.get_by_id(campus_id):
            raise ServiceException('所属校区不存在', code=7004, http_status=404)
        payload = {'campus_id': campus_id, 'name': name, 'code': code}
        try:
            if department_id is None:
                new_id = department_dao.create(payload)
                return {'success': True, 'message': '院系创建成功', 'id': new_id}
            updated = department_dao.update(department_id, payload)
            if not updated:
                raise ServiceException('院系不存在', code=7007, http_status=404)
            return {'success': True, 'message': '院系更新成功', 'id': department_id}
        except sqlite3.IntegrityError:
            raise ServiceException('院系名称已存在或关联数据无效', code=7008)

    @staticmethod
    def delete_department(department_id):
        deleted = department_dao.delete(department_id)
        if not deleted:
            raise ServiceException('院系不存在', code=7007, http_status=404)
        return {'success': True, 'message': '院系删除成功'}

    # ---- 专业 ----

    @staticmethod
    def list_majors(campus_id=None, department_id=None, name=None, page=1, size=20):
        page, size, offset = normalize_pagination(page, size)
        conditions = []
        params = []
        if campus_id is not None:
            conditions.append('d.campus_id = ?')
            params.append(campus_id)
        if department_id is not None:
            conditions.append('m.department_id = ?')
            params.append(department_id)
        if name:
            conditions.append('m.name LIKE ?')
            params.append(f'%{name}%')

        base_sql = (
            'FROM majors m'
            ' JOIN departments d ON d.id = m.department_id'
            ' JOIN campuses c ON c.id = d.campus_id'
        )
        where_clause = ''
        if conditions:
            where_clause = ' WHERE ' + ' AND '.join(conditions)

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f'SELECT COUNT(*) {base_sql}{where_clause}', tuple(params))
            total = cursor.fetchone()[0]

            cursor.execute(
                f'SELECT m.*, d.name AS department_name, d.campus_id AS campus_id, c.name AS campus_name'
                f' {base_sql}{where_clause}'
                f' ORDER BY m.id'
                f' LIMIT {size} OFFSET {offset}',
                tuple(params),
            )
            items = [_serialize_major(row) for row in cursor.fetchall()]
            return paginate(items, total, page, size)
        finally:
            conn.close()

    @staticmethod
    def save_major(major_id, department_id, name, code):
        if not department_id or not name:
            raise ServiceException('department_id 和 name 不能为空', code=7009)
        if not department_dao.get_by_id(department_id):
            raise ServiceException('所属院系不存在', code=7007, http_status=404)
        payload = {'department_id': department_id, 'name': name, 'code': code}
        try:
            if major_id is None:
                new_id = major_dao.create(payload)
                return {'success': True, 'message': '专业创建成功', 'id': new_id}
            updated = major_dao.update(major_id, payload)
            if not updated:
                raise ServiceException('专业不存在', code=7010, http_status=404)
            return {'success': True, 'message': '专业更新成功', 'id': major_id}
        except sqlite3.IntegrityError:
            raise ServiceException('专业名称已存在或关联数据无效', code=7011)

    @staticmethod
    def delete_major(major_id):
        deleted = major_dao.delete(major_id)
        if not deleted:
            raise ServiceException('专业不存在', code=7010, http_status=404)
        return {'success': True, 'message': '专业删除成功'}

    # ---- 年级 ----

    @staticmethod
    def list_grades(campus_id=None, department_id=None, major_id=None, year=None, page=1, size=20):
        page, size, offset = normalize_pagination(page, size)
        conditions = []
        params = []
        if campus_id is not None:
            conditions.append('d.campus_id = ?')
            params.append(campus_id)
        if department_id is not None:
            conditions.append('m.department_id = ?')
            params.append(department_id)
        if major_id is not None:
            conditions.append('g.major_id = ?')
            params.append(major_id)
        if year is not None:
            conditions.append('g.year = ?')
            params.append(year)

        base_sql = (
            'FROM grades g'
            ' JOIN majors m ON m.id = g.major_id'
            ' JOIN departments d ON d.id = m.department_id'
            ' JOIN campuses c ON c.id = d.campus_id'
        )
        where_clause = ''
        if conditions:
            where_clause = ' WHERE ' + ' AND '.join(conditions)

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f'SELECT COUNT(*) {base_sql}{where_clause}', tuple(params))
            total = cursor.fetchone()[0]

            cursor.execute(
                f'SELECT g.id, g.major_id, g.year, g.name, g.created_at,'
                f' m.name AS major_name, d.id AS department_id, d.name AS department_name,'
                f' c.id AS campus_id, c.name AS campus_name'
                f' {base_sql}{where_clause}'
                f' ORDER BY g.year DESC, m.name'
                f' LIMIT {size} OFFSET {offset}',
                tuple(params),
            )
            items = [_serialize_grade(row) for row in cursor.fetchall()]
            return paginate(items, total, page, size)
        finally:
            conn.close()

    @staticmethod
    def save_grade(grade_id, major_id, year, name):
        name = (name or '').strip()
        if grade_id is not None:
            existing = grade_dao.get_by_id(grade_id)
            if not existing:
                raise ServiceException('年级不存在', code=7013, http_status=404)
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
            raise ServiceException('major_id、year、name 不能为空', code=7012)
        if not major_dao.get_by_id(major_id):
            raise ServiceException('所属专业不存在', code=7010, http_status=404)
        payload = {'major_id': major_id, 'year': year, 'name': name}
        try:
            if grade_id is None:
                new_id = grade_dao.create(payload)
                return {'success': True, 'message': '年级创建成功', 'id': new_id}
            updated = grade_dao.update(grade_id, payload)
            if not updated:
                raise ServiceException('年级不存在', code=7013, http_status=404)
            return {'success': True, 'message': '年级更新成功', 'id': grade_id}
        except sqlite3.IntegrityError:
            raise ServiceException('同专业下年份重复或关联数据无效', code=7014)

    @staticmethod
    def delete_grade(grade_id):
        deleted = grade_dao.delete(grade_id)
        if not deleted:
            raise ServiceException('年级不存在', code=7013, http_status=404)
        return {'success': True, 'message': '年级删除成功'}

    # ---- 班级 ----

    @staticmethod
    def list_classes(grade_id=None, class_name=None, page=1, size=20, include_deleted=False):
        page, size, offset = normalize_pagination(page, size)
        conditions = []
        params = []
        if grade_id is not None:
            conditions.append('cl.grade_id = ?')
            params.append(grade_id)
        if class_name:
            conditions.append('cl.class_name LIKE ?')
            params.append(f'%{class_name}%')
        if not include_deleted:
            conditions.append('cl.deleted_at IS NULL')

        base_sql = (
            'FROM classes cl'
            ' JOIN grades g ON g.id = cl.grade_id'
            ' JOIN majors m ON m.id = g.major_id'
        )
        where_clause = ''
        if conditions:
            where_clause = ' WHERE ' + ' AND '.join(conditions)

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f'SELECT COUNT(*) {base_sql}{where_clause}', tuple(params))
            total = cursor.fetchone()[0]

            cursor.execute(
                f'SELECT cl.*, g.name AS grade_name, g.year, m.name AS major_name'
                f' {base_sql}{where_clause}'
                f' ORDER BY cl.class_name'
                f' LIMIT {size} OFFSET {offset}',
                tuple(params),
            )
            items = [_serialize_class(row) for row in cursor.fetchall()]
            return paginate(items, total, page, size)
        finally:
            conn.close()

    @staticmethod
    def save_class(target_class_name, class_name, grade_id):
        if not class_name or not grade_id:
            raise ServiceException('class_name 和 grade_id 不能为空', code=7016)
        if not grade_dao.get_by_id(grade_id):
            raise ServiceException('所属年级不存在', code=7013, http_status=404)

        try:
            if target_class_name is None:
                class_dao.create({'class_name': class_name, 'grade_id': grade_id})
                return {'success': True, 'message': '班级创建成功', 'class_name': class_name}

            existing = class_dao.get_by_id(target_class_name)
            if not existing:
                raise ServiceException('班级不存在', code=7002, http_status=404)
            class_dao.update(target_class_name, {'class_name': class_name, 'grade_id': grade_id, 'deleted_at': None})
            return {'success': True, 'message': '班级更新成功', 'class_name': class_name}
        except sqlite3.IntegrityError:
            raise ServiceException('班级名称重复或关联数据无效', code=7017)

    @staticmethod
    def delete_class(class_name):
        deleted = class_dao.delete(class_name)
        if not deleted:
            raise ServiceException('班级不存在', code=7002, http_status=404)
        return {'success': True, 'message': '班级删除成功'}
