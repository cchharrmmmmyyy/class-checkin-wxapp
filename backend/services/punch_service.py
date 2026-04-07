from datetime import datetime
from dao import user_dao, punch_record_dao, location_dao
from utils.geo import calculate_distance
from config import Config


class PunchService:

    @staticmethod
    def punch(user_id, latitude, longitude):
        punch_location = location_dao.get_enabled_punch_location()

        if punch_location and latitude is not None and longitude is not None:
            distance = calculate_distance(
                latitude, longitude,
                punch_location['latitude'],
                punch_location['longitude']
            )
            if distance > punch_location['radius']:
                return {
                    'success': False,
                    'message': f'不在打卡范围内，距离打卡点 {int(distance)} 米',
                    'out_of_range': True
                }

        if punch_location and punch_location['enabled'] and (latitude is None or longitude is None):
            return {
                'success': False,
                'message': '无法获取您的位置，请确保定位服务已开启',
                'no_location': True
            }

        today = datetime.now().strftime('%Y-%m-%d')

        existing = punch_record_dao.get_punch_record_by_user_and_date(user_id, today)
        if existing:
            return {
                'success': False,
                'message': '今日已打卡',
                'already_punched': True
            }

        punch_record_dao.create_punch_record(user_id, today)

        return {
            'success': True,
            'message': '打卡成功',
            'data': {'punch_date': today}
        }

    @staticmethod
    def get_user_punch_records(user_id):
        records = punch_record_dao.get_punch_records_by_user(user_id, Config.PUNCH_RECORDS_LIMIT)
        return [
            {
                'id': r['id'],
                'user_id': r['user_id'],
                'username': r['username'],
                'punch_date': r['punch_date']
            }
            for r in records
        ]

    @staticmethod
    def get_class_punch_records(class_name):
        today = datetime.now().strftime('%Y-%m-%d')

        students = user_dao.get_users_by_class(class_name)
        student_ids = [s['user_id'] for s in students]

        if student_ids:
            punched_user_ids = punch_record_dao.get_punch_user_ids_for_date(student_ids, today)
            leave_user_ids = punch_record_dao.get_leave_user_ids_for_date(student_ids, today)
        else:
            punched_user_ids = []
            leave_user_ids = []

        class_records = []
        for student in students:
            punched = student['user_id'] in punched_user_ids
            on_leave = student['user_id'] in leave_user_ids

            display_name = student['username']
            if student['role'] == 'monitor':
                display_name = student['username'] + ' (班委)'

            punch_status = '已打卡' if punched else ('请假' if on_leave else '未打卡')

            class_records.append({
                'username': display_name,
                'user_id': student['user_id'],
                'role': student['role'],
                'punched': punched,
                'on_leave': on_leave,
                'punchTime': punch_status
            })

        return class_records
