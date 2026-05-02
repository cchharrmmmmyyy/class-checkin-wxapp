from typing import List, Optional
from models.operation_log import OperationLog


class OperationLogDAO:
    def __init__(self):
        from utils.db import get_connection
        self.get_connection = get_connection

    def _row_to_model(self, row):
        if row is None:
            return None
        return OperationLog(
            id=row['id'],
            operator_id=row['operator_id'],
            operation_type=row['operation_type'],
            target_type=row['target_type'],
            target_id=row['target_id'],
            before_data=row['before_data'],
            after_data=row['after_data'],
            ip_address=row['ip_address'],
            created_at=row['created_at']
        )

    def count(self, where: str = None, params: tuple = (), conn=None) -> int:
        should_close = False
        if conn is None:
            conn = self.get_connection()
            should_close = True
        try:
            cursor = conn.cursor()
            sql = "SELECT COUNT(*) FROM operation_logs"
            if where:
                sql += f" WHERE {where}"
            cursor.execute(sql, params)
            return cursor.fetchone()[0]
        finally:
            if should_close:
                conn.close()

    def get_by_id(self, id: int, conn=None) -> Optional[OperationLog]:
        should_close = False
        if conn is None:
            conn = self.get_connection()
            should_close = True
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM operation_logs WHERE id = ?", (id,))
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            if should_close:
                conn.close()

    def get_list(self, where: str = None, params: tuple = (), order_by: str = "id DESC",
                 limit: int = None, offset: int = 0, conn=None) -> List[OperationLog]:
        should_close = False
        if conn is None:
            conn = self.get_connection()
            should_close = True
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM operation_logs"
            if where:
                sql += f" WHERE {where}"
            sql += f" ORDER BY {order_by}"
            if limit is not None:
                sql += f" LIMIT {limit} OFFSET {offset}"
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
        finally:
            if should_close:
                conn.close()

    def create(self, data: dict, conn=None) -> int:
        should_close = False
        if conn is None:
            conn = self.get_connection()
            should_close = True
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO operation_logs (operator_id, operation_type, target_type, target_id,
                   before_data, after_data, ip_address) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (data['operator_id'], data['operation_type'], data['target_type'], data['target_id'],
                 data.get('before_data'), data.get('after_data'), data.get('ip_address'))
            )
            if should_close:
                conn.commit()
            return cursor.lastrowid
        finally:
            if should_close:
                conn.close()
