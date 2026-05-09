from typing import List, Optional
from models.punch import Punch
from .base_dao import BaseDAO


class PunchDAO(BaseDAO[Punch]):
    def __init__(self):
        super().__init__(Punch, 'punches', 'id')

    def get_punch_by_user_and_date(self, user_id: str, punch_date: str) -> Optional[Punch]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM punches WHERE user_id = ? AND punch_date = ?", (user_id, punch_date))
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            conn.close()

    def get_punches_by_user(self, user_id: str, limit: int = None) -> List[Punch]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if limit is not None:
                cursor.execute("SELECT * FROM punches WHERE user_id = ? ORDER BY punch_date DESC LIMIT ?", (user_id, limit))
            else:
                cursor.execute("SELECT * FROM punches WHERE user_id = ? ORDER BY punch_date DESC", (user_id,))
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
        finally:
            conn.close()

    def count_by_date(self, date_str: str) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(DISTINCT user_id) FROM punches WHERE punch_date = ?",
                (date_str,)
            )
            return cursor.fetchone()[0]
        finally:
            conn.close()
