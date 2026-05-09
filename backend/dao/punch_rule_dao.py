from typing import List, Optional
from models.punch_rule import PunchRule
from .base_dao import BaseDAO


class PunchRuleDAO(BaseDAO[PunchRule]):
    def __init__(self):
        super().__init__(PunchRule, 'punch_rules', 'id')

    def create(self, data: dict) -> int:
        data.setdefault('priority', 100)
        data.setdefault('time_enabled', 1)
        data.setdefault('location_enabled', 1)
        data.setdefault('enabled', 1)
        return super().create(data)

    def update(self, id: int, data: dict) -> bool:
        data.setdefault('priority', 100)
        data.setdefault('time_enabled', 1)
        data.setdefault('location_enabled', 1)
        data.setdefault('enabled', 1)
        return super().update(id, data)
