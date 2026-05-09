from typing import List, Optional
import sqlite3
from models.operation_log import OperationLog
from .base_dao import BaseDAO


class OperationLogDAO(BaseDAO[OperationLog]):
    def __init__(self):
        super().__init__(OperationLog, 'operation_logs', 'id')

    def count(self, where: str = None, params: tuple = (), conn: sqlite3.Connection = None) -> int:
        return super().count(where, params, conn)

    def get_by_id(self, id: int, conn: sqlite3.Connection = None) -> Optional[OperationLog]:
        return super().get_by_id(id, conn)

    def get_list(self, where: str = None, params: tuple = (), order_by: str = "id DESC",
                 limit: int = None, offset: int = 0, conn: sqlite3.Connection = None) -> List[OperationLog]:
        return super().get_list(where, params, order_by, limit, offset, conn)

    def create(self, data: dict, conn: sqlite3.Connection = None) -> int:
        return super().create(data, conn)
