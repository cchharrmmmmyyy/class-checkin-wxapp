from typing import List, Optional
from models.punch_config import PunchConfig


class PunchConfigDAO:
    def __init__(self):
        from utils.db import get_connection
        self.get_connection = get_connection

    def _row_to_model(self, row):
        if row is None:
            return None
        return PunchConfig(
            id=row['id'],
            global_time_check_enabled=row['global_time_check_enabled'],
            global_location_check_enabled=row['global_location_check_enabled'],
            allow_multi_punch=row['allow_multi_punch'],
            allow_makeup=row['allow_makeup'],
            holiday_ranges=row['holiday_ranges'],
            updated_at=row['updated_at']
        )

    def get_config(self) -> Optional[PunchConfig]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM punch_config WHERE id = 1")
            row = cursor.fetchone()
            return self._row_to_model(row)
        finally:
            conn.close()

    def update(self, data: dict) -> bool:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE punch_config SET global_time_check_enabled = ?, global_location_check_enabled = ?,
                   allow_multi_punch = ?, allow_makeup = ?, holiday_ranges = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = 1""",
                (data['global_time_check_enabled'], data['global_location_check_enabled'],
                 data['allow_multi_punch'], data['allow_makeup'], data.get('holiday_ranges'))
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
