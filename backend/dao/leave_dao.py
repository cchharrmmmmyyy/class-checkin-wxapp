from typing import List, Optional
from models.leave import Leave
from .base_dao import BaseDAO


class LeaveDAO(BaseDAO[Leave]):
    def __init__(self):
        super().__init__(Leave, 'leaves', 'id')

    def count(self, where: str = None, params: tuple = ()) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            sql = "SELECT COUNT(*) FROM v_leave_user_read"
            if where:
                sql += f" WHERE {where}"
            cursor.execute(sql, params)
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def get_leave_records_by_user(self, user_id: str) -> List[Leave]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, user_id, leave_start_date, leave_end_date, leave_type, leave_reason, "
                "leave_status, approved_by, approved_at, created_at, deleted_at "
                "FROM v_leave_user_read "
                "WHERE user_id = ? AND deleted_at IS NULL "
                "ORDER BY created_at DESC",
                (user_id,)
            )
            return [self._row_to_model(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_pending_leave_applications_by_class(self, class_name: str) -> List[Leave]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, user_id, leave_start_date, leave_end_date, leave_type, leave_reason, "
                "leave_status, approved_by, approved_at, created_at, deleted_at "
                "FROM v_leave_user_read "
                "WHERE class_name = ? AND leave_status = 'pending' AND deleted_at IS NULL "
                "ORDER BY created_at DESC",
                (class_name,)
            )
            return [self._row_to_model(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_leave_record_by_id_and_class(self, leave_id: int, class_name: str) -> Optional[Leave]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, user_id, leave_start_date, leave_end_date, leave_type, leave_reason, leave_status, approved_by, approved_at, created_at, deleted_at "
                "FROM v_leave_user_read "
                "WHERE id = ? AND class_name = ? AND deleted_at IS NULL",
                (leave_id, class_name)
            )
            return self._row_to_model(cursor.fetchone())
        finally:
            conn.close()

    def update_leave_status(self, leave_id: int, status: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE leaves SET leave_status = ?, approved_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, leave_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def count_approved_by_date(self, date_str: str) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM leaves WHERE leave_status = 'approved' AND ? BETWEEN leave_start_date AND leave_end_date AND deleted_at IS NULL",
                (date_str,)
            )
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def count_pending(self) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM leaves WHERE leave_status = 'pending' AND deleted_at IS NULL")
            return cursor.fetchone()[0]
        finally:
            conn.close()
