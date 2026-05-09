"""用户管理服务：用户 CRUD、密码重置。"""

from dao.user_dao import UserDAO
from utils.exceptions import ServiceException
from utils.serializers import generate_random_password
from utils.pagination import paginate, normalize_pagination

user_dao = UserDAO()


class AdminUserService:

    @staticmethod
    def list_users():
        users = user_dao.get_list(where="deleted_at IS NULL")
        return [
            {
                'username': u.username,
                'user_id': u.user_id,
                'role': u.role,
                'class': u.class_name,
            }
            for u in users
        ]

    @staticmethod
    def list_users_paginated(class_name=None, role=None, page=1, size=50):
        page, size, offset = normalize_pagination(page, size)
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

        users = user_dao.get_list(
            where=where, params=tuple(params),
            order_by="user_id ASC", limit=size, offset=offset
        )

        items = [
            {'username': u.username, 'user_id': u.user_id, 'role': u.role, 'class': u.class_name}
            for u in users
        ]
        return paginate(items, total, page, size)

    @staticmethod
    def save_user(username, user_id, password, role, class_name, real_name=None, student_id=None):
        valid_roles = ('admin', 'teacher', 'student', 'monitor')
        if role not in valid_roles:
            raise ServiceException(f'角色必须是 {"、".join(valid_roles)} 之一', code=6004)

        if role == 'admin':
            if class_name:
                raise ServiceException('管理员不应设置班级', code=6005)
        elif not class_name:
            raise ServiceException('老师、学生、班委必须设置班级', code=6006)

        existing_user = user_dao.get_by_id(user_id)

        if existing_user:
            data = {'username': username, 'role': role, 'class_name': class_name}
            if password:
                data['password'] = password
            if real_name:
                data['real_name'] = real_name
            if student_id:
                data['student_id'] = student_id
            user_dao.update(user_id, data)
            message = '用户更新成功'
        else:
            data = {
                'user_id': user_id,
                'username': username,
                'password': password,
                'real_name': real_name or username,
                'role': role,
                'class_name': class_name,
                'student_id': student_id or user_id,
            }
            user_dao.create(data)
            message = '用户添加成功'

        return {'success': True, 'message': message}

    @staticmethod
    def delete_user(user_id):
        target = user_dao.get_by_id(user_id)

        if not target or target.deleted_at:
            raise ServiceException('用户不存在', code=6002, http_status=404)

        if target.role == 'admin':
            admins = user_dao.get_list(where="role = ? AND deleted_at IS NULL", params=('admin',))
            if len(admins) <= 1:
                raise ServiceException('不能删除最后一个管理员账户', code=6007, http_status=403)

        success = user_dao.delete(user_id)

        if not success:
            raise ServiceException('用户不存在', code=6002, http_status=404)

        return {'success': True, 'message': '用户删除成功'}

    @staticmethod
    def reset_password(user_id):
        target_user = user_dao.get_by_id(user_id)

        if not target_user or target_user.deleted_at:
            raise ServiceException('用户不存在', code=6002, http_status=404)

        if target_user.role == 'admin':
            raise ServiceException('不允许重置管理员账户密码', code=6007, http_status=403)

        new_password = generate_random_password()
        user_dao.update(user_id, {'password': new_password})

        return {
            'success': True,
            'message': '密码重置成功',
            'new_password': new_password,
        }
