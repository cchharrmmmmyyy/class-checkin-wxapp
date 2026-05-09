from typing import List, Optional
import sqlite3
from models.notification import Notification
from .base_dao import BaseDAO


class NotificationDAO(BaseDAO[Notification]):
    def __init__(self):
        super().__init__(Notification, 'notifications', 'id')

    def count(self, where: str = None, params: tuple = (), conn: sqlite3.Connection = None) -> int:
        return super().count(where, params, conn)

    def get_by_id(self, id: int, conn: sqlite3.Connection = None) -> Optional[Notification]:
        return super().get_by_id(id, conn)

    def get_list(self, where: str = None, params: tuple = (), order_by: str = "id DESC",
                 limit: int = None, offset: int = 0, conn: sqlite3.Connection = None) -> List[Notification]:
        return super().get_list(where, params, order_by, limit, offset, conn)

    def create(self, data: dict, conn: sqlite3.Connection = None) -> int:
        return super().create(data, conn)

    def mark_as_read(self, id: int, conn: sqlite3.Connection = None) -> bool:
        should_close = False
        if conn is None:
            conn = self._get_connection()
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

    def delete(self, id: int, conn: sqlite3.Connection = None) -> bool:
        return self.hard_delete(id, conn)
