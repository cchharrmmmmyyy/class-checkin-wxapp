from typing import List, Optional
from dao import NotificationDAO
from utils.exceptions import ServiceException
from utils.pagination import paginate, normalize_pagination
from utils import error_codes as EC


notification_dao = NotificationDAO()


class NotificationService:

    @staticmethod
    def send_notification(receiver_id: str, title: str, content: str,
                        notification_type: str, sender_id: str = None,
                        related_id: str = None, conn=None) -> int:
        valid_types = ['SYSTEM', 'PUNCH', 'LEAVE', 'MAKEUP', 'APPROVAL', 'REMINDER', 'ANNOUNCEMENT']
        if notification_type not in valid_types:
            raise ServiceException(
                f'无效的通知类型: {notification_type}',
                code=EC.NOTIFICATION_INVALID_TYPE,
                http_status=400
            )

        data = {
            'receiver_id': receiver_id,
            'sender_id': sender_id,
            'title': title,
            'content': content,
            'type': notification_type,
            'related_id': related_id
        }

        return notification_dao.create(data, conn=conn)

    @staticmethod
    def send_batch_notifications(receiver_ids: List[str], title: str, content: str,
                                notification_type: str, sender_id: str = None,
                                related_id: str = None, conn=None) -> List[int]:
        notification_ids = []
        for receiver_id in receiver_ids:
            notification_id = NotificationService.send_notification(
                receiver_id=receiver_id,
                title=title,
                content=content,
                notification_type=notification_type,
                sender_id=sender_id,
                related_id=related_id,
                conn=conn
            )
            notification_ids.append(notification_id)
        return notification_ids

    @staticmethod
    def get_user_notifications(user_id: str, notification_type: str = None,
                               is_read: bool = None, page: int = 1,
                               size: int = 50) -> dict:
        conditions = ['receiver_id = ?']
        params = [user_id]

        if notification_type:
            conditions.append('type = ?')
            params.append(notification_type)
        if is_read is not None:
            conditions.append('is_read = ?')
            params.append(1 if is_read else 0)

        where = ' AND '.join(conditions)
        order_by = 'created_at DESC'

        total = notification_dao.count(where=where, params=tuple(params))
        page, size, offset = normalize_pagination(page, size)
        notifications = notification_dao.get_list(
            where=where,
            params=tuple(params),
            order_by=order_by,
            limit=size,
            offset=offset
        )

        items = [
            {
                'id': n.id,
                'receiver_id': n.receiver_id,
                'sender_id': n.sender_id,
                'title': n.title,
                'content': n.content,
                'type': n.type,
                'is_read': bool(n.is_read),
                'related_id': n.related_id,
                'created_at': n.created_at.isoformat() if n.created_at else None
            }
            for n in notifications
        ]
        
        return paginate(items, total, page, size)

    @staticmethod
    def get_unread_count(user_id: str, notification_type: str = None) -> int:
        notifications = NotificationService.get_user_notifications(
            user_id=user_id,
            notification_type=notification_type,
            is_read=False,
            size=1000
        )
        return len(notifications)

    @staticmethod
    def mark_as_read(notification_id: int, user_id: str) -> bool:
        notification = notification_dao.get_by_id(notification_id)
        if not notification:
            raise ServiceException('通知不存在', code=EC.NOTIFICATION_NOT_FOUND, http_status=404)

        if notification.receiver_id != user_id:
            raise ServiceException('无权限操作', code=EC.NOTIFICATION_NO_PERMISSION, http_status=403)

        return notification_dao.mark_as_read(notification_id)

    @staticmethod
    def mark_all_as_read(user_id: str) -> int:
        notifications = NotificationService.get_user_notifications(
            user_id=user_id,
            is_read=False,
            size=1000
        )

        count = 0
        for n in notifications:
            if notification_dao.mark_as_read(n['id']):
                count += 1
        return count

    @staticmethod
    def delete_notification(notification_id: int, user_id: str) -> bool:
        notification = notification_dao.get_by_id(notification_id)
        if not notification:
            raise ServiceException('通知不存在', code=EC.NOTIFICATION_NOT_FOUND, http_status=404)

        if notification.receiver_id != user_id:
            raise ServiceException('无权限操作', code=EC.NOTIFICATION_NO_PERMISSION, http_status=403)

        return notification_dao.delete(notification_id)