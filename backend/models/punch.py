from dataclasses import dataclass
from datetime import datetime, date, time
from typing import Optional


@dataclass
class Punch:
    id: int
    user_id: str
    punch_date: date
    punch_time: time
    latitude: float
    longitude: float
    matched_rule_id: Optional[int]
    is_makeup: int
    device_id: Optional[str]
    created_at: datetime
