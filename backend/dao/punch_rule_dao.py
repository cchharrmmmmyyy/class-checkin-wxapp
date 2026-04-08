from typing import List, Optional
from models.punch_rule import PunchRule


class PunchRuleDAO:
    def __init__(self):
        from db_connection import get_connection
        self.get_connection = get_connection

    def _row_to_model(self, row):
        if row is None:
            return None
        return PunchRule(
            id=row['id'],
            time_slot_id=row['time_slot_id'],
            geofence_id=row['geofence_id'],
            priority=row['priority'],
            time_enabled=row['time_enabled'],
            location_enabled=row['location_enabled'],
            enabled=row['enabled'],
            created_at=row['created_at'],
            deleted_at=row['deleted_at']
        )

    def get_by_id(self, id: int) -> Optional[PunchRule]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM punch_rules WHERE id = ?", (id,))
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            conn.close()

    def get_list(self, where: str = None, params: tuple = (), order_by: str = "priority ASC",
                 limit: int = None, offset: int = 0) -> List[PunchRule]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM punch_rules"
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
                """INSERT INTO punch_rules (time_slot_id, geofence_id, priority, time_enabled, location_enabled, enabled)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (data['time_slot_id'], data['geofence_id'], data.get('priority', 100),
                 data.get('time_enabled', 1), data.get('location_enabled', 1), data.get('enabled', 1))
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
                """UPDATE punch_rules SET time_slot_id = ?, geofence_id = ?, priority = ?,
                   time_enabled = ?, location_enabled = ?, enabled = ? WHERE id = ?""",
                (data['time_slot_id'], data['geofence_id'], data.get('priority', 100),
                 data.get('time_enabled', 1), data.get('location_enabled', 1), data.get('enabled', 1), id)
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
                "UPDATE punch_rules SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?",
                (id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
