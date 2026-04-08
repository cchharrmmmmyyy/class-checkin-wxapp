from typing import List, Optional
from models.notification import Notification


class NotificationDAO:
    def __init__(self):
        from db_connection import get_connection
        self.get_connection = get_connection

    def _row_to_model(self, row):
        if row is None:
            return None
        return Notification(
            id=row['id'],
            receiver_id=row['receiver_id'],
            sender_id=row['sender_id'],
            title=row['title'],
            content=row['content'],
            type=row['type'],
            is_read=row['is_read'],
            related_id=row['related_id'],
            created_at=row['created_at']
        )

    def get_by_id(self, id: int, conn=None) -> Optional[Notification]:
        should_close = False
        if conn is None:
            conn = self.get_connection()
            should_close = True
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notifications WHERE id = ?", (id,))
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            if should_close:
                conn.close()

    def get_list(self, where: str = None, params: tuple = (), order_by: str = "id DESC",
                 limit: int = None, offset: int = 0, conn=None) -> List[Notification]:
        should_close = False
        if conn is None:
            conn = self.get_connection()
            should_close = True
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM notifications"
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
                """INSERT INTO notifications (receiver_id, sender_id, title, content, type, related_id)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (data['receiver_id'], data.get('sender_id'), data['title'],
                 data['content'], data['type'], data.get('related_id'))
            )
            if should_close:
                conn.commit()
            return cursor.lastrowid
        finally:
            if should_close:
                conn.close()

    def mark_as_read(self, id: int, conn=None) -> bool:
        should_close = False
        if conn is None:
            conn = self.get_connection()
            should_close = True
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (id,))
            if should_close:
                conn.commit()
            return cursor.rowcount > 0
        finally:
            if should_close:
                conn.close()

    def delete(self, id: int, conn=None) -> bool:
        should_close = False
        if conn is None:
            conn = self.get_connection()
            should_close = True
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notifications WHERE id = ?", (id,))
            if should_close:
                conn.commit()
            return cursor.rowcount > 0
        finally:
            if should_close:
                conn.close()
