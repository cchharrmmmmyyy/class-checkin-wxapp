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


def _serialize_department(item):
    return {
        'id': item.id,
        'campus_id': item.campus_id,
        'name': item.name,
        'code': item.code,
        'created_at': to_datetime_str(item.created_at),
        'deleted_at': None,
    }


def _serialize_major(item):
    return {
        'id': item.id,
        'department_id': item.department_id,
        'name': item.name,
        'code': item.code,
        'created_at': to_datetime_str(item.created_at),
        'deleted_at': None,
    }


def _serialize_grade(item):
    return {
        'id': item.id,
        'major_id': item.major_id,
        'year': item.year,
        'name': item.name,
        'created_at': to_datetime_str(item.created_at),
        'deleted_at': None,
    }


def _serialize_class(item):
    return {
        'class_name': item.class_name,
        'grade_id': item.grade_id,
        'created_at': to_datetime_str(item.created_at),
        'deleted_at': to_datetime_str(item.deleted_at),
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
            conditions.append('campus_id = ?')
            params.append(campus_id)
        if name:
            conditions.append('name LIKE ?')
            params.append(f'%{name}%')
        where = ' AND '.join(conditions) if conditions else None
        params_tuple = tuple(params)
        total = len(department_dao.get_list(where=where, params=params_tuple))
        records = department_dao.get_list(where=where, params=params_tuple, limit=size, offset=offset)
        items = [_serialize_department(item) for item in records]
        return paginate(items, total, page, size)

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
    def list_majors(department_id=None, name=None, page=1, size=20):
        page, size, offset = normalize_pagination(page, size)
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
        items = [_serialize_major(item) for item in records]
        return paginate(items, total, page, size)

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
    def list_grades(major_id=None, year=None, page=1, size=20):
        page, size, offset = normalize_pagination(page, size)
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
        items = [_serialize_grade(item) for item in records]
        return paginate(items, total, page, size)

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
        items = [_serialize_class(item) for item in records]
        return paginate(items, total, page, size)

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
