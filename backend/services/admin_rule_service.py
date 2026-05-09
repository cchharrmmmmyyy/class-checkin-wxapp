"""打卡规则管理服务：时间段/围栏/打卡规则 CRUD。"""

from dao.punch_geofence_dao import PunchGeofenceDAO
from dao.punch_time_slot_dao import PunchTimeSlotDAO
from dao.punch_rule_dao import PunchRuleDAO
from utils.exceptions import ServiceException
from utils.serializers import to_time_str, to_datetime_str, as_bool_int, load_polygon_coords, dump_polygon_coords, validate_polygon_coords
from utils.pagination import paginate, normalize_pagination

punch_geofence_dao = PunchGeofenceDAO()
punch_time_slot_dao = PunchTimeSlotDAO()
punch_rule_dao = PunchRuleDAO()


def _serialize_time_slot(item):
    return {
        'id': item.id,
        'name': item.name,
        'start_time': to_time_str(item.start_time),
        'end_time': to_time_str(item.end_time),
        'enabled': item.enabled,
        'created_at': to_datetime_str(item.created_at),
        'deleted_at': to_datetime_str(item.deleted_at),
    }


def _serialize_geofence(item):
    polygon = load_polygon_coords(item.polygon_coords) if item.polygon_coords else None
    return {
        'id': item.id,
        'name': item.name,
        'fence_type': item.fence_type,
        'latitude': item.latitude,
        'longitude': item.longitude,
        'radius': item.radius,
        'polygon_coords': polygon,
        'enabled': item.enabled,
        'created_at': to_datetime_str(item.created_at),
        'deleted_at': to_datetime_str(item.deleted_at),
    }


def _serialize_rule(item):
    return {
        'id': item.id,
        'time_slot_id': item.time_slot_id,
        'geofence_id': item.geofence_id,
        'priority': item.priority,
        'time_enabled': item.time_enabled,
        'location_enabled': item.location_enabled,
        'enabled': item.enabled,
        'created_at': to_datetime_str(item.created_at),
        'deleted_at': to_datetime_str(item.deleted_at),
    }


