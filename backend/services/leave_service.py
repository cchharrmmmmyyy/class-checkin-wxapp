from datetime import datetime
from dao import LeaveDAO
from utils.exceptions import ServiceException
from utils.pagination import paginate
from utils import error_codes as EC

leave_dao = LeaveDAO()


class LeaveService:

    @staticmethod
    def apply_leave(user_id, leave_start_date, leave_end_date, leave_type='personal', leave_reason=None):
        if not leave_start_date or not leave_end_date:
            raise ServiceException('请假开始和结束日期不能为空', code=EC.LEAVE_DATE_EMPTY)

        if leave_start_date in ('null', 'undefined') or leave_end_date in ('null', 'undefined'):
            raise ServiceException('请假开始和结束日期不能为空', code=EC.LEAVE_DATE_EMPTY)

        today = datetime.now().strftime('%Y-%m-%d')

        if leave_end_date < leave_start_date:
            raise ServiceException('请假结束日期不能早于开始日期', code=EC.LEAVE_END_BEFORE_START)

        if leave_start_date < today:
            raise ServiceException('请假开始日期不能是过去日期', code=EC.LEAVE_START_IN_PAST)

        existing_leaves = leave_dao.get_leave_records_by_user(user_id)
        for leave in existing_leaves:
            if (leave.leave_status in ['pending', 'approved'] and
                not (leave.leave_end_date < leave_start_date or leave.leave_start_date > leave_end_date)):
                raise ServiceException('该时间段内已存在请假记录', code=EC.LEAVE_OVERLAP)

        leave_dao.create({
            'user_id': user_id,
            'leave_start_date': leave_start_date,
            'leave_end_date': leave_end_date,
            'leave_type': leave_type,
            'leave_reason': leave_reason,
            'leave_status': 'pending'
        })

        return {
            'success': True,
            'message': '请假申请提交成功，等待老师批准',
            'data': {
                'leave_start_date': leave_start_date,
                'leave_end_date': leave_end_date
            }
        }

    @staticmethod
    def get_user_leave_records(user_id, status=None, page=1, size=50):
        where = "user_id = ? AND deleted_at IS NULL"
        params = [user_id]

        if status:
            where += " AND leave_status = ?"
            params.append(status)

        total = leave_dao.count(where=where, params=tuple(params))
        offset = (page - 1) * size

        records = leave_dao.get_list(
            where=where,
            params=tuple(params),
            order_by="created_at DESC",
            limit=size,
            offset=offset
        )

        items = [
            {
                'id': r.id,
                'user_id': r.user_id,
                'leave_start_date': r.leave_start_date,
                'leave_end_date': r.leave_end_date,
                'leave_type': r.leave_type,
                'leave_reason': r.leave_reason,
                'leave_status': r.leave_status,
                'created_at': r.created_at
            }
            for r in records
        ]

        return paginate(items, total, page, size)

    @staticmethod
    def get_pending_leave_applications(class_name, page=1, size=50):
        where = "class_name = ? AND leave_status = 'pending' AND deleted_at IS NULL"
        params = (class_name,)

        total = leave_dao.count(where=where, params=params)
        offset = (page - 1) * size

        conn = leave_dao._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, user_id, leave_start_date, leave_end_date, leave_type, leave_reason,
                       leave_status, approved_by, approved_at, created_at, username
                FROM v_leave_user_read
                WHERE class_name = ? AND leave_status = 'pending' AND deleted_at IS NULL
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
                'leave_start_date': app['leave_start_date'],
                'leave_end_date': app['leave_end_date'],
                'leave_type': app['leave_type'],
                'leave_reason': app['leave_reason'],
                'leave_status': app['leave_status'],
                'created_at': app['created_at']
            }
            for app in applications
        ]

        return paginate(items, total, page, size)

    @staticmethod
    def approve_leave(leave_id, class_name, status):
        if status not in ('approved', 'rejected'):
            raise ServiceException('审批状态只能是approved或rejected', code=EC.LEAVE_STATUS_INVALID)

        leave = leave_dao.get_leave_record_by_id_and_class(leave_id, class_name)

        if not leave:
            raise ServiceException(
                '未找到该请假申请或该申请不属于您的班级',
                code=EC.LEAVE_NOT_IN_CLASS,
                http_status=404
            )

        if leave.leave_status != 'pending':
            raise ServiceException(
                f'该请假申请已处于{leave.leave_status}状态，无法重复审批',
                code=EC.LEAVE_STATUS_INVALID
            )

        leave_dao.update_leave_status(leave_id, status)

        return {
            'success': True,
            'message': '请假审批成功',
            'data': {'leave_id': leave_id, 'status': status}
        }
