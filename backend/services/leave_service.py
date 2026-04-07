from datetime import datetime
from dao import leave_dao


class LeaveService:

    @staticmethod
    def apply_leave(user_id, leave_start_date, leave_end_date):
        today = datetime.now().strftime('%Y-%m-%d')

        if leave_start_date < today:
            return {
                'success': False,
                'message': '请假开始日期不能是过去日期'
            }

        if leave_end_date < leave_start_date:
            return {
                'success': False,
                'message': '请假结束日期不能早于开始日期'
            }

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
            return {
                'success': False,
                'message': '审批状态只能是approved或rejected'
            }

        leave_application = leave_dao.get_leave_record_by_id_and_class(leave_id, class_name)

        if not leave_application:
            return {
                'success': False,
                'message': '未找到该请假申请或该申请不属于您的班级'
            }

        if leave_application['leave_status'] != 'pending':
            return {
                'success': False,
                'message': f'该请假申请已处于{leave_application["leave_status"]}状态，无法重复审批'
            }

        leave_dao.update_leave_status(leave_id, status)

        return {
            'success': True,
            'message': '请假审批成功',
            'data': {'leave_id': leave_id, 'status': status}
        }
