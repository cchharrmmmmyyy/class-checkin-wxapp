from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Notification:
    id: int
    receiver_id: str
    sender_id: Optional[str]
    title: str
    content: str
    type: str
    is_read: int
    related_id: Optional[str]
    created_at: datetime
