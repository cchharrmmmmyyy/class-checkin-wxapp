# -*- coding: utf-8 -*-
"""
Black-box API test fixtures using Flask's test client.

Uses a fresh temp database per session so tests are isolated.
"""
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MINIPROGRAM_HEADER = {'X-Client-Type': 'miniprogram'}


@pytest.fixture(scope='session')
def client():
    """Flask test client with a fresh test database."""
    fd, db_path = tempfile.mkstemp(suffix='.db', prefix='test_')
    os.close(fd)

    # Override .env: python-dotenv won't overwrite existing os.environ keys
    os.environ['DATABASE_FILE'] = db_path
    os.environ['FLASK_DEBUG'] = 'true'
    os.environ['INSERT_TEST_DATA'] = 'true'

    # Now import — config.py will see our env vars
    from app import app
    app.config['TESTING'] = True

    with app.test_client() as c:
        yield c

    try:
        os.unlink(db_path)
    except OSError:
        pass


def _login(client, user_id, password, headers=None):
    r = client.post('/api/login', json={'user_id': user_id, 'password': password},
                    headers=headers or {})
    body = r.get_json()
    assert body['code'] == 200, f'Login {user_id} failed (code {body["code"]}): {body}'
    return body['data']['token']


@pytest.fixture(scope='session')
def admin_token(client):
    return _login(client, 'admin001', 'admin123')


@pytest.fixture(scope='session')
def teacher_token(client):
    return _login(client, 'T2024001', '123456', MINIPROGRAM_HEADER)


@pytest.fixture(scope='session')
def student_token(client):
    return _login(client, 'S2024001', '123456', MINIPROGRAM_HEADER)


@pytest.fixture(scope='session')
def monitor_token(client):
    return _login(client, 'S2024003', '123456', MINIPROGRAM_HEADER)
