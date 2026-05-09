from typing import List, Optional
from models.class_teacher import ClassTeacher
from .base_dao import BaseDAO


class ClassTeacherDAO(BaseDAO[ClassTeacher]):
    def __init__(self):
        super().__init__(ClassTeacher, 'class_teachers', 'class_name')

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
        conn = self._get_connection()
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

    def create(self, data: dict) -> tuple:
        conn = self._get_connection()
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
        conn = self._get_connection()
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
        conn = self._get_connection()
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
