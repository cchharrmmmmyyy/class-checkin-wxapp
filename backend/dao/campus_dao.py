from typing import List, Optional
from models.campus import Campus


class CampusDAO:
    def __init__(self):
        from utils.db import get_connection
        self.get_connection = get_connection

    def _row_to_model(self, row):
        if row is None:
            return None
        return Campus(
            id=row['id'],
            name=row['name'],
            address=row['address'],
            created_at=row['created_at']
        )

    def get_by_id(self, id: int) -> Optional[Campus]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM campuses WHERE id = ?", (id,))
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            conn.close()

    def get_list(self, where: str = None, params: tuple = (), order_by: str = "id ASC",
                 limit: int = None, offset: int = 0) -> List[Campus]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM campuses"
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
                "INSERT INTO campuses (name, address) VALUES (?, ?)",
                (data['name'], data.get('address'))
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
                "UPDATE campuses SET name = ?, address = ? WHERE id = ?",
                (data['name'], data.get('address'), id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete(self, id: int) -> bool:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM campuses WHERE id = ?", (id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
