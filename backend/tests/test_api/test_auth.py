"""
认证接口测试
测试登录、修改密码、获取当前用户信息等接口
"""
import pytest


class TestAuthAPI:

    def test_health_check(self, client):
        """测试健康检查接口"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert data['data']['status'] == 'ok'

    def test_login_success(self, client):
        """测试学生登录成功"""
        response = client.post('/api/login', json={
            'user_id': 'S2024001',
            'password': '123456'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert 'token' in data['data']
        assert data['data']['user']['user_id'] == 'S2024001'
        assert data['data']['user']['role'] == 'student'

    def test_login_teacher_success(self, client):
        """测试教师登录成功"""
        response = client.post('/api/login', json={
            'user_id': 'T2024001',
            'password': '123456'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert 'token' in data['data']
        assert data['data']['user']['role'] == 'teacher'

    def test_login_admin_success(self, client):
        """测试管理员登录成功"""
        response = client.post('/api/login', json={
            'user_id': 'admin001',
            'password': 'admin123'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert 'token' in data['data']
        assert data['data']['user']['role'] == 'admin'

    def test_admin_page_prefers_query_token_over_stale_cookie(self, client):
        """测试 /admin 优先使用最新 query token，而不是旧 cookie"""
        login_response = client.post('/api/login', json={
            'user_id': 'admin001',
            'password': 'admin123'
        })
        assert login_response.status_code == 200
        token = login_response.get_json()['data']['token']

        client.set_cookie('adminToken', 'stale.invalid.token')
        admin_response = client.get(f'/admin?token={token}')

        assert admin_response.status_code == 200
        assert '考勤系统 · 管理后台' in admin_response.get_data(as_text=True)

    def test_admin_page_redirects_with_reason_when_token_invalid(self, client):
        """测试 /admin 在 token 无效时带 reason 重定向到登录页"""
        client.set_cookie('adminToken', 'stale.invalid.token')
        resp = client.get('/admin', follow_redirects=False)
        assert resp.status_code in (301, 302, 303, 307, 308)
        assert resp.headers.get('Location', '').startswith('/login?reason=token_invalid')

    def test_login_invalid_password(self, client):
        """测试密码错误登录失败"""
        response = client.post('/api/login', json={
            'user_id': 'S2024001',
            'password': 'wrong_password'
        })
        assert response.status_code == 401
        data = response.get_json()
        assert data['code'] == 1001

    def test_login_invalid_user_id(self, client):
        """测试不存在的用户登录失败"""
        response = client.post('/api/login', json={
            'user_id': 'NOTEXIST',
            'password': '123456'
        })
        assert response.status_code == 401
        data = response.get_json()
        assert data['code'] == 1001

    def test_login_empty_credentials(self, client):
        """测试空凭据登录失败"""
        response = client.post('/api/login', json={
            'user_id': '',
            'password': ''
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data['code'] == 1000

    def test_login_missing_password(self, client):
        """测试缺少密码登录失败"""
        response = client.post('/api/login', json={
            'user_id': 'S2024001'
        })
        assert response.status_code == 400

    def test_get_current_user_with_token(self, client, student_token):
        """测试获取当前用户信息（有效Token）"""
        response = client.get('/api/current-user', headers={
            'Authorization': f'Bearer {student_token}'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert data['data']['user_id'] == 'S2024001'
        assert data['data']['role'] == 'student'

    def test_get_current_user_without_token(self, client):
        """测试获取当前用户信息（无Token）"""
        response = client.get('/api/current-user')
        assert response.status_code == 401
        data = response.get_json()
        assert data['code'] == 401

    def test_get_current_user_with_invalid_token(self, client):
        """测试获取当前用户信息（无效Token）"""
        response = client.get('/api/current-user', headers={
            'Authorization': 'Bearer invalid_token_here'
        })
        assert response.status_code == 401
        data = response.get_json()
        assert data['code'] == 401

    def test_change_password_success(self, client, student_token):
        """测试修改密码成功"""
        response = client.post('/api/change-password',
            headers={'Authorization': f'Bearer {student_token}'},
            json={
                'old_password': '123456',
                'new_password': '654321'
            }
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert data['data']['success'] is True

    def test_change_password_without_token(self, client):
        """测试修改密码（无Token）"""
        response = client.post('/api/change-password', json={
            'old_password': '123456',
            'new_password': '654321'
        })
        assert response.status_code == 401

    def test_change_password_wrong_old_password(self, client, student_token):
        """测试修改密码（旧密码错误）"""
        response = client.post('/api/change-password',
            headers={'Authorization': f'Bearer {student_token}'},
            json={
                'old_password': 'wrong_old',
                'new_password': '654321'
            }
        )
        assert response.status_code == 401
        data = response.get_json()
        assert data['code'] == 1005

    def test_change_password_empty_passwords(self, client, student_token):
        """测试修改密码（空密码）"""
        response = client.post('/api/change-password',
            headers={'Authorization': f'Bearer {student_token}'},
            json={
                'old_password': '',
                'new_password': ''
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['code'] == 1007
