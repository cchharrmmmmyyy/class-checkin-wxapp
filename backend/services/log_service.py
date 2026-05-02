from datetime import datetime
from typing import List, Optional
from dao import operation_log_dao
from utils.exceptions import ServiceException


class LogService:

    @staticmethod
    def log_operation(operator_id: str, operation_type: str, target_type: str,
                      target_id: str, before_data: str = None, after_data: str = None,
                      ip_address: str = None, conn=None) -> int:
        valid_types = ['LOGIN', 'LOGOUT', 'PUNCH', 'LEAVE', 'MAKEUP', 'APPROVE', 'REJECT',
                       'CREATE', 'UPDATE', 'DELETE', 'BULK_IMPORT', 'CONFIG_UPDATE']
        if operation_type not in valid_types:
            raise ServiceException(
                f'无效的操作类型: {operation_type}',
                code=9001,
                http_status=400
            )

        data = {
            'operator_id': operator_id,
            'operation_type': operation_type,
            'target_type': target_type,
            'target_id': target_id,
            'before_data': before_data,
            'after_data': after_data,
            'ip_address': ip_address
        }

        return operation_log_dao.create(data, conn=conn)

    @staticmethod
    def get_operation_logs(target_type: str = None, target_id: str = None,
                          operator_id: str = None, operation_type: str = None,
                          start_date: str = None, end_date: str = None,
                          page: int = 1, size: int = 50) -> dict:
        conditions = []
        params = []

        if target_type:
            conditions.append('target_type = ?')
            params.append(target_type)
        if target_id:
            conditions.append('target_id = ?')
            params.append(target_id)
        if operator_id:
            conditions.append('operator_id = ?')
            params.append(operator_id)
        if operation_type:
            conditions.append('operation_type = ?')
            params.append(operation_type)
        if start_date:
            conditions.append('created_at >= ?')
            params.append(start_date)
        if end_date:
            conditions.append('created_at <= ?')
            params.append(end_date)

        where = ' AND '.join(conditions) if conditions else None
        order_by = 'created_at DESC'

        dao = operation_log_dao.OperationLogDAO()
        total = dao.count(where=where, params=tuple(params))
        
        offset = (page - 1) * size
        logs = dao.get_list(
            where=where,
            params=tuple(params),
            order_by=order_by,
            limit=size,
            offset=offset
        )

        items = [
            {
                'id': log.id,
                'operator_id': log.operator_id,
                'operation_type': log.operation_type,
                'target_type': log.target_type,
                'target_id': log.target_id,
                'before_data': log.before_data,
                'after_data': log.after_data,
                'ip_address': log.ip_address,
                'created_at': log.created_at.isoformat() if log.created_at else None
            }
            for log in logs
        ]
        
        total_pages = (total + size - 1) // size if total else 0
        return {
            'items': items,
            'total': total,
            'page': page,
            'size': size,
            'total_pages': total_pages,
            'has_next': page < total_pages
        }

    @staticmethod
    def get_user_operation_logs(user_id: str, operation_type: str = None,
                                limit: int = 50, offset: int = 0) -> List[dict]:
        return LogService.get_operation_logs(
            operator_id=user_id,
            operation_type=operation_type,
            limit=limit,
            offset=offset
        )

    @staticmethod
    def get_target_logs(target_type: str, target_id: str,
                       limit: int = 50, offset: int = 0) -> List[dict]:
        return LogService.get_operation_logs(
            target_type=target_type,
            target_id=target_id,
            limit=limit,
            offset=offset
        )
