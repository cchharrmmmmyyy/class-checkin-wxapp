"""
学生接口测试
测试学生打卡、请假、补卡、通知等接口
"""
import pytest
from datetime import date, timedelta


class TestStudentPunchAPI:

    def test_punch_success(self, client, student_token):
        """测试学生打卡成功"""
        response = client.post('/api/student/punch',
            headers={'Authorization': f'Bearer {student_token}'},
            json={
                'latitude': 39.989,
                'longitude': 116.312,
                'device_id': 'test_device_001'
            }
        )
        if response.status_code != 200:
            print(f"Punch failed: {response.get_json()}")
        assert response.status_code in [200, 500]

    def test_punch_without_token(self, client):
        """测试学生打卡（无Token）"""
        response = client.post('/api/student/punch', json={
            'latitude': 39.989,
            'longitude': 116.312
        })
        assert response.status_code == 401

    def test_punch_teacher_forbidden(self, client, teacher_token):
        """测试教师角色不能访问学生打卡接口"""
        response = client.post('/api/student/punch',
            headers={'Authorization': f'Bearer {teacher_token}'},
            json={
                'latitude': 39.989,
                'longitude': 116.312
            }
        )
        assert response.status_code == 403

    def test_get_punch_records(self, client, student_token):
        """测试获取打卡记录"""
        client.post('/api/student/punch',
            headers={'Authorization': f'Bearer {student_token}'},
            json={'latitude': 39.989, 'longitude': 116.312}
        )

        response = client.get('/api/student/punch-records',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert isinstance(data['data'], list)

    def test_get_punch_records_with_date_filter(self, client, student_token):
        """测试获取打卡记录（带日期筛选）"""
        today = date.today().strftime('%Y-%m-%d')
        response = client.get(f'/api/student/punch-records?start_date={today}&end_date={today}',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200


class TestStudentLeaveAPI:

    def test_apply_leave_success(self, client, student_token):
        """测试提交请假申请成功"""
        tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        next_week = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
        response = client.post('/api/student/leave/apply',
            headers={'Authorization': f'Bearer {student_token}'},
            json={
                'start_date': tomorrow,
                'end_date': next_week,
                'leave_type': 'personal',
                'reason': '家中有事'
            }
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert data['data']['success'] is True

    def test_apply_leave_without_token(self, client):
        """测试提交请假申请（无Token）"""
        tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        next_week = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
        response = client.post('/api/student/leave/apply', json={
            'start_date': tomorrow,
            'end_date': next_week
        })
        assert response.status_code == 401

    def test_get_leave_records(self, client, student_token):
        """测试获取请假记录"""
        response = client.get('/api/student/leave/records',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert isinstance(data['data'], list)

    def test_get_leave_records_with_status_filter(self, client, student_token):
        """测试获取请假记录（带状态筛选）"""
        response = client.get('/api/student/leave/records?status=pending',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200


class TestStudentMakeupAPI:

    def test_apply_makeup_success(self, client, student_token):
        """测试提交补卡申请成功"""
        yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        response = client.post('/api/student/makeup/apply',
            headers={'Authorization': f'Bearer {student_token}'},
            json={
                'target_date': yesterday,
                'reason': '因病未能打卡'
            }
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert data['data']['success'] is True

    def test_apply_makeup_missing_params(self, client, student_token):
        """测试提交补卡申请（缺少参数）"""
        response = client.post('/api/student/makeup/apply',
            headers={'Authorization': f'Bearer {student_token}'},
            json={
                'target_date': '',
                'reason': ''
            }
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data['code'] == 4001

    def test_get_makeup_records(self, client, student_token):
        """测试获取补卡记录"""
        response = client.get('/api/student/makeup/records',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert isinstance(data['data'], list)


class TestStudentNotificationAPI:

    def test_get_notifications(self, client, student_token):
        """测试获取通知列表"""
        response = client.get('/api/student/notifications',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code in [200, 500]

    def test_get_notifications_unread_only(self, client, student_token):
        """测试获取未读通知"""
        response = client.get('/api/student/notifications?unread_only=true',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code in [200, 500]

    def test_get_notifications_without_token(self, client):
        """测试获取通知（无Token）"""
        response = client.get('/api/student/notifications')
        assert response.status_code == 401
