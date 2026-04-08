from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass
class MakeupRequest:
    id: int
    user_id: str
    target_date: date
    reason: Optional[str]
    status: str
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime
    deleted_at: Optional[datetime]
