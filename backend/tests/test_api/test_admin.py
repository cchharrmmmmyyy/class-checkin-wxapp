"""
管理员接口测试
覆盖组织架构、任课关系、规则管理、兼容接口与拆分后的考勤写接口。
"""

import uuid


class TestAdminOrgAPI:
    def test_list_org_resources(self, client, admin_token):
        headers = {'Authorization': f'Bearer {admin_token}'}
        for path in (
            '/api/admin/org/campuses',
            '/api/admin/org/departments',
            '/api/admin/org/majors',
            '/api/admin/org/grades',
            '/api/admin/org/classes'
        ):
            resp = client.get(path, headers=headers)
            assert resp.status_code == 200
            data = resp.get_json()
            assert data['code'] == 200
            assert 'items' in data['data']
            assert 'total' in data['data']

    def test_class_soft_delete_and_hidden_by_default(self, client, admin_token):
        headers = {'Authorization': f'Bearer {admin_token}'}
        name = f'测试班级{uuid.uuid4().hex[:6]}'
        create_resp = client.post(
            '/api/admin/org/classes',
            headers=headers,
            json={'class_name': name, 'grade_id': 1}
        )
        assert create_resp.status_code == 200

        delete_resp = client.delete(f'/api/admin/org/classes/{name}', headers=headers)
        assert delete_resp.status_code == 200

        hidden_resp = client.get(f'/api/admin/org/classes?class_name={name}', headers=headers)
        hidden_items = hidden_resp.get_json()['data']['items']
        assert all(item['class_name'] != name for item in hidden_items)

        include_resp = client.get(
            f'/api/admin/org/classes?class_name={name}&include_deleted=true',
            headers=headers
        )
        include_items = include_resp.get_json()['data']['items']
        assert any(item['class_name'] == name and item['deleted_at'] for item in include_items)

    def test_org_permission_denied_for_teacher(self, client, teacher_token):
        resp = client.get('/api/admin/org/campuses', headers={'Authorization': f'Bearer {teacher_token}'})
        assert resp.status_code == 403


class TestAdminTeachingAPI:
    def test_create_duplicate_and_delete_assignment(self, client, admin_token):
        headers = {'Authorization': f'Bearer {admin_token}'}
        payload = {'class_name': '电子2401', 'teacher_id': 'T2024002', 'semester': '2026-Spring'}
        create_resp = client.post('/api/admin/teaching/assignments', headers=headers, json=payload)
        assert create_resp.status_code == 200

        dup_resp = client.post('/api/admin/teaching/assignments', headers=headers, json=payload)
        assert dup_resp.status_code == 409
        assert dup_resp.get_json()['code'] == 5036

        query_resp = client.get('/api/admin/teaching/assignments?class_name=电子2401', headers=headers)
        assert query_resp.status_code == 200
        items = query_resp.get_json()['data']['items']
        assert any(item['teacher_id'] == 'T2024002' for item in items)

        del_resp = client.delete('/api/admin/teaching/assignments/电子2401/T2024002', headers=headers)
        assert del_resp.status_code == 200


class TestAdminRuleAPI:
    def test_time_slot_geofence_rule_crud(self, client, admin_token):
        headers = {'Authorization': f'Bearer {admin_token}'}
        slot_resp = client.post(
            '/api/admin/rules/time-slots',
            headers=headers,
            json={'name': '测试时段', 'start_time': '10:00', 'end_time': '10:30', 'enabled': 1}
        )
        assert slot_resp.status_code == 200
        slot_id = slot_resp.get_json()['data']['id']

        geofence_resp = client.post(
            '/api/admin/rules/punch-geofences',
            headers=headers,
            json={
                'name': '测试多边形',
                'fence_type': 'polygon',
                'polygon_coords': [[39.98, 116.31], [39.99, 116.32], [39.985, 116.33]],
                'enabled': 1
            }
        )
        assert geofence_resp.status_code == 200
        geofence_id = geofence_resp.get_json()['data']['id']

        rule_resp = client.post(
            '/api/admin/rules/punch-rules',
            headers=headers,
            json={
                'time_slot_id': slot_id,
                'geofence_id': geofence_id,
                'priority': 321,
                'time_enabled': 1,
                'location_enabled': 1,
                'enabled': 1
            }
        )
        assert rule_resp.status_code == 200
        rule_id = rule_resp.get_json()['data']['id']

        conflict_resp = client.post(
            '/api/admin/rules/punch-rules',
            headers=headers,
            json={
                'time_slot_id': 1,
                'geofence_id': 1,
                'priority': 321,
                'time_enabled': 1,
                'location_enabled': 1,
                'enabled': 1
            }
        )
        assert conflict_resp.status_code == 409
        assert conflict_resp.get_json()['code'] == 5046

        list_resp = client.get('/api/admin/rules/punch-rules', headers=headers)
        assert list_resp.status_code == 200
        assert any(item['id'] == rule_id for item in list_resp.get_json()['data']['items'])

        del_rule = client.delete(f'/api/admin/rules/punch-rules/{rule_id}', headers=headers)
        del_slot = client.delete(f'/api/admin/rules/time-slots/{slot_id}', headers=headers)
        del_fence = client.delete(f'/api/admin/rules/punch-geofences/{geofence_id}', headers=headers)
        assert del_rule.status_code == 200
        assert del_slot.status_code == 200
        assert del_fence.status_code == 200

    def test_polygon_validation_error(self, client, admin_token):
        resp = client.post(
            '/api/admin/rules/punch-geofences',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'name': '坏围栏', 'fence_type': 'polygon', 'polygon_coords': [[1, 2]], 'enabled': 1}
        )
        assert resp.status_code == 400
        assert resp.get_json()['code'] == 5031


