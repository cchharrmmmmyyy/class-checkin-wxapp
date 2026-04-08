from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Major:
    id: int
    department_id: int
    name: str
    code: Optional[str]
    created_at: datetime
