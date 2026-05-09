from datetime import datetime
from dao.user_dao import UserDAO
from utils.exceptions import ServiceException
from utils.pagination import paginate
from utils import error_codes as EC

user_dao = UserDAO()


class TeacherService:

    @staticmethod
    def appoint_monitor(student_id, teacher_class):
        student = user_dao.get_by_id(student_id)

        if not student or student.deleted_at:
            raise ServiceException('未找到该学生', code=EC.USER_NOT_FOUND, http_status=404)

        if student.class_name != teacher_class:
            raise ServiceException('该学生不在您的班级中', code=EC.LEAVE_NOT_IN_CLASS, http_status=403)

        if student.role != 'student':
            raise ServiceException('只有学生才能被任命为班委', code=EC.USER_ROLE_INVALID)

        user_dao.update(student_id, {'role': 'monitor'})

        return {
            'success': True,
            'message': '任命班委成功',
            'data': {
                'student_name': student.username,
                'student_id': student.user_id,
                'class': student.class_name,
                'appointed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }

    @staticmethod
    def remove_monitor(student_id, teacher_class):
        student = user_dao.get_by_id(student_id)

        if not student or student.deleted_at:
            raise ServiceException('未找到该学生', code=EC.USER_NOT_FOUND, http_status=404)

        if student.class_name != teacher_class:
            raise ServiceException('该学生不在您的班级中', code=EC.LEAVE_NOT_IN_CLASS, http_status=403)

        if student.role != 'monitor':
            raise ServiceException('该学生不是班委', code=EC.USER_ROLE_INVALID)

        user_dao.update(student_id, {'role': 'student'})

        return {
            'success': True,
            'message': '移除班委成功',
            'data': {
                'student_name': student.username,
                'student_id': student.user_id,
                'class': student.class_name,
                'removed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }

    @staticmethod
    def get_monitors(class_name, page=1, size=50):
        where = "class_name = ? AND role = 'monitor' AND deleted_at IS NULL"
        params = (class_name,)

        total = user_dao.count(where=where, params=params)
        offset = (page - 1) * size

        monitors = user_dao.get_list(
            where=where,
            params=params,
            order_by="user_id ASC",
            limit=size,
            offset=offset
        )

        items = [
            {'username': m.username, 'user_id': m.user_id}
            for m in monitors
        ]

        return paginate(items, total, page, size)

    @staticmethod
    def get_students(class_name, page=1, size=50):
        where = "class_name = ? AND deleted_at IS NULL"
        params = (class_name,)

        total = user_dao.count(where=where, params=params)
        offset = (page - 1) * size

        students = user_dao.get_list(
            where=where,
            params=params,
            order_by="user_id ASC",
            limit=size,
            offset=offset
        )

        items = [
            {'username': s.username, 'user_id': s.user_id, 'role': s.role}
            for s in students
        ]

        return paginate(items, total, page, size)

    @staticmethod
    def get_class_list():
        conn = user_dao.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT class_name FROM users WHERE class_name IS NOT NULL AND deleted_at IS NULL")
            classes = cursor.fetchall()
            return [class_row[0] for class_row in classes]
        finally:
            conn.close()
