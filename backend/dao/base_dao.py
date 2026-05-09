import sqlite3
import re
import dataclasses
from typing import TypeVar, Generic, List, Optional, Type
from datetime import datetime

T = TypeVar('T')

VALID_TABLE_NAMES = {
    'campuses', 'departments', 'majors', 'grades', 'classes',
    'users', 'class_teachers', 'punch_geofences', 'punch_time_slots',
    'punch_rules', 'punches', 'leaves', 'makeup_requests', 'punch_config',
    'operation_logs', 'notifications'
}

VALID_COLUMN_PATTERNS = {
    'id': re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$'),
    'table_name': re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
}

SAFE_IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

SAFE_ORDER_BY_PATTERN = re.compile(
    r'^[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?\s+(ASC|DESC)$',
    re.IGNORECASE
)

SAFE_WHERE_PATTERN = re.compile(
    r'^[a-zA-Z_][a-zA-Z0-9_]*(?:[<>=!]+|\s+LIKE\s+|\s+IN\s+)\s*\?'
    r'(?:\s+AND\s+[a-zA-Z_][a-zA-Z0-9_]*(?:[<>=!]+|\s+LIKE\s+|\s+IN\s+)\s*\?)*$'
)

TABLES_WITH_SOFT_DELETE = {
    'campuses', 'departments', 'majors', 'grades', 'classes',
    'users', 'class_teachers', 'punch_geofences', 'punch_time_slots',
    'punch_rules', 'leaves', 'makeup_requests'
}

ORDER_BY_WHITELIST = {
    'id_desc': 'id DESC',
    'id_asc': 'id ASC',
    'create_time_desc': 'created_at DESC',
    'create_time_asc': 'created_at ASC',
    'update_time_desc': 'updated_at DESC',
    'update_time_asc': 'updated_at ASC',
    'punch_date_desc': 'punch_date DESC',
    'punch_date_asc': 'punch_date ASC',
    'punch_time_desc': 'punch_time DESC',
    'punch_time_asc': 'punch_time ASC',
    'created_at_desc': 'created_at DESC',
    'created_at_asc': 'created_at ASC',
    'title_desc': 'title DESC',
    'title_asc': 'title ASC',
    'name_desc': 'name DESC',
    'name_asc': 'name ASC',
    'class_name_desc': 'class_name DESC',
    'class_name_asc': 'class_name ASC',
    'user_id_desc': 'user_id DESC',
    'user_id_asc': 'user_id ASC',
    'priority_desc': 'priority DESC',
    'priority_asc': 'priority ASC',
}


