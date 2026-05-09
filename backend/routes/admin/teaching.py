from flask import Blueprint, request
from services import AdminTeachingService
from utils.jwt import token_required, role_required
from utils.api_response import success
from utils.exceptions import ServiceException
from utils.error_codes import JSON_INVALID

admin_teaching_bp = Blueprint('admin_teaching', __name__, url_prefix='/api/admin')


@admin_teaching_bp.route('/teaching/assignments', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def list_assignments():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    class_name = request.args.get('class_name', '').strip() or None
    teacher_id = request.args.get('teacher_id', '').strip() or None
    semester = request.args.get('semester', '').strip() or None
    include_deleted = request.args.get('include_deleted', '').strip().lower() in ('1', 'true')
    result = AdminTeachingService.list_teaching_assignments(
        class_name=class_name, teacher_id=teacher_id, semester=semester,
        page=page, size=size, include_deleted=include_deleted
    )
    return success(data=result)


@admin_teaching_bp.route('/teaching/assignments', methods=['POST'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def create_assignment():
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    class_name = (data.get('class_name') or '').strip()
    teacher_id = (data.get('teacher_id') or '').strip()
    semester = (data.get('semester') or '').strip() or None
    result = AdminTeachingService.create_teaching_assignment(class_name, teacher_id, semester)
    return success(data=result)


@admin_teaching_bp.route('/teaching/assignments', methods=['PUT'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def update_assignment():
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    class_name = (data.get('class_name') or '').strip()
    teacher_id = (data.get('teacher_id') or '').strip()
    semester = (data.get('semester') or '').strip() or None
    result = AdminTeachingService.update_teaching_assignment(class_name, teacher_id, semester)
    return success(data=result)


@admin_teaching_bp.route('/teaching/assignments', methods=['DELETE'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def delete_assignment():
    class_name = request.args.get('class_name', '').strip()
    teacher_id = request.args.get('teacher_id', '').strip()
    result = AdminTeachingService.delete_teaching_assignment(class_name, teacher_id)
    return success(data=result)
