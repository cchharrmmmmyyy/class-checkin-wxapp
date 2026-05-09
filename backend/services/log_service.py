from datetime import datetime
from typing import List, Optional
from dao import operation_log_dao
from utils.exceptions import ServiceException
from utils.pagination import paginate, normalize_pagination
from utils import error_codes as EC


operation_log_dao_instance = operation_log_dao.OperationLogDAO()


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
                code=EC.LOG_INVALID_TYPE,
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

        return operation_log_dao_instance.create(data, conn=conn)

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

        total = operation_log_dao_instance.count(where=where, params=tuple(params))
        
        page, size, offset = normalize_pagination(page, size)
        logs = operation_log_dao_instance.get_list(
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
        
        return paginate(items, total, page, size)

    @staticmethod
    def get_user_operation_logs(user_id: str, operation_type: str = None,
                                page: int = 1, size: int = 50) -> dict:
        return LogService.get_operation_logs(
            operator_id=user_id,
            operation_type=operation_type,
            page=page,
            size=size
        )

    @staticmethod
    def get_target_logs(target_type: str, target_id: str,
                       page: int = 1, size: int = 50) -> dict:
        return LogService.get_operation_logs(
            target_type=target_type,
            target_id=target_id,
            page=page,
            size=size
        )