class BaseDAO(Generic[T]):
    def __init__(self, model_class: Type[T], table_name: str, id_column: str):
        if table_name not in VALID_TABLE_NAMES:
            raise ValueError(f"Invalid table name: {table_name}")
        if not VALID_COLUMN_PATTERNS['id'].match(id_column):
            raise ValueError(f"Invalid id column name: {id_column}")
        self.model_class = model_class
        self.table_name = table_name
        self.id_column = id_column
        self.supports_soft_delete = table_name in TABLES_WITH_SOFT_DELETE

    def _get_connection(self):
        from utils.db import get_connection
        return get_connection()

    def _row_to_model(self, row: sqlite3.Row) -> Optional[T]:
        if row is None:
            return None
        model_field_names = {f.name for f in dataclasses.fields(self.model_class)}
        data = {k: v for k, v in dict(row).items() if k in model_field_names}
        for key, value in data.items():
            if isinstance(value, str):
                try:
                    if len(value) == 19 and value[10] == 'T':
                        data[key] = datetime.fromisoformat(value.replace('T', ' '))
                except (ValueError, AttributeError):
                    pass
        return self.model_class(**data)

    def _validate_identifier(self, identifier: str, identifier_type: str = 'column') -> bool:
        pattern = VALID_COLUMN_PATTERNS.get(identifier_type, VALID_COLUMN_PATTERNS['id'])
        if not pattern.match(identifier):
            raise ValueError(f"Invalid {identifier_type}: {identifier}")
        return True

    def _resolve_order_by(self, order_by: str) -> str:
        if order_by in ORDER_BY_WHITELIST:
            return ORDER_BY_WHITELIST[order_by]
        if SAFE_ORDER_BY_PATTERN.match(order_by):
            return order_by
        raise ValueError(f"Invalid order_by parameter: {order_by}")

    def count(self, where: str = None, params: tuple = (), conn: sqlite3.Connection = None) -> int:
        if where and not SAFE_WHERE_PATTERN.match(where):
            raise ValueError(f"Invalid where parameter: {where}")
        should_close = False
        if conn is None:
            conn = self._get_connection()
            should_close = True
        try:
            cursor = conn.cursor()
            sql = f"SELECT COUNT(*) FROM {self.table_name}"
            if where:
                sql += f" WHERE {where}"
            cursor.execute(sql, params)
            return cursor.fetchone()[0]
        finally:
            if should_close:
                conn.close()

    def get_by_id(self, id, conn: sqlite3.Connection = None) -> Optional[T]:
        should_close = False
        if conn is None:
            conn = self._get_connection()
            should_close = True
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE {self.id_column} = ?", (id,))
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            if should_close:
                conn.close()

    def get_list(self, where: str = None, params: tuple = (), order_by: str = None,
                 limit: int = None, offset: int = 0, conn: sqlite3.Connection = None) -> List[T]:
        if where and not SAFE_WHERE_PATTERN.match(where):
            raise ValueError(f"Invalid where parameter: {where}")
        should_close = False
        if conn is None:
            conn = self._get_connection()
            should_close = True
        try:
            cursor = conn.cursor()
            sql = f"SELECT * FROM {self.table_name}"
            if where:
                sql += f" WHERE {where}"
            if order_by:
                sql += f" ORDER BY {self._resolve_order_by(order_by)}"
            if limit is not None:
                sql += f" LIMIT {limit} OFFSET {offset}"
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
        finally:
            if should_close:
                conn.close()

    def create(self, data: dict, conn: sqlite3.Connection = None) -> int:
        for key in data.keys():
            if not SAFE_IDENTIFIER_PATTERN.match(key):
                raise ValueError(f"Invalid column name: {key}")
        should_close = False
        if conn is None:
            conn = self._get_connection()
            should_close = True
        try:
            cursor = conn.cursor()
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, tuple(data.values()))
            if should_close:
                conn.commit()
            return cursor.lastrowid
        finally:
            if should_close:
                conn.close()

    def update(self, id, data: dict, conn: sqlite3.Connection = None) -> bool:
        for key in data.keys():
            if not SAFE_IDENTIFIER_PATTERN.match(key):
                raise ValueError(f"Invalid column name: {key}")
        should_close = False
        if conn is None:
            conn = self._get_connection()
            should_close = True
        try:
            cursor = conn.cursor()
            set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
            sql = f"UPDATE {self.table_name} SET {set_clause} WHERE {self.id_column} = ?"
            cursor.execute(sql, tuple(data.values()) + (id,))
            if should_close:
                conn.commit()
            return cursor.rowcount > 0
        finally:
            if should_close:
                conn.close()

    def delete(self, id, conn: sqlite3.Connection = None) -> bool:
        if self.supports_soft_delete:
            return self.soft_delete(id, conn)
        return self.hard_delete(id, conn)

    def hard_delete(self, id, conn: sqlite3.Connection = None) -> bool:
        should_close = False
        if conn is None:
            conn = self._get_connection()
            should_close = True
        try:
            cursor = conn.cursor()
            sql = f"DELETE FROM {self.table_name} WHERE {self.id_column} = ?"
            cursor.execute(sql, (id,))
            if should_close:
                conn.commit()
            return cursor.rowcount > 0
        finally:
            if should_close:
                conn.close()

    def soft_delete(self, id, conn: sqlite3.Connection = None) -> bool:
        if not self.supports_soft_delete:
            raise NotImplementedError(f"Table {self.table_name} does not support soft delete")
        should_close = False
        if conn is None:
            conn = self._get_connection()
            should_close = True
        try:
            cursor = conn.cursor()
            sql = f"UPDATE {self.table_name} SET deleted_at = CURRENT_TIMESTAMP WHERE {self.id_column} = ?"
            cursor.execute(sql, (id,))
            if should_close:
                conn.commit()
            return cursor.rowcount > 0
        finally:
            if should_close:
                conn.close()
