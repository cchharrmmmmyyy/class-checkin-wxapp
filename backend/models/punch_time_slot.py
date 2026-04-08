from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional


@dataclass
class PunchTimeSlot:
    id: int
    name: str
    start_time: time
    end_time: time
    enabled: int
    created_at: datetime
    deleted_at: Optional[datetime]
