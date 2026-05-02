from typing import List, Optional
from models.punch_geofence import PunchGeofence


class PunchGeofenceDAO:
    def __init__(self):
        from utils.db import get_connection
        self.get_connection = get_connection

    def _row_to_model(self, row):
        if row is None:
            return None
        return PunchGeofence(
            id=row['id'],
            name=row['name'],
            fence_type=row['fence_type'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            radius=row['radius'],
            polygon_coords=row['polygon_coords'],
            enabled=row['enabled'],
            created_at=row['created_at'],
            deleted_at=row['deleted_at']
        )

    def get_by_id(self, id: int) -> Optional[PunchGeofence]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM punch_geofences WHERE id = ?", (id,))
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            conn.close()

    def get_list(self, where: str = None, params: tuple = (), order_by: str = "id ASC",
                 limit: int = None, offset: int = 0) -> List[PunchGeofence]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM punch_geofences"
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
                """INSERT INTO punch_geofences (name, fence_type, latitude, longitude, radius, polygon_coords, enabled)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (data['name'], data['fence_type'], data.get('latitude'), data.get('longitude'),
                 data.get('radius'), data.get('polygon_coords'), data.get('enabled', 1))
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def update(self, id: int, data: dict) -> bool:
        conn = self.get_connection()
        try:
            # 先获取当前记录
            current = self.get_by_id(id)
            if not current:
                return False
            
            # 使用当前值作为默认值
            name = data.get('name', current.name)
            fence_type = data.get('fence_type', current.fence_type)
            latitude = data.get('latitude', current.latitude)
            longitude = data.get('longitude', current.longitude)
            radius = data.get('radius', current.radius)
            polygon_coords = data.get('polygon_coords', current.polygon_coords)
            enabled = data.get('enabled', current.enabled)
            
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE punch_geofences SET name = ?, fence_type = ?, latitude = ?, longitude = ?,
                   radius = ?, polygon_coords = ?, enabled = ? WHERE id = ?""",
                (name, fence_type, latitude, longitude, radius, polygon_coords, enabled, id)
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
                "UPDATE punch_geofences SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?",
                (id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_enabled_geofences(self) -> List[PunchGeofence]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM punch_geofences WHERE enabled = 1 AND deleted_at IS NULL")
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
        finally:
            conn.close()

    def get_first_enabled(self) -> Optional[PunchGeofence]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM punch_geofences WHERE enabled = 1 AND deleted_at IS NULL LIMIT 1")
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            conn.close()
