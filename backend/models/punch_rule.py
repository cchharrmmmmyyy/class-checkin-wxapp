from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PunchRule:
    id: int
    time_slot_id: int
    geofence_id: int
    priority: int
    time_enabled: int
    location_enabled: int
    enabled: int
    created_at: datetime
    deleted_at: Optional[datetime]
