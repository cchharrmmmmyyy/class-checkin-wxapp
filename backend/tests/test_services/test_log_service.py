import sys
import os
import importlib.util

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


def import_service_module_directly(module_name):
    module_path = os.path.join(backend_dir, 'services', f'{module_name}.py')
    spec = importlib.util.spec_from_file_location(f'services.{module_name}', module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[f'services.{module_name}'] = module
    spec.loader.exec_module(module)
    return module


class TestLogService:

    def test_log_operation_success(self):
        mock_dao = MagicMock()
        mock_dao.create.return_value = 1

        log_service_module = import_service_module_directly('log_service')
        log_service_module.operation_log_dao = mock_dao

        from services.log_service import LogService

        result = LogService.log_operation(
            operator_id='admin001',
            operation_type='LOGIN',
            target_type='USER',
            target_id='admin001',
            ip_address='127.0.0.1'
        )

        assert result == 1
        mock_dao.create.assert_called_once()
        call_args = mock_dao.create.call_args[0][0]
        assert call_args['operator_id'] == 'admin001'
        assert call_args['operation_type'] == 'LOGIN'

    def test_log_operation_invalid_type(self):
        log_service_module = import_service_module_directly('log_service')

        from services.log_service import LogService
        from utils.exceptions import ServiceException

        with pytest.raises(ServiceException) as exc_info:
            LogService.log_operation(
                operator_id='admin001',
                operation_type='INVALID_TYPE',
                target_type='USER',
                target_id='admin001'
            )

        assert exc_info.value.code == 9001

    def test_get_operation_logs_with_filters(self):
        from models.operation_log import OperationLog

        mock_log = OperationLog(
            id=1,
            operator_id='admin001',
            operation_type='LOGIN',
            target_type='USER',
            target_id='admin001',
            before_data=None,
            after_data=None,
            ip_address='127.0.0.1',
            created_at=datetime.now()
        )

        mock_dao = MagicMock()
        mock_dao.get_list.return_value = [mock_log]

        log_service_module = import_service_module_directly('log_service')
        log_service_module.operation_log_dao = mock_dao

        from services.log_service import LogService

        result = LogService.get_operation_logs(
            operator_id='admin001',
            operation_type='LOGIN',
            limit=50,
            offset=0
        )

        assert len(result) == 1
        assert result[0]['operator_id'] == 'admin001'
        assert result[0]['operation_type'] == 'LOGIN'

    def test_get_user_operation_logs(self):
        from models.operation_log import OperationLog

        mock_log = OperationLog(
            id=1,
            operator_id='S2024001',
            operation_type='PUNCH',
            target_type='PUNCH',
            target_id='1',
            before_data=None,
            after_data=None,
            ip_address=None,
            created_at=datetime.now()
        )

        mock_dao = MagicMock()
        mock_dao.get_list.return_value = [mock_log]

        log_service_module = import_service_module_directly('log_service')
        log_service_module.operation_log_dao = mock_dao

        from services.log_service import LogService

        result = LogService.get_user_operation_logs(
            user_id='S2024001',
            operation_type='PUNCH'
        )

        assert len(result) == 1
        assert result[0]['operator_id'] == 'S2024001'

    def test_get_target_logs(self):
        from models.operation_log import OperationLog

        mock_log = OperationLog(
            id=1,
            operator_id='T2024001',
            operation_type='APPROVE',
            target_type='LEAVE',
            target_id='leave001',
            before_data=None,
            after_data='{"status": "approved"}',
            ip_address=None,
            created_at=datetime.now()
        )

        mock_dao = MagicMock()
        mock_dao.get_list.return_value = [mock_log]

        log_service_module = import_service_module_directly('log_service')
        log_service_module.operation_log_dao = mock_dao

        from services.log_service import LogService

        result = LogService.get_target_logs(
            target_type='LEAVE',
            target_id='leave001'
        )

        assert len(result) == 1
        assert result[0]['target_type'] == 'LEAVE'
        assert result[0]['target_id'] == 'leave001'

    def test_log_operation_with_transaction(self):
        mock_dao = MagicMock()
        mock_dao.create.return_value = 1
        mock_conn = MagicMock()

        log_service_module = import_service_module_directly('log_service')
        log_service_module.operation_log_dao = mock_dao

        from services.log_service import LogService

        result = LogService.log_operation(
            operator_id='admin001',
            operation_type='BULK_IMPORT',
            target_type='USERS',
            target_id='batch001',
            ip_address='127.0.0.1',
            conn=mock_conn
        )

        assert result == 1
        call_kwargs = mock_dao.create.call_args[1]
        assert call_kwargs['conn'] == mock_conn
