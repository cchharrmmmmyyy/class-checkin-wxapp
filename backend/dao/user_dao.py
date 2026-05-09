from typing import Optional
from models.user import User
from .base_dao import BaseDAO
from utils.constants import ENABLED


class UserDAO(BaseDAO[User]):
    def __init__(self):
        super().__init__(User, 'users', 'user_id')

    def create(self, data: dict) -> str:
        data.setdefault('is_first_login', ENABLED)
        super().create(data)
        return data['user_id']

    def update(self, user_id: str, data: dict) -> bool:
        return super().update(user_id, data)

    def get_by_username(self, username: str) -> Optional[User]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND deleted_at IS NULL", (username,))
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            conn.close()

    def get_by_student_id(self, student_id: str) -> Optional[User]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE student_id = ? AND deleted_at IS NULL", (student_id,))
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            conn.close()

    def count_by_role(self, role: str) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = ? AND deleted_at IS NULL", (role,))
            return cursor.fetchone()[0]
        finally:
            conn.close()
