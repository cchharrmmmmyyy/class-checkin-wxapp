from flask import Blueprint, request
from services import AdminService
from utils.jwt import token_required, role_required
from utils.parse_args import parse_bool_arg
from utils.api_response import success
from utils.exceptions import ServiceException
from utils.constants import ENABLED, DISABLED, DEFAULT_PRIORITY
from utils.error_codes import JSON_INVALID

admin_rule_bp = Blueprint('admin_rule', __name__, url_prefix='/api/admin')


# ---- 时间段 ----

# 获取时间段列表
@admin_rule_bp.route('/rules/time-slots', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def list_time_slots():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    name = request.args.get('name', '').strip() or None
    enabled = request.args.get('enabled')
    include_deleted = parse_bool_arg('include_deleted', False)
    result = AdminService.list_time_slots(
        name=name, enabled=enabled, page=page, size=size, include_deleted=include_deleted
    )
    return success(data=result)


# 创建时间段
@admin_rule_bp.route('/rules/time-slots', methods=['POST'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def create_time_slot():
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    result = AdminService.save_time_slot(
        None, (data.get('name') or '').strip(),
        data.get('start_time'), data.get('end_time'), data.get('enabled', ENABLED)
    )
    return success(data=result)


# 更新时间段
@admin_rule_bp.route('/rules/time-slots/<int:slot_id>', methods=['PUT'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def update_time_slot(slot_id):
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    result = AdminService.save_time_slot(
        slot_id, (data.get('name') or '').strip(),
        data.get('start_time'), data.get('end_time'), data.get('enabled', ENABLED)
    )
    return success(data=result)


# 删除时间段
@admin_rule_bp.route('/rules/time-slots/<int:slot_id>', methods=['DELETE'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def delete_time_slot(slot_id):
    result = AdminService.delete_time_slot(slot_id)
    return success(data=result)


# ---- 围栏 ----

# 获取围栏列表
@admin_rule_bp.route('/rules/punch-geofences', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def list_punch_geofences():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    name = request.args.get('name', '').strip() or None
    enabled = request.args.get('enabled')
    fence_type = request.args.get('fence_type', '').strip() or None
    include_deleted = parse_bool_arg('include_deleted', False)
    result = AdminService.list_geofences(
        name=name, enabled=enabled, fence_type=fence_type,
        page=page, size=size, include_deleted=include_deleted
    )
    return success(data=result)


# 创建围栏
@admin_rule_bp.route('/rules/punch-geofences', methods=['POST'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def create_punch_geofence():
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    result = AdminService.save_geofence(
        geofence_id=None,
        name=(data.get('name') or '').strip(),
        fence_type=(data.get('fence_type') or '').strip(),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        radius=data.get('radius'),
        polygon_coords=data.get('polygon_coords'),
        enabled=data.get('enabled', ENABLED)
    )
    return success(data=result)


# 更新围栏
@admin_rule_bp.route('/rules/punch-geofences/<int:geofence_id>', methods=['PUT'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def update_punch_geofence(geofence_id):
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    result = AdminService.save_geofence(
        geofence_id=geofence_id,
        name=(data.get('name') or '').strip(),
        fence_type=(data.get('fence_type') or '').strip(),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        radius=data.get('radius'),
        polygon_coords=data.get('polygon_coords'),
        enabled=data.get('enabled', ENABLED)
    )
    return success(data=result)


# 删除围栏
@admin_rule_bp.route('/rules/punch-geofences/<int:geofence_id>', methods=['DELETE'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def delete_punch_geofence(geofence_id):
    result = AdminService.delete_geofence(geofence_id)
    return success(data=result)


# ---- 打卡规则 ----

# 获取打卡规则列表
@admin_rule_bp.route('/rules/punch-rules', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def list_punch_rules():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    enabled = request.args.get('enabled')
    time_slot_id = request.args.get('time_slot_id', type=int)
    geofence_id = request.args.get('geofence_id', type=int)
    include_deleted = parse_bool_arg('include_deleted', False)
    result = AdminService.list_punch_rules(
        enabled=enabled, time_slot_id=time_slot_id, geofence_id=geofence_id,
        page=page, size=size, include_deleted=include_deleted
    )
    return success(data=result)


# 创建打卡规则
@admin_rule_bp.route('/rules/punch-rules', methods=['POST'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def create_punch_rule():
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    result = AdminService.save_punch_rule(
        rule_id=None,
        time_slot_id=data.get('time_slot_id'),
        geofence_id=data.get('geofence_id'),
        priority=data.get('priority', DEFAULT_PRIORITY),
        time_enabled=data.get('time_enabled', ENABLED),
        location_enabled=data.get('location_enabled', ENABLED),
        enabled=data.get('enabled', ENABLED)
    )
    return success(data=result)


# 更新打卡规则
@admin_rule_bp.route('/rules/punch-rules/<int:rule_id>', methods=['PUT'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def update_punch_rule(rule_id):
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    result = AdminService.save_punch_rule(
        rule_id=rule_id,
        time_slot_id=data.get('time_slot_id'),
        geofence_id=data.get('geofence_id'),
        priority=data.get('priority', DEFAULT_PRIORITY),
        time_enabled=data.get('time_enabled', ENABLED),
        location_enabled=data.get('location_enabled', ENABLED),
        enabled=data.get('enabled', ENABLED)
    )
    return success(data=result)


# 删除打卡规则
@admin_rule_bp.route('/rules/punch-rules/<int:rule_id>', methods=['DELETE'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def delete_punch_rule(rule_id):
    result = AdminService.delete_punch_rule(rule_id)
    return success(data=result)
