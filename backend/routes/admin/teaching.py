from flask import Blueprint, request
from services import AdminService
from utils.jwt import token_required, role_required
from utils.api_response import success
from utils.exceptions import ServiceException
from utils.parse_args import parse_bool_arg

admin_teaching_bp = Blueprint('admin_teaching', __name__, url_prefix='/api/admin')


# 获取教学分配记录
@admin_teaching_bp.route('/teaching/assignments', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def list_teaching_assignments():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    class_name = request.args.get('class_name', '').strip() or None
    teacher_id = request.args.get('teacher_id', '').strip() or None
    semester = request.args.get('semester', '').strip() or None
    include_deleted = parse_bool_arg('include_deleted', False)
    result = AdminService.list_teaching_assignments(
        class_name=class_name, teacher_id=teacher_id, semester=semester,
        page=page, size=size, include_deleted=include_deleted
    )
    return success(data=result)


# 创建教学分配记录
@admin_teaching_bp.route('/teaching/assignments', methods=['POST'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def create_teaching_assignment():
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=4999)
    class_name = (data.get('class_name') or '').strip()
    teacher_id = (data.get('teacher_id') or '').strip()
    semester = (data.get('semester') or '').strip() or None
    result = AdminService.create_teaching_assignment(class_name, teacher_id, semester)
    return success(data=result)


# 更新教学分配记录
@admin_teaching_bp.route('/teaching/assignments/<class_name>/<teacher_id>', methods=['PUT'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def update_teaching_assignment(class_name, teacher_id):
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=4999)
    semester = (data.get('semester') or '').strip() or None
    result = AdminService.update_teaching_assignment(class_name, teacher_id, semester)
    return success(data=result)


# 删除教学分配记录
@admin_teaching_bp.route('/teaching/assignments/<class_name>/<teacher_id>', methods=['DELETE'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def delete_teaching_assignment(class_name, teacher_id):
    result = AdminService.delete_teaching_assignment(class_name, teacher_id)
    return success(data=result)
