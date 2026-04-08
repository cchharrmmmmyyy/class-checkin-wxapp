from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Class:
    class_name: str
    grade_id: int
    created_at: datetime
    deleted_at: Optional[datetime]
