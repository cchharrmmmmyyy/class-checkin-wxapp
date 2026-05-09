from models.department import Department
from .base_dao import BaseDAO


class DepartmentDAO(BaseDAO[Department]):
    def __init__(self):
        super().__init__(Department, 'departments', 'id')

    def delete(self, id: int) -> bool:
        return self.hard_delete(id)
