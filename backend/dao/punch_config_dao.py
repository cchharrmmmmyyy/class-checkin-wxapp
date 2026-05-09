from typing import Optional
from models.punch_config import PunchConfig
from .base_dao import BaseDAO


class PunchConfigDAO(BaseDAO[PunchConfig]):
    def __init__(self):
        super().__init__(PunchConfig, 'punch_config', 'id')

    def get_config(self) -> Optional[PunchConfig]:
        return self.get_by_id(1)

    def update(self, data: dict) -> bool:
        conn = self._get_connection()
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
