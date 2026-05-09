from typing import List, Optional
from models.makeup_request import MakeupRequest
from .base_dao import BaseDAO


class MakeupRequestDAO(BaseDAO[MakeupRequest]):
    def __init__(self):
        super().__init__(MakeupRequest, 'makeup_requests', 'id')

    def count(self, where: str = None, params: tuple = ()) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            sql = "SELECT COUNT(*) FROM v_makeup_user_read"
            if where:
                sql += f" WHERE {where}"
            cursor.execute(sql, params)
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def get_by_user_and_date(self, user_id: str, punch_date: str) -> Optional[MakeupRequest]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM makeup_requests WHERE user_id = ? AND target_date = ? AND deleted_at IS NULL",
                (user_id, punch_date)
            )
            return self._row_to_model(cursor.fetchone())
        finally:
            conn.close()

    def get_by_user(self, user_id: str) -> List[MakeupRequest]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM makeup_requests WHERE user_id = ? AND deleted_at IS NULL ORDER BY created_at DESC",
                (user_id,)
            )
            return [self._row_to_model(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_pending_by_class(self, class_name: str) -> List[MakeupRequest]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, user_id, target_date, reason, status, approved_by, approved_at, created_at, deleted_at
                FROM v_makeup_user_read
                WHERE class_name = ? AND status = 'pending' AND deleted_at IS NULL
                ORDER BY created_at DESC
                """,
                (class_name,)
            )
            return [self._row_to_model(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_by_id_and_class(self, request_id: int, class_name: str) -> Optional[MakeupRequest]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, user_id, target_date, reason, status, approved_by, approved_at, created_at, deleted_at
                FROM v_makeup_user_read
                WHERE id = ? AND class_name = ? AND deleted_at IS NULL
                """,
                (request_id, class_name)
            )
            return self._row_to_model(cursor.fetchone())
        finally:
            conn.close()

    def update_status(self, request_id: int, status: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE makeup_requests SET status = ?, approved_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, request_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
