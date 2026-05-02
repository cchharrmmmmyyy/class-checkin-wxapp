import os
import sqlite3
import pytest
import tempfile


class TestDbConnection:
    def test_hash_password(self):
        from utils.db import hash_password, verify_password
        password = 'test_password_123'
        hashed = hash_password(password)

        assert ':' in hashed
        assert verify_password(password, hashed)
        assert not verify_password('wrong_password', hashed)

    def test_verify_password_invalid_format(self):
        from utils.db import verify_password
        result = verify_password('password', 'invalid_hash_format')
        assert result is False


class TestInitDatabase:
    def test_init_database_creates_all_tables(self, monkeypatch):
        db_file = os.path.join(tempfile.gettempdir(), f'test_init_db_{os.getpid()}.db')

        import utils.db as db_conn_module
        monkeypatch.setattr(db_conn_module, 'DATABASE_FILE', db_file)

        from db.init_db import init_database
        init_database()

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        expected_tables = [
            'campuses', 'departments', 'majors', 'grades', 'classes',
            'users', 'class_teachers', 'punch_geofences', 'punch_time_slots',
            'punch_rules', 'punches', 'leaves', 'makeup_requests',
            'punch_config', 'operation_logs', 'notifications'
        ]

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        actual_tables = [row[0] for row in cursor.fetchall()]

        for table in expected_tables:
            assert table in actual_tables, f"Table {table} was not created"

        conn.close()

    def test_init_database_creates_read_views(self, monkeypatch):
        db_file = os.path.join(tempfile.gettempdir(), f'test_init_view_db_{os.getpid()}.db')

        import utils.db as db_conn_module
        monkeypatch.setattr(db_conn_module, 'DATABASE_FILE', db_file)

        from db.init_db import init_database
        init_database()

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        expected_views = [
            'v_leave_user_read',
            'v_makeup_user_read'
        ]
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        actual_views = [row[0] for row in cursor.fetchall()]

        for view_name in expected_views:
            assert view_name in actual_views, f"View {view_name} was not created"

        conn.close()

    def test_punch_config_initial_value(self, monkeypatch):
        db_file = os.path.join(tempfile.gettempdir(), f'test_config_db_{os.getpid()}.db')

        import utils.db as db_conn_module
        monkeypatch.setattr(db_conn_module, 'DATABASE_FILE', db_file)

        from db.init_db import init_database
        init_database()

        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM punch_config WHERE id = 1')
        row = cursor.fetchone()
        assert row is not None
        assert row['global_time_check_enabled'] == 1
        assert row['global_location_check_enabled'] == 1
        assert row['allow_multi_punch'] == 0
        assert row['allow_makeup'] == 1

        conn.close()
