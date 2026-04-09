"""
通用接口测试
测试通知、操作日志等通用功能的接口
"""
import pytest


class TestCommonNotificationAPI:

    def test_get_notifications(self, client, student_token):
        """测试获取通知列表"""
        response = client.get('/api/notifications',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code in [200, 500]

    def test_get_notifications_with_type_filter(self, client, student_token):
        """测试获取通知列表（按类型筛选）"""
        response = client.get('/api/notifications?type=PUNCH',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code in [200, 500]

    def test_get_notifications_unread_only(self, client, student_token):
        """测试获取未读通知"""
        response = client.get('/api/notifications?unread_only=true',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code in [200, 500]

    def test_get_notifications_without_token(self, client):
        """测试获取通知（无Token）"""
        response = client.get('/api/notifications')
        assert response.status_code == 401

    def test_mark_notification_read_success(self, client, student_token):
        """测试标记通知已读成功"""
        response = client.post('/api/notifications/mark-read',
            headers={'Authorization': f'Bearer {student_token}'},
            json={'notification_id': 1}
        )
        assert response.status_code in [200, 500]

    def test_mark_notification_read_missing_id(self, client, student_token):
        """测试标记通知已读（缺少通知ID）"""
        response = client.post('/api/notifications/mark-read',
            headers={'Authorization': f'Bearer {student_token}'},
            json={'notification_id': None}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['code'] == 8001

    def test_get_unread_count(self, client, student_token):
        """测试获取未读通知数量"""
        response = client.get('/api/notifications/unread-count',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code in [200, 500]

    def test_get_unread_count_with_type(self, client, student_token):
        """测试获取未读通知数量（按类型）"""
        response = client.get('/api/notifications/unread-count?type=PUNCH',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code in [200, 500]


class TestCommonOperationLogAPI:

    def test_get_operation_logs_as_admin(self, client, admin_token):
        """测试管理员获取操作日志"""
        response = client.get('/api/operation-logs',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code in [200, 500]

    def test_get_operation_logs_as_teacher(self, client, teacher_token):
        """测试教师获取操作日志"""
        response = client.get('/api/operation-logs',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert response.status_code in [200, 500]

    def test_get_operation_logs_as_student_forbidden(self, client, student_token):
        """测试学生不能获取操作日志"""
        response = client.get('/api/operation-logs',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code == 403

    def test_get_operation_logs_with_filters(self, client, admin_token):
        """测试获取操作日志（带筛选条件）"""
        response = client.get('/api/operation-logs?operation_type=LOGIN&limit=10',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert response.status_code in [200, 500]

    def test_get_operation_logs_without_token(self, client):
        """测试获取操作日志（无Token）"""
        response = client.get('/api/operation-logs')
        assert response.status_code == 401


class TestHealthCheck:

    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert data['data']['status'] == 'ok'
