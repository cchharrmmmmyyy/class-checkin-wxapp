from dao.user_dao import UserDAO
from dao.punch_dao import PunchDAO
from dao.punch_geofence_dao import PunchGeofenceDAO
from dao.leave_dao import LeaveDAO
from utils.exceptions import ServiceException
from config import Config
import random
import string

# 创建DAO实例
user_dao = UserDAO()
punch_dao = PunchDAO()
punch_geofence_dao = PunchGeofenceDAO()
leave_dao = LeaveDAO()


def _generate_random_password(length=None):
    if length is None:
        length = Config.RANDOM_PASSWORD_LENGTH
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


class AdminService:

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

        offset = (page - 1) * size
        users = user_dao.get_list(
            where=where,
            params=tuple(params),
            order_by="user_id ASC",
            limit=size,
            offset=offset
        )

        return {
            'users': [
                {
                    'username': u.username,
                    'user_id': u.user_id,
                    'role': u.role,
                    'class': u.class_name
                }
                for u in users
            ],
            'total': total,
            'page': page,
            'size': size
        }

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
    def get_attendance_records(username=None, user_id=None, start_date=None, end_date=None, leave_status=None):
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
        records = []

        # 添加打卡记录
        for punch in punches:
            user = user_dao.get_by_id(punch.user_id)
            records.append({
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
            records.append({
                'id': leave.id,
                'username': user.username if user else '',
                'user_id': leave.user_id,
                'punch_date': None,
                'leave_start_date': leave.leave_start_date,
                'leave_end_date': leave.leave_end_date,
                'leave_status': leave.leave_status
            })

        # 按日期排序
        records.sort(key=lambda x: x['punch_date'] or x['leave_start_date'], reverse=True)

        return records

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
                raise ServiceException(f'请假状态必须是 {"、".join(valid_statuses)} 之一', code=5011)

        if has_punch:
            if record_id:
                # 更新打卡记录
                punch = punch_dao.get_by_id(record_id)
                if not punch:
                    raise ServiceException('打卡记录不存在', code=5012, http_status=404)
                data = {
                    'user_id': user_id,
                    'punch_date': punch_date,
                    'punch_time': '12:00:00',  # 默认时间
                    'latitude': 0.0,  # 默认位置
                    'longitude': 0.0
                }
                punch_dao.update(record_id, data)
                message = '打卡记录更新成功'
            else:
                # 创建打卡记录
                data = {
                    'user_id': user_id,
                    'punch_date': punch_date,
                    'punch_time': '12:00:00',  # 默认时间
                    'latitude': 0.0,  # 默认位置
                    'longitude': 0.0
                }
                punch_dao.create(data)
                message = '打卡记录添加成功'
        else:
            if record_id:
                # 更新请假记录
                leave = leave_dao.get_by_id(record_id)
                if not leave:
                    raise ServiceException('请假记录不存在', code=5013, http_status=404)
                data = {
                    'leave_status': leave_status
                }
                leave_dao.update(record_id, data)
                message = '请假记录更新成功'
            else:
                # 创建请假记录
                data = {
                    'user_id': user_id,
                    'leave_start_date': leave_start_date,
                    'leave_end_date': leave_end_date,
                    'leave_type': 'personal',
                    'leave_status': leave_status
                }
                leave_dao.create(data)
                message = '请假记录添加成功'

        return {'success': True, 'message': message}

    @staticmethod
    def delete_attendance_record(record_id):
        # 尝试删除打卡记录
        punch_deleted = punch_dao.delete(record_id)
        if punch_deleted:
            return {'success': True, 'message': '打卡记录删除成功'}

        # 尝试删除请假记录
        leave_deleted = leave_dao.delete(record_id)
        if leave_deleted:
            return {'success': True, 'message': '请假记录删除成功'}

        raise ServiceException('考勤记录不存在', code=5012, http_status=404)

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
                'enabled': geofence.enabled
            }
        }

    @staticmethod
    def save_punch_location(name, latitude, longitude, radius, enabled=1):
        if not name or latitude is None or longitude is None or radius is None:
            raise ServiceException('位置名称、经纬度半径不能为空', code=5013)

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

        return {'success': True, 'message': '打卡位置设置成功'}
