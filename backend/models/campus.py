from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Campus:
    id: int
    name: str
    address: Optional[str]
    created_at: datetime
