from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class OperationLog:
    id: int
    operator_id: str
    operation_type: str
    target_type: str
    target_id: str
    before_data: Optional[str]
    after_data: Optional[str]
    ip_address: Optional[str]
    created_at: datetime
