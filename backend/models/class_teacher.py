from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ClassTeacher:
    class_name: str
    teacher_id: str
    semester: Optional[str]
    created_at: datetime
    deleted_at: Optional[datetime]
