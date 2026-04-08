from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Department:
    id: int
    campus_id: int
    name: str
    code: Optional[str]
    created_at: datetime
