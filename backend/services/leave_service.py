from datetime import datetime
from dao import LeaveDAO
from utils.exceptions import ServiceException

# 创建DAO实例
leave_dao = LeaveDAO()


class LeaveService:

    @staticmethod
    def apply_leave(user_id, leave_start_date, leave_end_date):
        if not leave_start_date or not leave_end_date:
            raise ServiceException('请假开始和结束日期不能为空', code=3001)

        if leave_start_date in ('null', 'undefined') or leave_end_date in ('null', 'undefined'):
            raise ServiceException('请假开始和结束日期不能为空', code=3001)

        today = datetime.now().strftime('%Y-%m-%d')

        if leave_end_date < leave_start_date:
            raise ServiceException('请假结束日期不能早于开始日期', code=3003)

        if leave_start_date < today:
            raise ServiceException('请假开始日期不能是过去日期', code=3002)

        # 检查是否与现有请假记录重叠
        existing_leaves = leave_dao.get_leave_records_by_user(user_id)
        for leave in existing_leaves:
            if (leave['leave_status'] in ['pending', 'approved'] and
                not (leave['leave_end_date'] < leave_start_date or leave['leave_start_date'] > leave_end_date)):
                raise ServiceException('该时间段内已存在请假记录', code=3004)

        leave_dao.create_leave_record(user_id, leave_start_date, leave_end_date)

        return {
            'success': True,
            'message': '请假申请提交成功，等待老师批准',
            'data': {
                'leave_start_date': leave_start_date,
                'leave_end_date': leave_end_date
            }
        }

    @staticmethod
    def get_user_leave_records(user_id):
        records = leave_dao.get_leave_records_by_user(user_id)
        return [
            {
                'id': r['id'],
                'user_id': r['user_id'],
                'username': r['username'],
                'leave_start_date': r['leave_start_date'],
                'leave_end_date': r['leave_end_date'],
                'leave_status': r['leave_status']
            }
            for r in records
        ]

    @staticmethod
    def get_pending_applications(class_name):
        applications = leave_dao.get_pending_leave_applications_by_class(class_name)
        return [
            {
                'id': app['id'],
                'username': app['username'],
                'user_id': app['user_id'],
                'leave_start_date': app['leave_start_date'],
                'leave_end_date': app['leave_end_date'],
                'leave_status': app['leave_status']
            }
            for app in applications
        ]

    @staticmethod
    def approve_leave(leave_id, class_name, status):
        if status not in ('approved', 'rejected'):
            raise ServiceException('审批状态只能是approved或rejected', code=3004)

        leave_application = leave_dao.get_leave_record_by_id_and_class(leave_id, class_name)

        if not leave_application:
            raise ServiceException(
                '未找到该请假申请或该申请不属于您的班级',
                code=3005,
                http_status=404
            )

        if leave_application['leave_status'] != 'pending':
            raise ServiceException(
                f'该请假申请已处于{leave_application["leave_status"]}状态，无法重复审批',
                code=3006
            )

        leave_dao.update_leave_status(leave_id, status)

        return {
            'success': True,
            'message': '请假审批成功',
            'data': {'leave_id': leave_id, 'status': status}
        }
