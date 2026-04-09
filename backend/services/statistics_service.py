from dao.user_dao import UserDAO
from dao.punch_dao import PunchDAO
from dao.leave_dao import LeaveDAO
from utils.exceptions import ServiceException
import datetime

user_dao = UserDAO()
punch_dao = PunchDAO()
leave_dao = LeaveDAO()


class StatisticsService:

    @staticmethod
    def get_class_statistics(class_name, start_date, end_date):
        """获取班级统计数据"""
        students = user_dao.get_list(where="class_name = ? AND deleted_at IS NULL", params=(class_name,))
        
        if not students:
            raise ServiceException(f"班级 {class_name} 没有学生")
        
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        total_days = (end - start).days + 1
        
        statistics = {
            'class_name': class_name,
            'start_date': start_date,
            'end_date': end_date,
            'total_students': len(students),
            'total_days': total_days,
            'total_punches': 0,
            'total_leaves': 0,
            'total_absents': 0,
            'attendance_rate': 0.0,
            'students': []
        }
        
        student_ids = [student.user_id for student in students]
        
        for student in students:
            student_stat = {
                'user_id': student.user_id,
                'username': student.username,
                'real_name': student.real_name,
                'punches': 0,
                'leaves': 0,
                'absents': 0,
                'attendance_rate': 0.0
            }
            
            punches = punch_dao.get_list(
                where="user_id = ? AND punch_date >= ? AND punch_date <= ?",
                params=(student.user_id, start_date, end_date)
            )
            student_stat['punches'] = len(punches)
            
            leaves = leave_dao.get_list(
                where="user_id = ? AND leave_start_date <= ? AND leave_end_date >= ? AND leave_status = 'approved' AND deleted_at IS NULL",
                params=(student.user_id, end_date, start_date)
            )
            student_stat['leaves'] = len(leaves)
            
            student_stat['absents'] = total_days - student_stat['punches'] - student_stat['leaves']
            
            if total_days > 0:
                student_stat['attendance_rate'] = (student_stat['punches'] + student_stat['leaves']) / total_days
            
            statistics['students'].append(student_stat)
            statistics['total_punches'] += student_stat['punches']
            statistics['total_leaves'] += student_stat['leaves']
            statistics['total_absents'] += student_stat['absents']
        
        total_attendance_days = statistics['total_punches'] + statistics['total_leaves']
        total_possible_days = len(students) * total_days
        
        if total_possible_days > 0:
            statistics['attendance_rate'] = total_attendance_days / total_possible_days
        
        return statistics

    @staticmethod
    def get_student_statistics(user_id, start_date, end_date):
        """获取学生个人统计数据"""
        user = user_dao.get_by_id(user_id)
        
        if not user:
            raise ServiceException(f"用户 {user_id} 不存在")
        
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        total_days = (end - start).days + 1
        
        punches = punch_dao.get_list(
            where="user_id = ? AND punch_date >= ? AND punch_date <= ?",
            params=(user_id, start_date, end_date)
        )
        
        leaves = leave_dao.get_list(
            where="user_id = ? AND leave_start_date <= ? AND leave_end_date >= ? AND leave_status = 'approved' AND deleted_at IS NULL",
            params=(user_id, end_date, start_date)
        )
        
        statistics = {
            'user_id': user.user_id,
            'username': user.username,
            'real_name': user.real_name,
            'class_name': user.class_name,
            'start_date': start_date,
            'end_date': end_date,
            'total_days': total_days,
            'punches': len(punches),
            'leaves': len(leaves),
            'absents': total_days - len(punches) - len(leaves),
            'attendance_rate': 0.0,
            'punch_records': [],
            'leave_records': []
        }
        
        if total_days > 0:
            statistics['attendance_rate'] = (len(punches) + len(leaves)) / total_days
        
        for punch in punches:
            statistics['punch_records'].append({
                'id': punch.id,
                'punch_date': punch.punch_date,
                'punch_time': punch.punch_time,
                'latitude': punch.latitude,
                'longitude': punch.longitude,
                'is_makeup': punch.is_makeup
            })
        
        for leave in leaves:
            statistics['leave_records'].append({
                'id': leave.id,
                'leave_start_date': leave.leave_start_date,
                'leave_end_date': leave.leave_end_date,
                'leave_type': leave.leave_type,
                'leave_reason': leave.leave_reason
            })
        
        return statistics

    @staticmethod
    def get_attendance_alerts(class_name, threshold=0.8):
        """获取考勤预警名单（出勤率低于阈值的学生）"""
        today = datetime.date.today()
        start_of_month = today.replace(day=1).strftime('%Y-%m-%d')
        end_of_month = today.strftime('%Y-%m-%d')
        
        statistics = StatisticsService.get_class_statistics(class_name, start_of_month, end_of_month)
        
        alerts = []
        for student in statistics['students']:
            if student['attendance_rate'] < threshold:
                alerts.append({
                    'user_id': student['user_id'],
                    'username': student['username'],
                    'real_name': student['real_name'],
                    'attendance_rate': student['attendance_rate'],
                    'punches': student['punches'],
                    'leaves': student['leaves'],
                    'absents': student['absents'],
                    'threshold': threshold
                })
        
        return sorted(alerts, key=lambda x: x['attendance_rate'])

    @staticmethod
    def get_attendance_trend(class_name, days=30):
        """获取班级考勤趋势（最近N天）"""
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days - 1)
        
        trend = {
            'class_name': class_name,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'days': days,
            'daily_data': []
        }
        
        students = user_dao.get_list(where="class_name = ? AND deleted_at IS NULL", params=(class_name,))
        student_count = len(students)
        
        if student_count == 0:
            return trend
        
        for i in range(days):
            current_date = start_date + datetime.timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            
            punches = punch_dao.get_list(
                where="punch_date = ?",
                params=(date_str,)
            )
            
            leaves = leave_dao.get_list(
                where="leave_start_date <= ? AND leave_end_date >= ? AND leave_status = 'approved' AND deleted_at IS NULL",
                params=(date_str, date_str)
            )
            
            daily_punch_users = set(p.user_id for p in punches)
            daily_leave_users = set(l.user_id for l in leaves)
            
            present_count = len(daily_punch_users)
            leave_count = len(daily_leave_users)
            absent_count = student_count - present_count - leave_count
            
            if student_count > 0:
                attendance_rate = (present_count + leave_count) / student_count
            else:
                attendance_rate = 0.0
            
            trend['daily_data'].append({
                'date': date_str,
                'present_count': present_count,
                'leave_count': leave_count,
                'absent_count': absent_count,
                'attendance_rate': attendance_rate
            })
        
        return trend

    @staticmethod
    def get_daily_statistics(class_name, date=None):
        """获取班级当日考勤统计"""
        if date is None:
            date = datetime.date.today().strftime('%Y-%m-%d')
        
        students = user_dao.get_list(where="class_name = ? AND deleted_at IS NULL", params=(class_name,))
        student_count = len(students)
        
        if student_count == 0:
            raise ServiceException(f"班级 {class_name} 没有学生")
        
        statistics = {
            'class_name': class_name,
            'date': date,
            'total_students': student_count,
            'present': 0,
            'leave': 0,
            'absent': 0,
            'attendance_rate': 0.0,
            'details': []
        }
        
        for student in students:
            detail = {
                'user_id': student.user_id,
                'username': student.username,
                'real_name': student.real_name,
                'status': 'absent'
            }
            
            punch = punch_dao.get_punch_by_user_and_date(student.user_id, date)
            if punch:
                detail['status'] = 'present'
                detail['punch_time'] = punch.punch_time
            
            leaves = leave_dao.get_list(
                where="user_id = ? AND leave_start_date <= ? AND leave_end_date >= ? AND leave_status = 'approved' AND deleted_at IS NULL",
                params=(student.user_id, date, date)
            )
            if leaves:
                detail['status'] = 'leave'
                detail['leave_reason'] = leaves[0].leave_reason
            
            statistics['details'].append(detail)
            
            if detail['status'] == 'present':
                statistics['present'] += 1
            elif detail['status'] == 'leave':
                statistics['leave'] += 1
            else:
                statistics['absent'] += 1
        
        if student_count > 0:
            statistics['attendance_rate'] = (statistics['present'] + statistics['leave']) / student_count
        
        return statistics
