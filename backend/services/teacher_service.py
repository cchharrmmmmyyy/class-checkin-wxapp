from datetime import datetime
from dao import user_dao


class TeacherService:

    @staticmethod
    def appoint_monitor(student_id, teacher_class):
        student = user_dao.get_user_by_id(student_id)

        if not student:
            return {
                'success': False,
                'message': '未找到该学生'
            }

        if student['class'] != teacher_class:
            return {
                'success': False,
                'message': '该学生不在您的班级中'
            }

        if student['role'] != 'student':
            return {
                'success': False,
                'message': '只有学生才能被任命为班委'
            }

        user_dao.update_user_role(student_id, 'monitor')

        return {
            'success': True,
            'message': '任命班委成功',
            'data': {
                'student_name': student['username'],
                'student_id': student['user_id'],
                'class': student['class'],
                'appointed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }

    @staticmethod
    def remove_monitor(student_id, teacher_class):
        student = user_dao.get_user_by_id(student_id)

        if not student:
            return {
                'success': False,
                'message': '未找到该学生'
            }

        if student['class'] != teacher_class:
            return {
                'success': False,
                'message': '该学生不在您的班级中'
            }

        if student['role'] != 'monitor':
            return {
                'success': False,
                'message': '该学生不是班委'
            }

        user_dao.update_user_role(student_id, 'student')

        return {
            'success': True,
            'message': '移除班委成功',
            'data': {
                'student_name': student['username'],
                'student_id': student['user_id'],
                'class': student['class'],
                'removed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }

    @staticmethod
    def get_monitors(class_name):
        monitors = user_dao.get_monitors_by_class(class_name)
        return [
            {'username': m['username'], 'user_id': m['user_id']}
            for m in monitors
        ]

    @staticmethod
    def get_students(class_name):
        students = user_dao.get_users_by_class(class_name)
        return [
            {'username': s['username'], 'user_id': s['user_id'], 'role': s['role']}
            for s in students
        ]

    @staticmethod
    def get_class_list():
        return user_dao.get_all_classes()
