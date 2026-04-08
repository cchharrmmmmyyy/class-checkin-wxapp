from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PunchConfig:
    id: int
    global_time_check_enabled: int
    global_location_check_enabled: int
    allow_multi_punch: int
    allow_makeup: int
    holiday_ranges: Optional[str]
    updated_at: datetime
