from typing import List, Optional
from models.punch import Punch


class PunchDAO:
    def __init__(self):
        from utils.db import get_connection
        self.get_connection = get_connection

    def _row_to_model(self, row):
        if row is None:
            return None
        return Punch(
            id=row['id'],
            user_id=row['user_id'],
            punch_date=row['punch_date'],
            punch_time=row['punch_time'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            matched_rule_id=row['matched_rule_id'],
            is_makeup=row['is_makeup'],
            device_id=row['device_id'],
            created_at=row['created_at']
        )

    def count(self, where: str = None, params: tuple = ()) -> int:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = "SELECT COUNT(*) FROM punches"
            if where:
                sql += f" WHERE {where}"
            cursor.execute(sql, params)
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def get_by_id(self, id: int) -> Optional[Punch]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM punches WHERE id = ?", (id,))
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            conn.close()

    def get_list(self, where: str = None, params: tuple = (), order_by: str = "id DESC",
                 limit: int = None, offset: int = 0) -> List[Punch]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM punches"
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
                """INSERT INTO punches (user_id, punch_date, punch_time, latitude, longitude,
                   matched_rule_id, is_makeup, device_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (data['user_id'], data['punch_date'], data['punch_time'], data['latitude'],
                 data['longitude'], data.get('matched_rule_id'), data.get('is_makeup', 0),
                 data.get('device_id'))
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
                """UPDATE punches SET user_id = ?, punch_date = ?, punch_time = ?, latitude = ?,
                   longitude = ?, matched_rule_id = ?, is_makeup = ?, device_id = ? WHERE id = ?""",
                (data['user_id'], data['punch_date'], data['punch_time'], data['latitude'],
                 data['longitude'], data.get('matched_rule_id'), data.get('is_makeup', 0),
                 data.get('device_id'), id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete(self, id: int) -> bool:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM punches WHERE id = ?", (id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_punch_by_user_and_date(self, user_id: str, punch_date: str) -> Optional[Punch]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM punches WHERE user_id = ? AND punch_date = ?", (user_id, punch_date))
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            conn.close()

    def get_punches_by_user(self, user_id: str, limit: int = 30) -> List[Punch]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM punches WHERE user_id = ? ORDER BY punch_date DESC LIMIT ?", (user_id, limit))
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
        finally:
            conn.close()

    def create_punch(self, user_id: str, punch_date: str, punch_time: str, latitude: float, longitude: float, is_makeup: int = 0) -> int:
        data = {
            'user_id': user_id,
            'punch_date': punch_date,
            'punch_time': punch_time,
            'latitude': latitude,
            'longitude': longitude,
            'is_makeup': is_makeup
        }
        return self.create(data)

    def count_by_date(self, date_str: str) -> int:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(DISTINCT user_id) FROM punches WHERE punch_date = ?",
                (date_str,)
            )
            return cursor.fetchone()[0]
        finally:
            conn.close()
