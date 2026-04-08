from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass
class Leave:
    id: int
    user_id: str
    leave_start_date: date
    leave_end_date: date
    leave_type: str
    leave_reason: Optional[str]
    leave_status: str
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime
    deleted_at: Optional[datetime]
