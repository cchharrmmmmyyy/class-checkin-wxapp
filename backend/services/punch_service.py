from datetime import datetime
from dao import UserDAO, PunchDAO, PunchGeofenceDAO, LeaveDAO
from utils.geo import calculate_distance
from utils.exceptions import ServiceException
from utils.pagination import paginate, normalize_pagination
from utils import error_codes as EC
from config import Config
from services.config_service import ConfigService

user_dao = UserDAO()
punch_dao = PunchDAO()
punch_geofence_dao = PunchGeofenceDAO()
leave_dao = LeaveDAO()


class PunchService:

    @staticmethod
    def punch(user_id, latitude, longitude):
        if ConfigService.is_location_check_enabled():
            punch_geofences = punch_geofence_dao.get_enabled_geofences()

            if punch_geofences and latitude is not None and longitude is not None:
                in_range = False
                for geofence in punch_geofences:
                    distance = calculate_distance(
                        latitude, longitude,
                        geofence.latitude,
                        geofence.longitude
                    )
                    if distance <= geofence.radius:
                        in_range = True
                        break

                if not in_range:
                    raise ServiceException('不在打卡范围内', code=EC.PUNCH_OUT_OF_RANGE)

            if punch_geofences and (latitude is None or longitude is None):
                raise ServiceException('无法获取您的位置，请确保定位服务已开启', code=EC.PUNCH_LOCATION_FAILED)

        today = datetime.now().strftime('%Y-%m-%d')
        now = datetime.now().strftime('%H:%M:%S')

        leave_records = leave_dao.get_leave_records_by_user(user_id)
        for leave in leave_records:
            if leave.leave_status == 'approved' and leave.leave_start_date <= today <= leave.leave_end_date:
                raise ServiceException('请假期间不允许打卡', code=EC.PUNCH_ON_LEAVE)

        existing = punch_dao.get_punch_by_user_and_date(user_id, today)
        if existing:
            raise ServiceException('今日已打卡', code=EC.PUNCH_ALREADY_PUNCHED)

        punch_id = punch_dao.create({
            'user_id': user_id,
            'punch_date': today,
            'punch_time': now,
            'latitude': latitude,
            'longitude': longitude,
        })

        return {
            'success': True,
            'message': '打卡成功',
            'data': {'punch_date': today, 'punch_time': now, 'punch_id': punch_id}
        }

    @staticmethod
    def get_user_punch_records(user_id, start_date=None, end_date=None, page=1, size=50):
        conditions = ["user_id = ?"]
        params = [user_id]

        if start_date:
            conditions.append("punch_date >= ?")
            params.append(start_date)

        if end_date:
            conditions.append("punch_date <= ?")
            params.append(end_date)

        where = " AND ".join(conditions)
        total = punch_dao.count(where=where, params=tuple(params))
        page, size, offset = normalize_pagination(page, size)

        records = punch_dao.get_list(
            where=where,
            params=tuple(params),
            order_by="punch_date DESC",
            limit=size,
            offset=offset
        )

        items = [
            {
                'id': r.id,
                'punch_date': r.punch_date,
                'punch_time': r.punch_time,
                'latitude': r.latitude,
                'longitude': r.longitude,
                'is_makeup': r.is_makeup,
                'created_at': r.created_at
            }
            for r in records
        ]

        return paginate(items, total, page, size)

    @staticmethod
    def get_statistics(date_str=None):
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')

        punch_count = punch_dao.count_by_date(date_str)
        leave_count = leave_dao.count_approved_by_date(date_str)

        return {
            'date': date_str,
            'punch_count': punch_count,
            'leave_count': leave_count
        }
