from datetime import datetime, timedelta
from dao import MakeupRequestDAO, PunchDAO
from utils.exceptions import ServiceException
from utils.pagination import paginate, normalize_pagination
from utils import error_codes as EC

makeup_request_dao = MakeupRequestDAO()
punch_dao = PunchDAO()


class MakeupService:

    @staticmethod
    def apply_makeup(user_id, punch_date, reason):
        if not punch_date:
            raise ServiceException('补卡日期不能为空', code=EC.MAKEUP_DATE_MISSING)

        if not reason:
            raise ServiceException('补卡原因不能为空', code=EC.MAKEUP_REASON_MISSING)

        today = datetime.now().strftime('%Y-%m-%d')

        if punch_date > today:
            raise ServiceException('补卡日期不能是未来日期', code=EC.MAKEUP_FUTURE_DATE)

        three_days_ago = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        if punch_date < three_days_ago:
            raise ServiceException('只能补近3天的卡', code=EC.MAKEUP_TOO_OLD)

        existing_punch = punch_dao.get_punch_by_user_and_date(user_id, punch_date)
        if existing_punch:
            raise ServiceException('当日已有打卡记录，不能补卡', code=EC.MAKEUP_ALREADY_PUNCHED)

        existing = makeup_request_dao.get_by_user_and_date(user_id, punch_date)
        if existing:
            raise ServiceException('该日期已经申请过补卡', code=EC.MAKEUP_ALREADY_APPLIED)

        makeup_request_dao.create({
            'user_id': user_id,
            'target_date': punch_date,
            'reason': reason,
        })

        return {
            'success': True,
            'message': '补卡申请提交成功，等待老师批准',
            'data': {
                'punch_date': punch_date,
            }
        }

    @staticmethod
    def get_user_makeup_records(user_id, page=1, size=50):
        where = "user_id = ? AND deleted_at IS NULL"
        params = (user_id,)

        total = makeup_request_dao.count(where=where, params=params)
        page, size, offset = normalize_pagination(page, size)

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

        return paginate(items, total, page, size)

    @staticmethod
    def get_pending_makeup_applications(class_name, page=1, size=50):
        where = "class_name = ? AND status = 'pending' AND deleted_at IS NULL"
        params = (class_name,)

        total = makeup_request_dao.count(where=where, params=params)
        page, size, offset = normalize_pagination(page, size)

        conn = makeup_request_dao._get_connection()
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

        return paginate(items, total, page, size)

    @staticmethod
    def approve_makeup(request_id, class_name, status, punch_time, latitude, longitude):
        if status not in ('approved', 'rejected'):
            raise ServiceException('审批状态只能是approved或rejected', code=EC.MAKEUP_STATUS_INVALID)

        makeup_application = makeup_request_dao.get_by_id_and_class(request_id, class_name)

        if not makeup_application:
            raise ServiceException(
                '未找到该补卡申请或该申请不属于您的班级',
                code=EC.MAKEUP_NOT_IN_CLASS,
                http_status=404
            )

        if makeup_application.status != 'pending':
            raise ServiceException(
                f'该补卡申请已处于{makeup_application.status}状态，无法重复审批',
                code=EC.MAKEUP_STATUS_INVALID
            )

        makeup_request_dao.update_status(request_id, status)

        if status == 'approved':
            if not punch_time:
                raise ServiceException('打卡时间不能为空', code=EC.MAKEUP_DATE_MISSING)
            if latitude is None:
                raise ServiceException('打卡纬度不能为空', code=EC.PUNCH_LOCATION_FAILED)
            if longitude is None:
                raise ServiceException('打卡经度不能为空', code=EC.PUNCH_LOCATION_FAILED)
            punch_dao.create({
                'user_id': makeup_application.user_id,
                'punch_date': makeup_application.target_date,
                'punch_time': punch_time,
                'latitude': latitude,
                'longitude': longitude,
                'is_makeup': 1,
            })

        return {
            'success': True,
            'message': '补卡审批成功',
            'data': {'request_id': request_id, 'status': status}
        }
