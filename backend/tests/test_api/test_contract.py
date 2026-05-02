"""
接口契约测试：
- 响应信封统一为 {code, message, data, trace_id?}
- 旧同义接口兼容期返回弃用头
"""


class TestApiContract:

    def test_health_response_envelope(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200
        payload = response.get_json()

        assert payload['code'] == 200
        assert payload['message'] == 'success'
        assert isinstance(payload['data'], dict)
        assert payload['data']['status'] == 'ok'
        assert payload.get('trace_id')
        assert response.headers.get('X-Trace-Id')

    def test_auth_error_response_envelope(self, client):
        response = client.get('/api/current-user')
        assert response.status_code == 401
        payload = response.get_json()

        assert payload['code'] == 401
        assert 'message' in payload
        assert 'data' in payload
        assert payload['data'] is None
        assert payload.get('trace_id')

    def test_legacy_student_route_deprecation_headers(self, client, student_token):
        response = client.get(
            '/api/students/records',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code == 200
        payload = response.get_json()

        assert payload['code'] == 200
        assert 'data' in payload
        assert response.headers.get('Deprecation') == 'true'
        assert response.headers.get('Sunset') == '2026-07-31'
        assert 'deprecation' in (response.headers.get('Link') or '')

    def test_legacy_teacher_route_deprecation_headers(self, client, teacher_token):
        response = client.get(
            '/api/teachers/classes',
            headers={'Authorization': f'Bearer {teacher_token}'}
        )
        assert response.status_code == 200
        payload = response.get_json()

        assert payload['code'] == 200
        assert isinstance(payload['data'], list)
        assert response.headers.get('Deprecation') == 'true'

    def test_notifications_unread_count_response_envelope(self, client, student_token):
        response = client.get(
            '/api/notifications/unread-count',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert response.status_code == 200
        payload = response.get_json()

        assert payload['code'] == 200
        assert payload['message'] == 'success'
        assert isinstance(payload['data'], dict)
        assert 'count' in payload['data']
        assert payload.get('trace_id')
