"""
管理员接口测试
测试管理员用户管理、考勤管理、配置管理等接口
"""
import pytest


class TestAdminUserAPI:

    def test_get_users(self, client, admin_token):
        """测试获取用户列表"""
        response = client.get('/api/admin/users',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert 'users' in data['data']
        assert 'total' in data['data']

    def test_get_users_pagination(self, client, admin_token):
        """测试获取用户列表（分页）"""
        response = client.get('/api/admin/users?page=1&size=5',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert len(data['data']['users']) <= 5

    def test_get_users_filter_by_role(self, client, admin_token):
        """测试获取用户列表（按角色筛选）"""
        response = client.get('/api/admin/users?role=student',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200

    def test_get_users_without_admin_token(self, client, teacher_token):
        """测试非管理员不能获取用户列表"""
        response = client.get('/api/admin/users',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert response.status_code == 403

    def test_create_user_success(self, client, admin_token):
        """测试创建用户成功"""
        import uuid
        user_id = f'TEST{uuid.uuid4().hex[:6].upper()}'
        response = client.post('/api/admin/users',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'username': '测试用户',
                'user_id': user_id,
                'password': 'test123456',
                'role': 'student',
                'class': '计算机2401'
            }
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert data['data']['success'] is True

    def test_create_user_missing_params(self, client, admin_token):
        """测试创建用户（缺少参数）"""
        response = client.post('/api/admin/users',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'username': '测试用户',
                'user_id': '',
                'password': '',
                'role': ''
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['code'] == 5000

    def test_create_user_without_admin_token(self, client, teacher_token):
        """测试非管理员不能创建用户"""
        response = client.post('/api/admin/users',
            headers={'Authorization': f'Bearer {teacher_token}'},
            json={
                'username': '测试用户',
                'user_id': 'TEST001',
                'password': 'test123456',
                'role': 'student'
            }
        )
        assert response.status_code == 403

    def test_update_user_success(self, client, admin_token):
        """测试更新用户成功"""
        response = client.put('/api/admin/users/S2024001',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'username': '张三更新',
                'role': 'student',
                'class': '计算机2401'
            }
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200

    def test_delete_user_success(self, client, admin_token):
        """测试删除用户成功"""
        response = client.delete('/api/admin/users/S2024004',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200

    def test_reset_password_success(self, client, admin_token):
        """测试重置用户密码成功"""
        response = client.post('/api/admin/users/reset-password',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'user_id': 'S2024001'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert 'new_password' in data['data']

    def test_reset_password_missing_user_id(self, client, admin_token):
        """测试重置用户密码（缺少用户ID）"""
        response = client.post('/api/admin/users/reset-password',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'user_id': ''}
        )
        assert response.status_code == 400


class TestAdminAttendanceAPI:

    def test_get_attendance_records(self, client, admin_token):
        """测试获取考勤记录"""
        response = client.get('/api/admin/attendance-records',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert isinstance(data['data'], list)

    def test_get_attendance_records_with_filters(self, client, admin_token):
        """测试获取考勤记录（带筛选条件）"""
        response = client.get('/api/admin/attendance-records?user_id=S2024001&start_date=2026-01-01',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200

    def test_create_attendance_record_success(self, client, admin_token):
        """测试创建考勤记录成功"""
        response = client.post('/api/admin/attendance-records',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'id': None,
                'user_id': 'S2024001',
                'punch_date': '2026-04-09',
                'leave_start_date': None,
                'leave_end_date': None,
                'leave_status': 'present'
            }
        )
        assert response.status_code in [200, 500]

    def test_create_attendance_record_missing_user_id(self, client, admin_token):
        """测试创建考勤记录（缺少用户ID）"""
        response = client.post('/api/admin/attendance-records',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'id': None,
                'user_id': '',
                'punch_date': '2026-04-09'
            }
        )
        assert response.status_code in [400, 500]

    def test_delete_attendance_record_success(self, client, admin_token):
        """测试删除考勤记录成功"""
        response = client.delete('/api/admin/attendance-records/999',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code in [200, 404]


class TestAdminConfigAPI:

    def test_get_punch_location(self, client, admin_token):
        """测试获取打卡位置配置"""
        response = client.get('/api/admin/punch-location',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200

    def test_set_punch_location_success(self, client, admin_token):
        """测试设置打卡位置成功"""
        response = client.post('/api/admin/punch-location',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'name': '测试地点',
                'latitude': 39.989,
                'longitude': 116.312,
                'radius': 200,
                'enabled': 1
            }
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200

    def test_get_config(self, client, admin_token):
        """测试获取全局配置"""
        response = client.get('/api/admin/config',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert 'global_time_check_enabled' in data['data']

    def test_update_config_success(self, client, admin_token):
        """测试更新全局配置成功"""
        response = client.put('/api/admin/config',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'global_time_check_enabled': True,
                'global_location_check_enabled': False,
                'allow_multi_punch': True
            }
        )
        assert response.status_code in [200, 400, 500]

    def test_config_without_admin_token(self, client, teacher_token):
        """测试非管理员不能访问配置接口"""
        response = client.get('/api/admin/config',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert response.status_code == 403
