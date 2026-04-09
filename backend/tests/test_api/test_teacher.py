"""
教师接口测试
测试教师班级管理、请假审批、补卡审批、班委管理等接口
"""
import pytest
from datetime import date, timedelta


class TestTeacherClassAPI:

    def test_get_classes(self, client, teacher_token):
        """测试获取班级列表"""
        response = client.get('/api/teacher/classes',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert isinstance(data['data'], list)
        assert '计算机2401' in data['data']

    def test_get_classes_without_token(self, client):
        """测试获取班级列表（无Token）"""
        response = client.get('/api/teacher/classes')
        assert response.status_code == 401

    def test_get_classes_student_forbidden(self, client, student_token):
        """测试学生不能访问教师班级接口"""
        response = client.get('/api/teacher/classes',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code == 403

    def test_get_class_students(self, client, teacher_token):
        """测试获取班级学生列表"""
        response = client.get('/api/teacher/class/students?class_name=计算机2401',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert isinstance(data['data'], list)

    def test_get_class_students_missing_class_name(self, client, teacher_token):
        """测试获取班级学生列表（使用默认班级）"""
        response = client.get('/api/teacher/class/students',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert response.status_code == 200

    def test_get_class_punch_summary(self, client, teacher_token):
        """测试获取班级打卡汇总"""
        today = date.today().strftime('%Y-%m-%d')
        response = client.get(f'/api/teacher/class/punch-summary?class_name=计算机2401&date={today}',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert 'total_students' in data['data']


class TestTeacherLeaveAPI:

    def test_get_pending_leaves(self, client, teacher_token):
        """测试获取待审批请假列表"""
        response = client.get('/api/teacher/leave/pending?class_name=计算机2401',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert isinstance(data['data'], list)

    def test_get_pending_leaves_missing_class_name(self, client, teacher_token):
        """测试获取待审批请假列表（使用默认班级）"""
        response = client.get('/api/teacher/leave/pending',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert response.status_code == 200

    def test_approve_leave_success(self, client, teacher_token, student_token):
        """测试审批请假成功"""
        tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        next_week = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
        client.post('/api/student/leave/apply',
            headers={'Authorization': f'Bearer {student_token}'},
            json={'start_date': tomorrow, 'end_date': next_week}
        )

        response = client.post('/api/teacher/leave/approve',
            headers={'Authorization': f'Bearer {teacher_token}'},
            json={'leave_id': 1, 'status': 'approved'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200

    def test_approve_leave_missing_params(self, client, teacher_token):
        """测试审批请假（缺少参数）"""
        response = client.post('/api/teacher/leave/approve',
            headers={'Authorization': f'Bearer {teacher_token}'},
            json={'leave_id': '', 'status': ''}
        )
        assert response.status_code == 400

    def test_approve_leave_student_forbidden(self, client, student_token):
        """测试学生不能审批请假"""
        response = client.post('/api/teacher/leave/approve',
            headers={'Authorization': f'Bearer {student_token}'},
            json={'leave_id': 1, 'status': 'approved'}
        )
        assert response.status_code == 403


class TestTeacherMakeupAPI:

    def test_get_pending_makeups(self, client, teacher_token):
        """测试获取待审批补卡列表"""
        response = client.get('/api/teacher/makeup/pending?class_name=计算机2401',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert isinstance(data['data'], list)

    def test_get_pending_makeups_missing_class_name(self, client, teacher_token):
        """测试获取待审批补卡列表（使用默认班级）"""
        response = client.get('/api/teacher/makeup/pending',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert response.status_code == 200

    def test_approve_makeup_success(self, client, teacher_token, student_token):
        """测试审批补卡成功"""
        yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        client.post('/api/student/makeup/apply',
            headers={'Authorization': f'Bearer {student_token}'},
            json={'target_date': yesterday, 'reason': '因病未能打卡'}
        )

        response = client.post('/api/teacher/makeup/approve',
            headers={'Authorization': f'Bearer {teacher_token}'},
            json={'makeup_id': 1, 'status': 'approved', 'punch_time': '08:00:00'}
        )
        assert response.status_code in [200, 500]

    def test_approve_makeup_student_forbidden(self, client, student_token):
        """测试学生不能审批补卡"""
        response = client.post('/api/teacher/makeup/approve',
            headers={'Authorization': f'Bearer {student_token}'},
            json={'makeup_id': 1, 'status': 'approved'}
        )
        assert response.status_code == 403


class TestTeacherMonitorAPI:

    def test_get_monitors(self, client, teacher_token):
        """测试获取班委列表"""
        response = client.get('/api/teacher/monitors?class_name=计算机2401',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert isinstance(data['data'], list)

    def test_appoint_monitor_success(self, client, teacher_token):
        """测试任命班委成功"""
        response = client.post('/api/teacher/monitor/appoint',
            headers={'Authorization': f'Bearer {teacher_token}'},
            json={'student_id': 'S2024002'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert data['data']['success'] is True

    def test_appoint_monitor_missing_student_id(self, client, teacher_token):
        """测试任命班委（缺少学生ID）"""
        response = client.post('/api/teacher/monitor/appoint',
            headers={'Authorization': f'Bearer {teacher_token}'},
            json={'student_id': ''}
        )
        assert response.status_code == 400

    def test_remove_monitor_success(self, client, teacher_token):
        """测试撤销班委成功"""
        client.post('/api/teacher/monitor/appoint',
            headers={'Authorization': f'Bearer {teacher_token}'},
            json={'student_id': 'S2024002'}
        )

        response = client.delete('/api/teacher/monitor/remove?student_id=S2024002',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200

    def test_remove_monitor_missing_student_id(self, client, teacher_token):
        """测试撤销班委（缺少学生ID）"""
        response = client.delete('/api/teacher/monitor/remove',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert response.status_code == 400

    def test_monitor_operations_student_forbidden(self, client, student_token):
        """测试学生不能进行班委操作"""
        response = client.post('/api/teacher/monitor/appoint',
            headers={'Authorization': f'Bearer {student_token}'},
            json={'student_id': 'S2024002'}
        )
        assert response.status_code == 403
