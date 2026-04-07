from dao import user_dao, punch_record_dao, location_dao
from db_connection import hash_password
from config import Config
import random
import string


def _generate_random_password(length=None):
    if length is None:
        length = Config.RANDOM_PASSWORD_LENGTH
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


class AdminService:

    @staticmethod
    def list_users():
        users = user_dao.get_all_users()
        return [
            {
                'username': u['username'],
                'user_id': u['user_id'],
                'role': u['role'],
                'class': u['class']
            }
            for u in users
        ]

    @staticmethod
    def save_user(username, user_id, password, role, class_name):
        valid_roles = ('admin', 'teacher', 'student', 'monitor')
        if role not in valid_roles:
            return {
                'success': False,
                'message': f'角色必须是 {", ".join(valid_roles)} 之一'
            }

        if role == 'admin':
            if class_name:
                return {
                    'success': False,
                    'message': '管理员不应设置班级'
                }
        elif not class_name:
            return {
                'success': False,
                'message': '老师、学生、班委必须设置班级'
            }

        existing_user = user_dao.get_user_by_id(user_id)

        if existing_user:
            user_dao.update_user(username, user_id, password, role, class_name)
            message = '用户更新成功'
        else:
            user_dao.create_user(username, user_id, password, role, class_name)
            message = '用户添加成功'

        return {'success': True, 'message': message}

    @staticmethod
    def delete_user(user_id):
        target = user_dao.get_user_by_id(user_id)

        if not target:
            return {'success': False, 'message': '用户不存在'}

        if target['role'] == 'admin':
            if user_dao.count_admins() <= 1:
                return {'success': False, 'message': '不能删除最后一个管理员账户'}

        rowcount = user_dao.delete_user(user_id)

        if rowcount == 0:
            return {'success': False, 'message': '用户不存在'}

        return {'success': True, 'message': '用户删除成功'}

    @staticmethod
    def reset_password(user_id):
        target_user = user_dao.get_user_by_id(user_id)

        if not target_user:
            return {'success': False, 'message': '用户不存在'}

        if target_user['role'] == 'admin':
            return {'success': False, 'message': '不允许重置管理员账户密码'}

        new_password = _generate_random_password()
        user_dao.reset_password(user_id, new_password)

        return {
            'success': True,
            'message': '密码重置成功',
            'new_password': new_password
        }

    @staticmethod
    def get_attendance_records(username=None, user_id=None, start_date=None, end_date=None, leave_status=None):
        records = punch_record_dao.get_all_attendance_records(
            username=username,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            leave_status=leave_status
        )
        return [
            {
                'id': r['id'],
                'username': r['username'],
                'user_id': r['user_id'],
                'punch_date': r['punch_date'],
                'leave_start_date': r['leave_start_date'],
                'leave_end_date': r['leave_end_date'],
                'leave_status': r['leave_status']
            }
            for r in records
        ]

    @staticmethod
    def save_attendance_record(record_id, user_id, punch_date, leave_start_date, leave_end_date, leave_status):
        has_punch = bool(punch_date)
        has_leave = bool(leave_start_date and leave_end_date)

        if not has_punch and not has_leave:
            return {'success': False, 'message': '打卡日期和请假日期不能同时为空'}

        if has_punch and has_leave:
            return {'success': False, 'message': '打卡记录和请假记录不能同时存在'}

        if has_leave:
            valid_statuses = ('pending', 'approved', 'rejected')
            if leave_status not in valid_statuses:
                return {
                    'success': False,
                    'message': f'请假状态必须是 {", ".join(valid_statuses)} 之一'
                }

        if record_id:
            punch_record_dao.update_punch_record(
                record_id, user_id, punch_date,
                leave_start_date, leave_end_date, leave_status
            )
            message = '考勤记录更新成功'
        else:
            punch_record_dao.create_attendance_record(
                user_id, punch_date,
                leave_start_date, leave_end_date, leave_status
            )
            message = '考勤记录添加成功'

        return {'success': True, 'message': message}

    @staticmethod
    def delete_attendance_record(record_id):
        rowcount = punch_record_dao.delete_punch_record(record_id)

        if rowcount == 0:
            return {'success': False, 'message': '考勤记录不存在'}

        return {'success': True, 'message': '考勤记录删除成功'}

    @staticmethod
    def get_punch_location():
        location = location_dao.get_punch_location()

        if not location:
            return {'success': True, 'data': None}

        return {
            'success': True,
            'data': {
                'id': location['id'],
                'name': location['name'],
                'latitude': location['latitude'],
                'longitude': location['longitude'],
                'radius': location['radius'],
                'enabled': location['enabled']
            }
        }

    @staticmethod
    def save_punch_location(name, latitude, longitude, radius, enabled=1):
        if not name or latitude is None or longitude is None or radius is None:
            return {'success': False, 'message': '位置名称、经纬度半径不能为空'}

        location_dao.upsert_punch_location(name, latitude, longitude, radius, enabled)

        return {'success': True, 'message': '打卡位置设置成功'}
