from typing import List, Optional
from models.class_teacher import ClassTeacher


class ClassTeacherDAO:
    def __init__(self):
        from utils.db import get_connection
        self.get_connection = get_connection

    def _row_to_model(self, row):
        if row is None:
            return None
        return ClassTeacher(
            class_name=row['class_name'],
            teacher_id=row['teacher_id'],
            semester=row['semester'],
            created_at=row['created_at'],
            deleted_at=row['deleted_at']
        )

    def get_by_id(self, class_name: str, teacher_id: str) -> Optional[ClassTeacher]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM class_teachers WHERE class_name = ? AND teacher_id = ?",
                (class_name, teacher_id)
            )
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            conn.close()

    def get_list(self, where: str = None, params: tuple = (), order_by: str = "class_name ASC",
                 limit: int = None, offset: int = 0) -> List[ClassTeacher]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM class_teachers"
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

    def create(self, data: dict) -> tuple:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO class_teachers (class_name, teacher_id, semester) VALUES (?, ?, ?)",
                (data['class_name'], data['teacher_id'], data.get('semester'))
            )
            conn.commit()
            return (data['class_name'], data['teacher_id'])
        finally:
            conn.close()

    def update(self, class_name: str, teacher_id: str, data: dict) -> bool:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE class_teachers SET semester = ? WHERE class_name = ? AND teacher_id = ?",
                (data.get('semester'), class_name, teacher_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete(self, class_name: str, teacher_id: str) -> bool:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE class_teachers SET deleted_at = CURRENT_TIMESTAMP WHERE class_name = ? AND teacher_id = ?",
                (class_name, teacher_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
