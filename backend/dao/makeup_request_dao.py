from typing import List, Optional
from models.makeup_request import MakeupRequest


class MakeupRequestDAO:
    def __init__(self):
        from db_connection import get_connection
        self.get_connection = get_connection

    def _row_to_model(self, row):
        if row is None:
            return None
        return MakeupRequest(
            id=row['id'],
            user_id=row['user_id'],
            target_date=row['target_date'],
            reason=row['reason'],
            status=row['status'],
            approved_by=row['approved_by'],
            approved_at=row['approved_at'],
            created_at=row['created_at'],
            deleted_at=row['deleted_at']
        )

    def get_by_id(self, id: int) -> Optional[MakeupRequest]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM makeup_requests WHERE id = ?", (id,))
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            conn.close()

    def get_list(self, where: str = None, params: tuple = (), order_by: str = "id DESC",
                 limit: int = None, offset: int = 0) -> List[MakeupRequest]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM makeup_requests"
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
                "INSERT INTO makeup_requests (user_id, target_date, reason) VALUES (?, ?, ?)",
                (data['user_id'], data['target_date'], data.get('reason'))
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
                """UPDATE makeup_requests SET status = ?, approved_by = ?, approved_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (data['status'], data.get('approved_by'), id)
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
                "UPDATE makeup_requests SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?",
                (id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_by_user_and_date(self, user_id: str, punch_date: str):
        """根据用户ID和打卡日期获取补卡申请"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM makeup_requests WHERE user_id = ? AND target_date = ? AND deleted_at IS NULL",
                (user_id, punch_date)
            )
            return cursor.fetchone()
        finally:
            conn.close()

    def get_by_user(self, user_id: str):
        """根据用户ID获取补卡申请"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM makeup_requests WHERE user_id = ? AND deleted_at IS NULL ORDER BY created_at DESC",
                (user_id,)
            )
            return cursor.fetchall()
        finally:
            conn.close()

    def get_pending_by_class(self, class_name: str):
        """获取班级待审批的补卡申请"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT mr.*, u.username 
                FROM makeup_requests mr
                JOIN users u ON mr.user_id = u.user_id
                WHERE u.class_name = ? AND mr.status = 'pending' AND mr.deleted_at IS NULL
                ORDER BY mr.created_at DESC
                """,
                (class_name,)
            )
            return cursor.fetchall()
        finally:
            conn.close()

    def get_by_id_and_class(self, request_id: int, class_name: str):
        """根据ID和班级获取补卡申请"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT mr.*
                FROM makeup_requests mr
                JOIN users u ON mr.user_id = u.user_id
                WHERE mr.id = ? AND u.class_name = ? AND mr.deleted_at IS NULL
                """,
                (request_id, class_name)
            )
            return cursor.fetchone()
        finally:
            conn.close()

    def update_status(self, request_id: int, status: str):
        """更新补卡申请状态"""
        conn = self.get_connection()
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

    def create(self, user_id: str, punch_date: str, reason: str) -> int:
        """创建补卡申请"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO makeup_requests (user_id, target_date, reason, status) VALUES (?, ?, ?, 'pending')",
                (user_id, punch_date, reason)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
