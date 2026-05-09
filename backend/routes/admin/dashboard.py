from flask import Blueprint, request
from services import AdminAttendanceService, ConfigService, StatisticsService
from utils.jwt import token_required, role_required
from utils.api_response import success
from utils.exceptions import ServiceException
from utils.error_codes import JSON_INVALID

admin_dashboard_bp = Blueprint('admin_dashboard', __name__, url_prefix='/api/admin')


# 获取仪表盘统计数据
@admin_dashboard_bp.route('/dashboard/stats', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def dashboard_stats():
    result = AdminAttendanceService.get_dashboard_stats()
    return success(data=result)


# 获取考勤趋势统计
@admin_dashboard_bp.route('/dashboard/trend', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def dashboard_trend():
    days = request.args.get('days', 7, type=int)
    result = StatisticsService.get_attendance_trend(days=days)
    return success(data=result)


# 获取打卡配置
@admin_dashboard_bp.route('/config', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def get_config():
    config = ConfigService.get_punch_config()
    return success(data=config)


# 更新打卡配置
@admin_dashboard_bp.route('/config', methods=['PUT'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def update_config():
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    result = ConfigService.update_punch_config(data)
    return success(data=result)
