from dao import UserDAO, PunchDAO, PunchGeofenceDAO
from utils.exceptions import ServiceException
from config import Config
import random
import string

# 创建DAO实例
user_dao = UserDAO()
punch_dao = PunchDAO()
punch_geofence_dao = PunchGeofenceDAO()


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
            raise ServiceException(f'角色必须是 {", ".join(valid_roles)} 之一', code=5001)

        if role == 'admin':
            if class_name:
                raise ServiceException('管理员不应设置班级', code=5002)
        elif not class_name:
            raise ServiceException('老师、学生、班委必须设置班级', code=5003)

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
            raise ServiceException('用户不存在', code=5004, http_status=404)

        if target['role'] == 'admin':
            if user_dao.count_admins() <= 1:
                raise ServiceException('不能删除最后一个管理员账户', code=5005, http_status=403)

        rowcount = user_dao.delete_user(user_id)

        if rowcount == 0:
            raise ServiceException('用户不存在', code=5006, http_status=404)

        return {'success': True, 'message': '用户删除成功'}

    @staticmethod
    def reset_password(user_id):
        target_user = user_dao.get_user_by_id(user_id)

        if not target_user:
            raise ServiceException('用户不存在', code=5007, http_status=404)

        if target_user['role'] == 'admin':
            raise ServiceException('不允许重置管理员账户密码', code=5008, http_status=403)

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
            raise ServiceException('打卡日期和请假日期不能同时为空', code=5009)

        if has_punch and has_leave:
            raise ServiceException('打卡记录和请假记录不能同时存在', code=5010)

        if has_leave:
            valid_statuses = ('pending', 'approved', 'rejected')
            if leave_status not in valid_statuses:
                raise ServiceException(f'请假状态必须是 {", ".join(valid_statuses)} 之一', code=5011)

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
            raise ServiceException('考勤记录不存在', code=5012, http_status=404)

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
            raise ServiceException('位置名称、经纬度半径不能为空', code=5013)

        location_dao.upsert_punch_location(name, latitude, longitude, radius, enabled)

        return {'success': True, 'message': '打卡位置设置成功'}
