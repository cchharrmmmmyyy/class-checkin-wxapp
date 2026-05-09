from typing import List, Optional
from models.punch_geofence import PunchGeofence
from .base_dao import BaseDAO


class PunchGeofenceDAO(BaseDAO[PunchGeofence]):
    def __init__(self):
        super().__init__(PunchGeofence, 'punch_geofences', 'id')

    def create(self, data: dict) -> int:
        data.setdefault('enabled', 1)
        return super().create(data)

    def get_enabled_geofences(self) -> List[PunchGeofence]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM punch_geofences WHERE enabled = 1 AND deleted_at IS NULL")
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]
        finally:
            conn.close()

    def get_first_enabled(self) -> Optional[PunchGeofence]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM punch_geofences WHERE enabled = 1 AND deleted_at IS NULL LIMIT 1")
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            conn.close()
