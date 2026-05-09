from typing import List, Optional
from models.major import Major
from .base_dao import BaseDAO


class MajorDAO(BaseDAO[Major]):
    def __init__(self):
        super().__init__(Major, 'majors', 'id')

    def delete(self, id: int) -> bool:
        return self.hard_delete(id)
