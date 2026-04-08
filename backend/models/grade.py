from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Grade:
    id: int
    major_id: int
    year: int
    name: str
    created_at: datetime