class TestAdminAttendanceSplitAPI:
    def test_split_attendance_write_endpoints(self, client, admin_token):
        headers = {'Authorization': f'Bearer {admin_token}'}
        punch_resp = client.post(
            '/api/admin/attendance/punch-records',
            headers=headers,
            json={'user_id': 'S2024001', 'punch_date': '2026-04-21'}
        )
        assert punch_resp.status_code == 200
        punch_id = punch_resp.get_json()['data']['id']

        update_punch = client.put(
            f'/api/admin/attendance/punch-records/{punch_id}',
            headers=headers,
            json={'user_id': 'S2024001', 'punch_date': '2026-04-22'}
        )
        assert update_punch.status_code == 200

        leave_resp = client.post(
            '/api/admin/attendance/leave-records',
            headers=headers,
            json={
                'user_id': 'S2024002',
                'leave_start_date': '2026-04-22',
                'leave_end_date': '2026-04-23',
                'leave_status': 'pending'
            }
        )
        assert leave_resp.status_code == 200
        leave_id = leave_resp.get_json()['data']['id']

        update_leave = client.put(
            f'/api/admin/attendance/leave-records/{leave_id}',
            headers=headers,
            json={'leave_status': 'approved'}
        )
        assert update_leave.status_code == 200

        assert client.delete(f'/api/admin/attendance/punch-records/{punch_id}', headers=headers).status_code == 200
        assert client.delete(f'/api/admin/attendance/leave-records/{leave_id}', headers=headers).status_code == 200

    def test_legacy_attendance_endpoint_has_migration_hint(self, client, admin_token):
        resp = client.post(
            '/api/admin/attendance-records',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={'user_id': 'S2024001', 'punch_date': '2026-04-21'}
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert 'migration_hint' in body['data']
        assert resp.headers.get('Deprecation') == 'true'


class TestAdminCompatAndConfigAPI:
    def test_punch_location_is_legacy_compatible(self, client, admin_token):
        headers = {'Authorization': f'Bearer {admin_token}'}
        get_resp = client.get('/api/admin/punch-location', headers=headers)
        assert get_resp.status_code == 200
        get_data = get_resp.get_json()
        assert get_data['code'] == 200
        assert get_data['data']['compatibility']['legacy'] is True
        assert get_resp.headers.get('Deprecation') == 'true'

        post_resp = client.post(
            '/api/admin/punch-location',
            headers=headers,
            json={'name': '测试地点', 'latitude': 39.989, 'longitude': 116.312, 'radius': 200, 'enabled': 1}
        )
        assert post_resp.status_code == 200
        assert post_resp.headers.get('Deprecation') == 'true'

    def test_get_and_update_config(self, client, admin_token):
        headers = {'Authorization': f'Bearer {admin_token}'}
        get_resp = client.get('/api/admin/config', headers=headers)
        assert get_resp.status_code == 200
        assert 'global_time_check_enabled' in get_resp.get_json()['data']

        update_resp = client.put(
            '/api/admin/config',
            headers=headers,
            json={
                'global_time_check_enabled': True,
                'global_location_check_enabled': False,
                'allow_multi_punch': True
            }
        )
        assert update_resp.status_code in (200, 400)
