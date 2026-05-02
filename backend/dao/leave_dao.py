from typing import List, Optional
from models.leave import Leave


class LeaveDAO:
    def __init__(self):
        from utils.db import get_connection
        self.get_connection = get_connection

    def _row_to_model(self, row):
        if row is None:
            return None
        return Leave(
            id=row['id'],
            user_id=row['user_id'],
            leave_start_date=row['leave_start_date'],
            leave_end_date=row['leave_end_date'],
            leave_type=row['leave_type'],
            leave_reason=row['leave_reason'],
            leave_status=row['leave_status'],
            approved_by=row['approved_by'],
            approved_at=row['approved_at'],
            created_at=row['created_at'],
            deleted_at=row['deleted_at']
        )

    def count(self, where: str = None, params: tuple = ()) -> int:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = "SELECT COUNT(*) FROM v_leave_user_read"
            if where:
                sql += f" WHERE {where}"
            cursor.execute(sql, params)
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def get_by_id(self, id: int) -> Optional[Leave]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM leaves WHERE id = ?", (id,))
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            conn.close()

    def get_list(self, where: str = None, params: tuple = (), order_by: str = "id DESC",
                 limit: int = None, offset: int = 0) -> List[Leave]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM leaves"
            if where:
                sql += f" WHERE {where}"
            sql += f" ORDER BY {order_by}"
            if limit is not None:
                sql += f" LIMIT {limit} OFFSET {offset}"
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
        finally:
            conn.close()

    def create(self, data: dict) -> int:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO leaves (user_id, leave_start_date, leave_end_date, leave_type, leave_reason)
                   VALUES (?, ?, ?, ?, ?)""",
                (data['user_id'], data['leave_start_date'], data['leave_end_date'],
                 data['leave_type'], data.get('leave_reason'))
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def update(self, id: int, data: dict) -> bool:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE leaves SET leave_status = ?, approved_by = ?, approved_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (data['leave_status'], data.get('approved_by'), id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete(self, id: int) -> bool:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE leaves SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?",
                (id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def create_leave_record(self, user_id: str, leave_start_date: str, leave_end_date: str, leave_type: str = 'personal', leave_reason: str = None) -> int:
        """创建请假记录"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO leaves (user_id, leave_start_date, leave_end_date, leave_type, leave_reason, leave_status) VALUES (?, ?, ?, ?, ?, 'pending')",
                (user_id, leave_start_date, leave_end_date, leave_type, leave_reason)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_leave_records_by_user(self, user_id: str):
        """获取用户的请假记录"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, user_id, leave_start_date, leave_end_date, leave_type, leave_reason, leave_status, approved_by, approved_at, created_at, deleted_at, username "
                "FROM v_leave_user_read "
                "WHERE user_id = ? AND deleted_at IS NULL "
                "ORDER BY created_at DESC",
                (user_id,)
            )
            return cursor.fetchall()
        finally:
            conn.close()

    def get_pending_leave_applications_by_class(self, class_name: str):
        """获取班级待审批的请假申请"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, user_id, leave_start_date, leave_end_date, leave_type, leave_reason, leave_status, approved_by, approved_at, created_at, deleted_at, username "
                "FROM v_leave_user_read "
                "WHERE class_name = ? AND leave_status = 'pending' AND deleted_at IS NULL "
                "ORDER BY created_at DESC",
                (class_name,)
            )
            return cursor.fetchall()
        finally:
            conn.close()

    def get_leave_record_by_id_and_class(self, leave_id: int, class_name: str):
        """根据ID和班级获取请假申请"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, user_id, leave_start_date, leave_end_date, leave_type, leave_reason, leave_status, approved_by, approved_at, created_at, deleted_at "
                "FROM v_leave_user_read "
                "WHERE id = ? AND class_name = ? AND deleted_at IS NULL",
                (leave_id, class_name)
            )
            return cursor.fetchone()
        finally:
            conn.close()

    def update_leave_status(self, leave_id: int, status: str) -> bool:
        """更新请假状态"""
        conn = self.get_connection()
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
        conn = self.get_connection()
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
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM leaves WHERE leave_status = 'pending' AND deleted_at IS NULL")
            return cursor.fetchone()[0]
        finally:
            conn.close()
