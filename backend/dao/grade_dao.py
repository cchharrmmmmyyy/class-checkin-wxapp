from models.grade import Grade
from .base_dao import BaseDAO


class GradeDAO(BaseDAO[Grade]):
    def __init__(self):
        super().__init__(Grade, 'grades', 'id')

    def delete(self, id: int) -> bool:
        return self.hard_delete(id)
