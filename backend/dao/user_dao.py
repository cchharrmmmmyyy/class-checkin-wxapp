from typing import List, Optional
from models.user import User


class UserDAO:
    def __init__(self):
        from utils.db import get_connection
        self.get_connection = get_connection

    def _row_to_model(self, row):
        if row is None:
            return None
        return User(
            user_id=row['user_id'],
            username=row['username'],
            password=row['password'],
            real_name=row['real_name'],
            role=row['role'],
            class_name=row['class_name'],
            student_id=row['student_id'],
            phone=row['phone'],
            email=row['email'],
            is_first_login=row['is_first_login'],
            last_punch_time=row['last_punch_time'],
            login_fail_count=row['login_fail_count'],
            lock_until=row['lock_until'],
            last_login_time=row['last_login_time'],
            last_login_ip=row['last_login_ip'],
            created_at=row['created_at'],
            deleted_at=row['deleted_at']
        )

    def get_by_id(self, user_id: str) -> Optional[User]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            conn.close()

    def get_list(self, where: str = None, params: tuple = (), order_by: str = "user_id ASC",
                 limit: int = None, offset: int = 0) -> List[User]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM users"
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
        from utils.password import hash_password
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO users (user_id, username, password, real_name, role, class_name,
                   student_id, phone, email, is_first_login) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (data['user_id'], data['username'], hash_password(data['password']), data['real_name'],
                 data['role'], data.get('class_name'), data.get('student_id'), data.get('phone'),
                 data.get('email'), data.get('is_first_login', 1))
            )
            conn.commit()
            return data['user_id']
        finally:
            conn.close()

    def update(self, user_id: str, data: dict) -> bool:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            fields = []
            values = []
            for key in ['username', 'real_name', 'role', 'class_name', 'student_id', 'phone', 'email']:
                if key in data:
                    fields.append(f"{key} = ?")
                    values.append(data[key])
            if 'password' in data:
                from utils.password import hash_password
                fields.append("password = ?")
                values.append(hash_password(data['password']))
            if not fields:
                return False
            values.append(user_id)
            sql = f"UPDATE users SET {', '.join(fields)} WHERE user_id = ?"
            cursor.execute(sql, tuple(values))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete(self, user_id: str) -> bool:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET deleted_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                (user_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_by_username(self, username: str) -> Optional[User]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND deleted_at IS NULL", (username,))
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            conn.close()

    def get_by_student_id(self, student_id: str) -> Optional[User]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE student_id = ? AND deleted_at IS NULL", (student_id,))
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            conn.close()

    def count(self, where: str = None, params: tuple = ()) -> int:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = "SELECT COUNT(*) FROM users"
            if where:
                sql += f" WHERE {where}"
            cursor.execute(sql, params)
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def count_by_role(self, role: str) -> int:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = ? AND deleted_at IS NULL", (role,))
            return cursor.fetchone()[0]
        finally:
            conn.close()
