"""教学安排管理服务。"""

import sqlite3

from dao.class_dao import ClassDAO
from dao.class_teacher_dao import ClassTeacherDAO
from dao.user_dao import UserDAO
from utils.db import get_connection
from utils.exceptions import ServiceException
from utils.serializers import to_datetime_str
from utils.pagination import paginate, normalize_pagination

class_dao = ClassDAO()
class_teacher_dao = ClassTeacherDAO()
user_dao = UserDAO()


def _serialize_assignment(item):
    return {
        'class_name': item.class_name,
        'teacher_id': item.teacher_id,
        'semester': item.semester,
        'created_at': to_datetime_str(item.created_at),
        'deleted_at': to_datetime_str(item.deleted_at),
    }


class AdminTeachingService:

    @staticmethod
    def list_teaching_assignments(class_name=None, teacher_id=None, semester=None, page=1, size=20, include_deleted=False):
        page, size, offset = normalize_pagination(page, size)
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
        items = [_serialize_assignment(item) for item in records]
        return paginate(items, total, page, size)

    @staticmethod
    def create_teaching_assignment(class_name, teacher_id, semester=None):
        if not class_name or not teacher_id:
            raise ServiceException('class_name 和 teacher_id 不能为空', code=7016)
        target_class = class_dao.get_by_id(class_name)
        if not target_class or target_class.deleted_at:
            raise ServiceException('班级不存在或已删除', code=7002, http_status=404)
        teacher = user_dao.get_by_id(teacher_id)
        if not teacher or teacher.deleted_at or teacher.role != 'teacher':
            raise ServiceException('教师不存在或角色不正确', code=7020, http_status=404)

        existing = class_teacher_dao.get_by_id(class_name, teacher_id)
        if existing and not existing.deleted_at:
            raise ServiceException('该教师已绑定到该班级', code=7018, http_status=409)

        try:
            if existing and existing.deleted_at:
                class_teacher_dao.update(class_name, teacher_id, {'semester': semester, 'deleted_at': None})
            else:
                class_teacher_dao.create({'class_name': class_name, 'teacher_id': teacher_id, 'semester': semester})
        except sqlite3.IntegrityError:
            raise ServiceException('任课关系创建失败', code=7018)

        return {
            'success': True,
            'message': '任课关系创建成功',
            'assignment': {'class_name': class_name, 'teacher_id': teacher_id, 'semester': semester, 'active': True},
        }

    @staticmethod
    def delete_teaching_assignment(class_name, teacher_id):
        existing = class_teacher_dao.get_by_id(class_name, teacher_id)
        if not existing or existing.deleted_at:
            raise ServiceException('任课关系不存在', code=7019, http_status=404)
        class_teacher_dao.delete(class_name, teacher_id)
        return {'success': True, 'message': '任课关系移除成功'}

    @staticmethod
    def update_teaching_assignment(class_name, teacher_id, semester):
        existing = class_teacher_dao.get_by_id(class_name, teacher_id)
        if not existing or existing.deleted_at:
            raise ServiceException('任课关系不存在', code=7019, http_status=404)

        class_teacher_dao.update(class_name, teacher_id, {'semester': semester})
        return {
            'success': True,
            'message': '任课关系更新成功',
            'assignment': {'class_name': class_name, 'teacher_id': teacher_id, 'semester': semester},
        }
