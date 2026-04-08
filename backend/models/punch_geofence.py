from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PunchGeofence:
    id: int
    name: str
    fence_type: str
    latitude: Optional[float]
    longitude: Optional[float]
    radius: Optional[int]
    polygon_coords: Optional[str]
    enabled: int
    created_at: datetime
    deleted_at: Optional[datetime]
