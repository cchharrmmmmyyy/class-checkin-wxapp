from flask import Blueprint, request
from services import AdminOrgService
from utils.jwt import token_required, role_required
from utils.parse_args import parse_bool_arg
from utils.api_response import success
from utils.exceptions import ServiceException
from utils.error_codes import JSON_INVALID

admin_org_bp = Blueprint('admin_org', __name__, url_prefix='/api/admin')


# ---- 校区 ----

@admin_org_bp.route('/org/campuses', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def list_campuses():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    name = request.args.get('name', '').strip() or None
    result = AdminOrgService.list_campuses(name=name, page=page, size=size)
    return success(data=result)


@admin_org_bp.route('/org/campuses', methods=['POST'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def create_campus():
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    name = (data.get('name') or '').strip()
    address = data.get('address')
    result = AdminOrgService.save_campus(None, name, address)
    return success(data=result)


@admin_org_bp.route('/org/campuses/<int:campus_id>', methods=['PUT'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def update_campus(campus_id):
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    name = (data.get('name') or '').strip()
    address = data.get('address')
    result = AdminOrgService.save_campus(campus_id, name, address)
    return success(data=result)


@admin_org_bp.route('/org/campuses/<int:campus_id>', methods=['DELETE'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def delete_campus(campus_id):
    result = AdminOrgService.delete_campus(campus_id)
    return success(data=result)


# ---- 院系 ----

@admin_org_bp.route('/org/departments', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def list_departments():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    campus_id = request.args.get('campus_id', type=int)
    name = request.args.get('name', '').strip() or None
    result = AdminOrgService.list_departments(campus_id=campus_id, name=name, page=page, size=size)
    return success(data=result)


@admin_org_bp.route('/org/departments', methods=['POST'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def create_department():
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    campus_id = data.get('campus_id')
    name = (data.get('name') or '').strip()
    code = data.get('code')
    result = AdminOrgService.save_department(None, campus_id, name, code)
    return success(data=result)


@admin_org_bp.route('/org/departments/<int:department_id>', methods=['PUT'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def update_department(department_id):
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    campus_id = data.get('campus_id')
    name = (data.get('name') or '').strip()
    code = data.get('code')
    result = AdminOrgService.save_department(department_id, campus_id, name, code)
    return success(data=result)


@admin_org_bp.route('/org/departments/<int:department_id>', methods=['DELETE'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def delete_department(department_id):
    result = AdminOrgService.delete_department(department_id)
    return success(data=result)


# ---- 专业 ----

@admin_org_bp.route('/org/majors', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def list_majors():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    campus_id = request.args.get('campus_id', type=int)
    department_id = request.args.get('department_id', type=int)
    name = request.args.get('name', '').strip() or None
    result = AdminOrgService.list_majors(
        campus_id=campus_id, department_id=department_id, name=name, page=page, size=size
    )
    return success(data=result)


@admin_org_bp.route('/org/majors', methods=['POST'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def create_major():
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    department_id = data.get('department_id')
    name = (data.get('name') or '').strip()
    code = data.get('code')
    result = AdminOrgService.save_major(None, department_id, name, code)
    return success(data=result)


@admin_org_bp.route('/org/majors/<int:major_id>', methods=['PUT'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def update_major(major_id):
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    department_id = data.get('department_id')
    name = (data.get('name') or '').strip()
    code = data.get('code')
    result = AdminOrgService.save_major(major_id, department_id, name, code)
    return success(data=result)


@admin_org_bp.route('/org/majors/<int:major_id>', methods=['DELETE'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def delete_major(major_id):
    result = AdminOrgService.delete_major(major_id)
    return success(data=result)


# ---- 年级 ----

@admin_org_bp.route('/org/grades', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def list_grades():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    campus_id = request.args.get('campus_id', type=int)
    department_id = request.args.get('department_id', type=int)
    major_id = request.args.get('major_id', type=int)
    year = request.args.get('year', type=int)
    result = AdminOrgService.list_grades(
        campus_id=campus_id, department_id=department_id,
        major_id=major_id, year=year, page=page, size=size
    )
    return success(data=result)


@admin_org_bp.route('/org/grades', methods=['POST'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def create_grade():
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    major_id = data.get('major_id')
    year = data.get('year')
    name = (data.get('name') or '').strip()
    result = AdminOrgService.save_grade(None, major_id, year, name)
    return success(data=result)


@admin_org_bp.route('/org/grades/<int:grade_id>', methods=['PUT'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def update_grade(grade_id):
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    major_id = data.get('major_id')
    year = data.get('year')
    name = (data.get('name') or '').strip()
    result = AdminOrgService.save_grade(grade_id, major_id, year, name)
    return success(data=result)


@admin_org_bp.route('/org/grades/<int:grade_id>', methods=['DELETE'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def delete_grade(grade_id):
    result = AdminOrgService.delete_grade(grade_id)
    return success(data=result)


# ---- 班级 ----

@admin_org_bp.route('/org/classes', methods=['GET'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def list_classes():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    grade_id = request.args.get('grade_id', type=int)
    class_name = request.args.get('class_name', '').strip() or None
    include_deleted = parse_bool_arg('include_deleted', False)
    result = AdminOrgService.list_classes(
        grade_id=grade_id, class_name=class_name, page=page, size=size,
        include_deleted=include_deleted
    )
    return success(data=result)


@admin_org_bp.route('/org/classes', methods=['POST'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def create_class():
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    class_name = (data.get('class_name') or '').strip()
    grade_id = data.get('grade_id')
    result = AdminOrgService.save_class(None, class_name, grade_id)
    return success(data=result)


@admin_org_bp.route('/org/classes/<class_name>', methods=['PUT'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def update_class(class_name):
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceException('请求体不是有效的JSON格式', code=JSON_INVALID)
    new_class_name = (data.get('class_name') or class_name).strip()
    grade_id = data.get('grade_id')
    result = AdminOrgService.save_class(class_name, new_class_name, grade_id)
    return success(data=result)


@admin_org_bp.route('/org/classes/<class_name>', methods=['DELETE'])
@token_required(allow_cookie=True)
@role_required(['admin'])
def delete_class(class_name):
    result = AdminOrgService.delete_class(class_name)
    return success(data=result)
