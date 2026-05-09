from models.punch_rule import PunchRule
from .base_dao import BaseDAO
from utils.constants import ENABLED, DEFAULT_PRIORITY


class PunchRuleDAO(BaseDAO[PunchRule]):
    def __init__(self):
        super().__init__(PunchRule, 'punch_rules', 'id')

    def create(self, data: dict) -> int:
        data.setdefault('priority', DEFAULT_PRIORITY)
        data.setdefault('time_enabled', ENABLED)
        data.setdefault('location_enabled', ENABLED)
        data.setdefault('enabled', ENABLED)
        return super().create(data)

    def update(self, id: int, data: dict) -> bool:
        data.setdefault('priority', DEFAULT_PRIORITY)
        data.setdefault('time_enabled', ENABLED)
        data.setdefault('location_enabled', ENABLED)
        data.setdefault('enabled', ENABLED)
        return super().update(id, data)
