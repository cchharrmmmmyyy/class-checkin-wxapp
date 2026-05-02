from datetime import datetime, timedelta
from dao import MakeupRequestDAO, PunchDAO
from utils.exceptions import ServiceException

# 创建DAO实例
makeup_request_dao = MakeupRequestDAO()
punch_dao = PunchDAO()


class MakeupService:

    @staticmethod
    def apply_makeup(user_id, punch_date, reason):
        """申请补卡"""
        if not punch_date:
            raise ServiceException('补卡日期不能为空', code=4001)

        if not reason:
            raise ServiceException('补卡原因不能为空', code=4002)

        today = datetime.now().strftime('%Y-%m-%d')

        if punch_date > today:
            raise ServiceException('补卡日期不能是未来日期', code=4003)

        # 检查是否在补卡时限内（3天）
        three_days_ago = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        if punch_date < three_days_ago:
            raise ServiceException('只能补近3天的卡', code=4008)

        # 检查当日是否已有打卡记录
        existing_punch = punch_dao.get_punch_by_user_and_date(user_id, punch_date)
        if existing_punch:
            raise ServiceException('当日已有打卡记录，不能补卡', code=4009)

        # 检查是否已经申请过补卡
        existing = makeup_request_dao.get_by_user_and_date(user_id, punch_date)
        if existing:
            raise ServiceException('该日期已经申请过补卡', code=4004)

        # 创建补卡申请
        request_id = makeup_request_dao.create(user_id, punch_date, reason)

        return {
            'success': True,
            'message': '补卡申请提交成功，等待老师批准',
            'data': {
                'punch_date': punch_date,
                'request_id': request_id
            }
        }

    @staticmethod
    def get_user_makeup_records(user_id, page=1, size=50):
        """获取用户的补卡记录"""
        where = "user_id = ? AND deleted_at IS NULL"
        params = (user_id,)
        
        total = makeup_request_dao.count(where=where, params=params)
        offset = (page - 1) * size
        
        records = makeup_request_dao.get_list(
            where=where,
            params=params,
            order_by="created_at DESC",
            limit=size,
            offset=offset
        )
        
        items = [
            {
                'id': r.id,
                'user_id': r.user_id,
                'target_date': r.target_date,
                'reason': r.reason,
                'status': r.status,
                'created_at': r.created_at
            }
            for r in records
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
    def get_pending_makeup_applications(class_name, page=1, size=50):
        """获取班级待审批的补卡申请"""
        where = "class_name = ? AND status = 'pending' AND deleted_at IS NULL"
        params = (class_name,)
        
        total = makeup_request_dao.count(where=where, params=params)
        offset = (page - 1) * size
        
        # 使用 raw sql 查询以获取 username
        conn = makeup_request_dao.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, user_id, target_date, reason, status, created_at, username
                FROM v_makeup_user_read
                WHERE class_name = ? AND status = 'pending' AND deleted_at IS NULL
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (class_name, size, offset)
            )
            applications = cursor.fetchall()
        finally:
            conn.close()

        items = [
            {
                'id': app['id'],
                'username': app['username'],
                'user_id': app['user_id'],
                'target_date': app['target_date'],
                'reason': app['reason'],
                'status': app['status'],
                'created_at': app['created_at']
            }
            for app in applications
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
    def approve_makeup(request_id, class_name, status):
        """审批补卡申请"""
        if status not in ('approved', 'rejected'):
            raise ServiceException('审批状态只能是approved或rejected', code=4005)

        makeup_application = makeup_request_dao.get_by_id_and_class(request_id, class_name)

        if not makeup_application:
            raise ServiceException(
                '未找到该补卡申请或该申请不属于您的班级',
                code=4006,
                http_status=404
            )

        if makeup_application['status'] != 'pending':
            raise ServiceException(
                f'该补卡申请已处于{makeup_application["status"]}状态，无法重复审批',
                code=4007
            )

        # 更新补卡申请状态
        makeup_request_dao.update_status(request_id, status)

        # 如果批准补卡，创建打卡记录
        if status == 'approved':
            # 使用模块级别的punch_dao实例
            # 补卡记录使用0作为默认坐标，因为没有实际位置信息
            punch_dao.create_punch(
                makeup_application['user_id'],
                makeup_application['target_date'],
                '12:00:00',
                0,  # latitude
                0,  # longitude
                is_makeup=1
            )

        return {
            'success': True,
            'message': '补卡审批成功',
            'data': {'request_id': request_id, 'status': status}
        }