class AdminRuleService:

    # ---- 时间段 ----

    @staticmethod
    def list_time_slots(name=None, enabled=None, page=1, size=20, include_deleted=False):
        page, size, offset = normalize_pagination(page, size)
        conditions = []
        params = []
        if name:
            conditions.append('name LIKE ?')
            params.append(f'%{name}%')
        if enabled is not None:
            conditions.append('enabled = ?')
            params.append(as_bool_int(enabled))
        if not include_deleted:
            conditions.append('deleted_at IS NULL')
        where = ' AND '.join(conditions) if conditions else None
        params_tuple = tuple(params)
        total = len(punch_time_slot_dao.get_list(where=where, params=params_tuple))
        records = punch_time_slot_dao.get_list(where=where, params=params_tuple, limit=size, offset=offset)
        items = [_serialize_time_slot(item) for item in records]
        return paginate(items, total, page, size)

    @staticmethod
    def save_time_slot(slot_id, name, start_time, end_time, enabled=1):
        if not name or not start_time or not end_time:
            raise ServiceException('name、start_time、end_time 不能为空', code=7015)
        payload = {
            'name': name,
            'start_time': start_time,
            'end_time': end_time,
            'enabled': as_bool_int(enabled),
        }
        if slot_id is None:
            new_id = punch_time_slot_dao.create(payload)
            return {'success': True, 'message': '时段创建成功', 'id': new_id}

        current = punch_time_slot_dao.get_by_id(slot_id)
        if not current or current.deleted_at:
            raise ServiceException('时段不存在', code=7013, http_status=404)
        punch_time_slot_dao.update(slot_id, payload)
        return {'success': True, 'message': '时段更新成功', 'id': slot_id}

    @staticmethod
    def delete_time_slot(slot_id):
        deleted = punch_time_slot_dao.delete(slot_id)
        if not deleted:
            raise ServiceException('时段不存在', code=7013, http_status=404)
        return {'success': True, 'message': '时段删除成功'}

    # ---- 围栏 ----

    @staticmethod
    def list_geofences(name=None, enabled=None, fence_type=None, page=1, size=20, include_deleted=False):
        page, size, offset = normalize_pagination(page, size)
        conditions = []
        params = []
        if name:
            conditions.append('name LIKE ?')
            params.append(f'%{name}%')
        if enabled is not None:
            conditions.append('enabled = ?')
            params.append(as_bool_int(enabled))
        if fence_type:
            conditions.append('fence_type = ?')
            params.append(fence_type)
        if not include_deleted:
            conditions.append('deleted_at IS NULL')
        where = ' AND '.join(conditions) if conditions else None
        params_tuple = tuple(params)
        total = len(punch_geofence_dao.get_list(where=where, params=params_tuple))
        records = punch_geofence_dao.get_list(where=where, params=params_tuple, limit=size, offset=offset)
        items = [_serialize_geofence(item) for item in records]
        return paginate(items, total, page, size)

    @staticmethod
    def save_geofence(geofence_id, name, fence_type, latitude=None, longitude=None, radius=None, polygon_coords=None, enabled=1):
        if not name or not fence_type:
            raise ServiceException('name 和 fence_type 不能为空', code=7009)
        if fence_type not in ('circle', 'polygon'):
            raise ServiceException('fence_type 仅支持 circle 或 polygon', code=7009)

        payload = {'name': name, 'fence_type': fence_type, 'enabled': as_bool_int(enabled)}
        if fence_type == 'circle':
            if latitude is None or longitude is None or radius is None:
                raise ServiceException('circle 围栏必须提供 latitude、longitude、radius', code=7009)
            payload.update({'latitude': latitude, 'longitude': longitude, 'radius': radius, 'polygon_coords': None})
        else:
            coords = validate_polygon_coords(polygon_coords)
            payload.update({'latitude': None, 'longitude': None, 'radius': None, 'polygon_coords': dump_polygon_coords(coords)})

        if geofence_id is None:
            new_id = punch_geofence_dao.create(payload)
            return {'success': True, 'message': '围栏创建成功', 'id': new_id}

        current = punch_geofence_dao.get_by_id(geofence_id)
        if not current or current.deleted_at:
            raise ServiceException('围栏不存在', code=7010, http_status=404)
        punch_geofence_dao.update(geofence_id, payload)
        return {'success': True, 'message': '围栏更新成功', 'id': geofence_id}

    @staticmethod
    def delete_geofence(geofence_id):
        deleted = punch_geofence_dao.delete(geofence_id)
        if not deleted:
            raise ServiceException('围栏不存在', code=7010, http_status=404)
        return {'success': True, 'message': '围栏删除成功'}

    # ---- 打卡规则 ----

    @staticmethod
    def _ensure_rule_refs(time_slot_id, geofence_id):
        slot = punch_time_slot_dao.get_by_id(time_slot_id)
        if not slot or slot.deleted_at:
            raise ServiceException('关联时段不存在', code=7013, http_status=404)
        fence = punch_geofence_dao.get_by_id(geofence_id)
        if not fence or fence.deleted_at:
            raise ServiceException('关联围栏不存在', code=7010, http_status=404)

    @staticmethod
    def _validate_rule_priority_conflict(priority, rule_id=None):
        conflicts = punch_rule_dao.get_list(where='priority = ? AND deleted_at IS NULL', params=(priority,))
        for item in conflicts:
            if rule_id is None or item.id != rule_id:
                raise ServiceException('priority 冲突，请使用唯一优先级', code=9011, http_status=409)

    @staticmethod
    def list_punch_rules(enabled=None, time_slot_id=None, geofence_id=None, page=1, size=20, include_deleted=False):
        page, size, offset = normalize_pagination(page, size)
        conditions = []
        params = []
        if enabled is not None:
            conditions.append('enabled = ?')
            params.append(as_bool_int(enabled))
        if time_slot_id is not None:
            conditions.append('time_slot_id = ?')
            params.append(time_slot_id)
        if geofence_id is not None:
            conditions.append('geofence_id = ?')
            params.append(geofence_id)
        if not include_deleted:
            conditions.append('deleted_at IS NULL')
        where = ' AND '.join(conditions) if conditions else None
        params_tuple = tuple(params)
        total = len(punch_rule_dao.get_list(where=where, params=params_tuple))
        records = punch_rule_dao.get_list(where=where, params=params_tuple, limit=size, offset=offset)
        items = [_serialize_rule(item) for item in records]
        return paginate(items, total, page, size)

    @staticmethod
    def save_punch_rule(rule_id, time_slot_id, geofence_id, priority=100, time_enabled=1, location_enabled=1, enabled=1):
        if time_slot_id is None or geofence_id is None:
            raise ServiceException('time_slot_id 和 geofence_id 不能为空', code=7009)
        AdminRuleService._ensure_rule_refs(time_slot_id, geofence_id)
        AdminRuleService._validate_rule_priority_conflict(priority, rule_id)
        payload = {
            'time_slot_id': time_slot_id,
            'geofence_id': geofence_id,
            'priority': priority,
            'time_enabled': as_bool_int(time_enabled),
            'location_enabled': as_bool_int(location_enabled),
            'enabled': as_bool_int(enabled),
        }
        if rule_id is None:
            new_id = punch_rule_dao.create(payload)
            return {'success': True, 'message': '规则创建成功', 'id': new_id}

        current = punch_rule_dao.get_by_id(rule_id)
        if not current or current.deleted_at:
            raise ServiceException('规则不存在', code=7010, http_status=404)
        punch_rule_dao.update(rule_id, payload)
        return {'success': True, 'message': '规则更新成功', 'id': rule_id}

    @staticmethod
    def delete_punch_rule(rule_id):
        deleted = punch_rule_dao.delete(rule_id)
        if not deleted:
            raise ServiceException('规则不存在', code=7010, http_status=404)
        return {'success': True, 'message': '规则删除成功'}
