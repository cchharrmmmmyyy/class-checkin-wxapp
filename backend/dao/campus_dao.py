from models.campus import Campus
from .base_dao import BaseDAO


class CampusDAO(BaseDAO[Campus]):
    def __init__(self):
        super().__init__(Campus, 'campuses', 'id')

    def delete(self, id: int) -> bool:
        return self.hard_delete(id)
