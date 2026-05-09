"""考勤管理服务：记录查询/导出/仪表盘/打卡位置。"""

import csv
import io
from datetime import date

from dao.user_dao import UserDAO
from dao.punch_dao import PunchDAO
from dao.leave_dao import LeaveDAO
from dao.punch_geofence_dao import PunchGeofenceDAO
from utils.exceptions import ServiceException
from utils.error_codes import PUNCH_TIME_MISSING, PUNCH_LOCATION_MISSING
from utils.serializers import load_polygon_coords
from utils.pagination import paginate, normalize_pagination

user_dao = UserDAO()
punch_dao = PunchDAO()
leave_dao = LeaveDAO()
punch_geofence_dao = PunchGeofenceDAO()


class AdminAttendanceService:

    @staticmethod
    def get_attendance_records(username=None, user_id=None, start_date=None, end_date=None, leave_status=None, page=1, size=50):
        page, size, offset = normalize_pagination(page, size)
        punch_conditions = ['1=1']
        punch_params = []
        leave_conditions = ['1=1']
        leave_params = []

        if username:
            users = user_dao.get_list(
                where='username LIKE ? AND deleted_at IS NULL',
                params=(f'%{username}%',),
            )
            user_ids = [u.user_id for u in users]
            if not user_ids:
                return paginate([], 0, page, size)
            placeholders = ','.join('?' * len(user_ids))
            punch_conditions.append(f'user_id IN ({placeholders})')
            punch_params.extend(user_ids)
            leave_conditions.append(f'user_id IN ({placeholders})')
            leave_params.extend(user_ids)

        if user_id:
            punch_conditions.append('user_id = ?')
            punch_params.append(user_id)
            leave_conditions.append('user_id = ?')
            leave_params.append(user_id)

        if start_date:
            punch_conditions.append('punch_date >= ?')
            punch_params.append(start_date)
            leave_conditions.append('leave_start_date >= ?')
            leave_params.append(start_date)

        if end_date:
            punch_conditions.append('punch_date <= ?')
            punch_params.append(end_date)
            leave_conditions.append('leave_end_date <= ?')
            leave_params.append(end_date)

        if leave_status:
            leave_conditions.append('leave_status = ?')
            leave_params.append(leave_status)

        punches = punch_dao.get_list(where=' AND '.join(punch_conditions), params=tuple(punch_params))
        leaves = leave_dao.get_list(where=' AND '.join(leave_conditions), params=tuple(leave_params))

        all_records = []

        for punch in punches:
            user = user_dao.get_by_id(punch.user_id)
            all_records.append({
                'id': punch.id,
                'username': user.username if user else '',
                'user_id': punch.user_id,
                'punch_date': punch.punch_date,
                'leave_start_date': None,
                'leave_end_date': None,
                'leave_status': None,
            })

        for leave in leaves:
            user = user_dao.get_by_id(leave.user_id)
            all_records.append({
                'id': leave.id,
                'username': user.username if user else '',
                'user_id': leave.user_id,
                'punch_date': None,
                'leave_start_date': leave.leave_start_date,
                'leave_end_date': leave.leave_end_date,
                'leave_status': leave.leave_status,
            })

        all_records.sort(key=lambda x: x['punch_date'] or x['leave_start_date'], reverse=True)
        total = len(all_records)
        items = all_records if size is None else all_records[offset:offset + size]
        return paginate(items, total, page, size)

    @staticmethod
    def export_attendance_records_csv(username=None, user_id=None, start_date=None, end_date=None, leave_status=None):
        records = AdminAttendanceService.get_attendance_records(
            username=username, user_id=user_id, start_date=start_date,
            end_date=end_date, leave_status=leave_status, page=1, size=None,
        ).get('items', [])

        output = io.StringIO()
        output.write('\ufeff')
        writer = csv.writer(output)
        writer.writerow(['ID', '学号', '姓名', '打卡日期', '请假开始日期', '请假结束日期', '状态'])

        for r in records:
            status = '-'
            if r['leave_status'] == 'pending':
                status = '待审批'
            elif r['leave_status'] == 'approved':
                status = '已审批'
            elif r['leave_status'] == 'rejected':
                status = '已拒绝'
            elif r['punch_date']:
                status = '已打卡'

            writer.writerow([
                r['id'], r['user_id'], r['username'],
                r['punch_date'] or '-', r['leave_start_date'] or '-',
                r['leave_end_date'] or '-', status,
            ])

        output.seek(0)
        filename = f"attendance_export_{date.today().isoformat()}.csv"
        return output.getvalue().encode('utf-8-sig'), filename

    @staticmethod
    def save_punch_record(record_id, user_id, punch_date, punch_time, latitude, longitude):
        if not user_id:
            raise ServiceException('用户ID不能为空', code=6008)
        if not punch_date:
            raise ServiceException('打卡日期不能为空', code=6009)
        if not punch_time:
            raise ServiceException('打卡时间不能为空', code=PUNCH_TIME_MISSING)
        if latitude is None:
            raise ServiceException('打卡纬度不能为空', code=PUNCH_LOCATION_MISSING)
        if longitude is None:
            raise ServiceException('打卡经度不能为空', code=PUNCH_LOCATION_MISSING)
        target_user = user_dao.get_by_id(user_id)
        if not target_user or target_user.deleted_at:
            raise ServiceException('用户不存在', code=6002, http_status=404)
        payload = {
            'user_id': user_id,
            'punch_date': punch_date,
            'punch_time': punch_time,
            'latitude': latitude,
            'longitude': longitude,
        }
        if record_id:
            target = punch_dao.get_by_id(record_id)
            if not target:
                raise ServiceException('打卡记录不存在', code=6010, http_status=404)
            punch_dao.update(record_id, payload)
            return {'success': True, 'message': '打卡记录更新成功', 'id': record_id}
        new_id = punch_dao.create(payload)
        return {'success': True, 'message': '打卡记录添加成功', 'id': new_id}

    @staticmethod
    def save_leave_record(record_id, user_id, leave_start_date=None, leave_end_date=None, leave_status=None, leave_type=None, leave_reason=None):
        if record_id:
            target = leave_dao.get_by_id(record_id)
            if not target or target.deleted_at:
                raise ServiceException('请假记录不存在', code=6011, http_status=404)
            valid_statuses = ('pending', 'approved', 'rejected')
            if leave_status not in valid_statuses:
                raise ServiceException(f'请假状态必须是 {"、".join(valid_statuses)} 之一', code=4005)
            leave_dao.update(record_id, {'leave_status': leave_status, 'approved_by': None})
            return {'success': True, 'message': '请假记录更新成功', 'id': record_id}

        if not user_id or not leave_start_date or not leave_end_date:
            raise ServiceException('用户ID和请假起止日期不能为空', code=4001)
        if not leave_type:
            raise ServiceException('请假类型不能为空', code=4001)
        target_user = user_dao.get_by_id(user_id)
        if not target_user or target_user.deleted_at:
            raise ServiceException('用户不存在', code=6002, http_status=404)
        data = {
            'user_id': user_id,
            'leave_start_date': leave_start_date,
            'leave_end_date': leave_end_date,
            'leave_type': leave_type,
            'leave_reason': leave_reason,
        }
        new_id = leave_dao.create(data)
        if leave_status and leave_status != 'pending':
            leave_dao.update(new_id, {'leave_status': leave_status, 'approved_by': None})
        return {'success': True, 'message': '请假记录添加成功', 'id': new_id}

    @staticmethod
    def delete_punch_record(record_id):
        deleted = punch_dao.delete(record_id)
        if not deleted:
            raise ServiceException('打卡记录不存在', code=6010, http_status=404)
        return {'success': True, 'message': '打卡记录删除成功'}

    @staticmethod
    def delete_leave_record(record_id):
        deleted = leave_dao.delete(record_id)
        if not deleted:
            raise ServiceException('请假记录不存在', code=6011, http_status=404)
        return {'success': True, 'message': '请假记录删除成功'}

    @staticmethod
    def get_punch_location():
        geofences = punch_geofence_dao.get_enabled_geofences()
        if not geofences:
            return {'success': True, 'data': None}

        geofence = geofences[0]
        return {
            'success': True,
            'data': {
                'id': geofence.id,
                'name': geofence.name,
                'latitude': geofence.latitude,
                'longitude': geofence.longitude,
                'radius': geofence.radius,
                'enabled': geofence.enabled,
                'fence_type': geofence.fence_type,
                'polygon_coords': load_polygon_coords(geofence.polygon_coords) if geofence.polygon_coords else None,
            },
            'compatibility': {
                'legacy': True,
                'replacement': '/api/admin/rules/punch-geofences',
                'sunset_date': '2026-07-31',
            },
        }

    @staticmethod
    def save_punch_location(name, latitude, longitude, radius, enabled=1):
        if not name or latitude is None or longitude is None or radius is None:
            raise ServiceException('位置名称、经纬度半径不能为空', code=7009)

        existing_geofences = punch_geofence_dao.get_list()
        for geofence in existing_geofences:
            punch_geofence_dao.update(geofence.id, {'enabled': 0})

        data = {
            'name': name,
            'fence_type': 'circle',
            'latitude': latitude,
            'longitude': longitude,
            'radius': radius,
            'enabled': enabled,
        }
        punch_geofence_dao.create(data)

        return {
            'success': True,
            'message': '打卡位置设置成功',
            'compatibility': {
                'legacy': True,
                'replacement': '/api/admin/rules/punch-geofences',
                'sunset_date': '2026-07-31',
            },
        }

    @staticmethod
    def get_dashboard_stats():
        today = date.today().isoformat()

        total_students = user_dao.count_by_role('student')
        present_today = punch_dao.count_by_date(today)
        on_leave_today = leave_dao.count_approved_by_date(today)
        absent_today = total_students - present_today - on_leave_today
        pending_leaves = leave_dao.count_pending()

        geofence = punch_geofence_dao.get_first_enabled()
        geofence_data = None
        if geofence:
            geofence_data = {
                'id': geofence.id,
                'name': geofence.name,
                'latitude': geofence.latitude,
                'longitude': geofence.longitude,
                'radius': geofence.radius,
                'enabled': geofence.enabled,
            }

        return {
            'total_students': total_students,
            'present_today': present_today,
            'on_leave_today': on_leave_today,
            'absent_today': absent_today,
            'pending_leaves': pending_leaves,
            'geofence': geofence_data,
        }
