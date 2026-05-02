from typing import List, Optional
from models.class_model import Class


class ClassDAO:
    def __init__(self):
        from utils.db import get_connection
        self.get_connection = get_connection

    def _row_to_model(self, row):
        if row is None:
            return None
        return Class(
            class_name=row['class_name'],
            grade_id=row['grade_id'],
            created_at=row['created_at'],
            deleted_at=row['deleted_at']
        )

    def get_by_id(self, class_name: str) -> Optional[Class]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM classes WHERE class_name = ?", (class_name,))
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            conn.close()

    def get_list(self, where: str = None, params: tuple = (), order_by: str = "class_name ASC",
                 limit: int = None, offset: int = 0) -> List[Class]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM classes"
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

    def create(self, data: dict) -> str:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO classes (class_name, grade_id) VALUES (?, ?)",
                (data['class_name'], data['grade_id'])
            )
            conn.commit()
            return data['class_name']
        finally:
            conn.close()

    def update(self, class_name: str, data: dict) -> bool:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE classes SET grade_id = ? WHERE class_name = ?",
                (data['grade_id'], class_name)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete(self, class_name: str) -> bool:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE classes SET deleted_at = CURRENT_TIMESTAMP WHERE class_name = ?",
                (class_name,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
