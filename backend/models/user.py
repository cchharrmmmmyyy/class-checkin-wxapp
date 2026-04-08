from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    user_id: str
    username: str
    password: str
    real_name: str
    role: str
    class_name: Optional[str]
    student_id: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    is_first_login: int
    last_punch_time: Optional[datetime]
    login_fail_count: int
    lock_until: Optional[datetime]
    last_login_time: Optional[datetime]
    last_login_ip: Optional[str]
    created_at: datetime
    deleted_at: Optional[datetime]
