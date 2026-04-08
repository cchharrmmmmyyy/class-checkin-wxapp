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


class TestNotificationService:

    def test_send_notification_success(self):
        mock_dao = MagicMock()
        mock_dao.create.return_value = 1

        notification_module = import_service_module_directly('notification_service')
        notification_module.notification_dao = mock_dao

        from services.notification_service import NotificationService

        result = NotificationService.send_notification(
            receiver_id='S2024001',
            title='打卡提醒',
            content='请注意今日打卡',
            notification_type='REMINDER',
            sender_id='SYSTEM'
        )

        assert result == 1
        mock_dao.create.assert_called_once()
        call_args = mock_dao.create.call_args[0][0]
        assert call_args['receiver_id'] == 'S2024001'
        assert call_args['title'] == '打卡提醒'

    def test_send_notification_invalid_type(self):
        notification_module = import_service_module_directly('notification_service')

        from services.notification_service import NotificationService
        from utils.exceptions import ServiceException

        with pytest.raises(ServiceException) as exc_info:
            NotificationService.send_notification(
                receiver_id='S2024001',
                title='测试',
                content='测试内容',
                notification_type='INVALID_TYPE'
            )

        assert exc_info.value.code == 8001

    def test_send_batch_notifications(self):
        mock_dao = MagicMock()
        mock_dao.create.side_effect = [1, 2, 3]

        notification_module = import_service_module_directly('notification_service')
        notification_module.notification_dao = mock_dao

        from services.notification_service import NotificationService

        result = NotificationService.send_batch_notifications(
            receiver_ids=['S2024001', 'S2024002', 'S2024003'],
            title='批量通知',
            content='这是一条批量通知',
            notification_type='ANNOUNCEMENT',
            sender_id='SYSTEM'
        )

        assert result == [1, 2, 3]
        assert mock_dao.create.call_count == 3

    def test_get_user_notifications(self):
        from models.notification import Notification

        mock_notification = Notification(
            id=1,
            receiver_id='S2024001',
            sender_id='SYSTEM',
            title='打卡提醒',
            content='请注意今日打卡',
            type='REMINDER',
            is_read=0,
            related_id=None,
            created_at=datetime.now()
        )

        mock_dao = MagicMock()
        mock_dao.get_list.return_value = [mock_notification]

        notification_module = import_service_module_directly('notification_service')
        notification_module.notification_dao = mock_dao

        from services.notification_service import NotificationService

        result = NotificationService.get_user_notifications(
            user_id='S2024001',
            notification_type='REMINDER'
        )

        assert len(result) == 1
        assert result[0]['receiver_id'] == 'S2024001'
        assert result[0]['is_read'] is False

    def test_get_unread_count(self):
        from models.notification import Notification

        mock_notification = Notification(
            id=1,
            receiver_id='S2024001',
            sender_id='SYSTEM',
            title='打卡提醒',
            content='请注意今日打卡',
            type='REMINDER',
            is_read=0,
            related_id=None,
            created_at=datetime.now()
        )

        mock_dao = MagicMock()
        mock_dao.get_list.return_value = [mock_notification]

        notification_module = import_service_module_directly('notification_service')
        notification_module.notification_dao = mock_dao

        from services.notification_service import NotificationService

        result = NotificationService.get_unread_count(user_id='S2024001')

        assert result == 1

    def test_mark_as_read_success(self):
        from models.notification import Notification

        mock_notification = Notification(
            id=1,
            receiver_id='S2024001',
            sender_id='SYSTEM',
            title='打卡提醒',
            content='请注意今日打卡',
            type='REMINDER',
            is_read=0,
            related_id=None,
            created_at=datetime.now()
        )

        mock_dao = MagicMock()
        mock_dao.get_by_id.return_value = mock_notification
        mock_dao.mark_as_read.return_value = True

        notification_module = import_service_module_directly('notification_service')
        notification_module.notification_dao = mock_dao

        from services.notification_service import NotificationService

        result = NotificationService.mark_as_read(
            notification_id=1,
            user_id='S2024001'
        )

        assert result is True
        mock_dao.mark_as_read.assert_called_once_with(1)

    def test_mark_as_read_not_found(self):
        mock_dao = MagicMock()
        mock_dao.get_by_id.return_value = None

        notification_module = import_service_module_directly('notification_service')
        notification_module.notification_dao = mock_dao

        from services.notification_service import NotificationService
        from utils.exceptions import ServiceException

        with pytest.raises(ServiceException) as exc_info:
            NotificationService.mark_as_read(
                notification_id=999,
                user_id='S2024001'
            )

        assert exc_info.value.code == 8002

    def test_mark_as_read_wrong_user(self):
        from models.notification import Notification

        mock_notification = Notification(
            id=1,
            receiver_id='S2024001',
            sender_id='SYSTEM',
            title='打卡提醒',
            content='请注意今日打卡',
            type='REMINDER',
            is_read=0,
            related_id=None,
            created_at=datetime.now()
        )

        mock_dao = MagicMock()
        mock_dao.get_by_id.return_value = mock_notification

        notification_module = import_service_module_directly('notification_service')
        notification_module.notification_dao = mock_dao

        from services.notification_service import NotificationService
        from utils.exceptions import ServiceException

        with pytest.raises(ServiceException) as exc_info:
            NotificationService.mark_as_read(
                notification_id=1,
                user_id='S2024002'
            )

        assert exc_info.value.code == 8003

    def test_delete_notification_success(self):
        from models.notification import Notification

        mock_notification = Notification(
            id=1,
            receiver_id='S2024001',
            sender_id='SYSTEM',
            title='打卡提醒',
            content='请注意今日打卡',
            type='REMINDER',
            is_read=1,
            related_id=None,
            created_at=datetime.now()
        )

        mock_dao = MagicMock()
        mock_dao.get_by_id.return_value = mock_notification
        mock_dao.delete.return_value = True

        notification_module = import_service_module_directly('notification_service')
        notification_module.notification_dao = mock_dao

        from services.notification_service import NotificationService

        result = NotificationService.delete_notification(
            notification_id=1,
            user_id='S2024001'
        )

        assert result is True
        mock_dao.delete.assert_called_once_with(1)

    def test_delete_notification_wrong_user(self):
        from models.notification import Notification

        mock_notification = Notification(
            id=1,
            receiver_id='S2024001',
            sender_id='SYSTEM',
            title='打卡提醒',
            content='请注意今日打卡',
            type='REMINDER',
            is_read=1,
            related_id=None,
            created_at=datetime.now()
        )

        mock_dao = MagicMock()
        mock_dao.get_by_id.return_value = mock_notification

        notification_module = import_service_module_directly('notification_service')
        notification_module.notification_dao = mock_dao

        from services.notification_service import NotificationService
        from utils.exceptions import ServiceException

        with pytest.raises(ServiceException) as exc_info:
            NotificationService.delete_notification(
                notification_id=1,
                user_id='S2024002'
            )

        assert exc_info.value.code == 8003

    def test_mark_all_as_read(self):
        from models.notification import Notification

        mock_notifications = [
            Notification(
                id=i,
                receiver_id='S2024001',
                sender_id='SYSTEM',
                title=f'通知{i}',
                content=f'内容{i}',
                type='REMINDER',
                is_read=0,
                related_id=None,
                created_at=datetime.now()
            )
            for i in range(3)
        ]

        mock_dao = MagicMock()
        mock_dao.get_list.return_value = mock_notifications
        mock_dao.mark_as_read.return_value = True

        notification_module = import_service_module_directly('notification_service')
        notification_module.notification_dao = mock_dao

        from services.notification_service import NotificationService

        result = NotificationService.mark_all_as_read(user_id='S2024001')

        assert result == 3
        assert mock_dao.mark_as_read.call_count == 3
