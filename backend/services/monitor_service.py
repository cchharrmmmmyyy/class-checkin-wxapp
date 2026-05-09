from dao.user_dao import UserDAO
from dao.punch_dao import PunchDAO
from dao.leave_dao import LeaveDAO
from utils.exceptions import ServiceException
import datetime

# 创建DAO实例
user_dao = UserDAO()
punch_dao = PunchDAO()
leave_dao = LeaveDAO()


class MonitorService:

    @staticmethod
    def get_class_attendance(class_name, date=None):
        """获取班级考勤情况"""
        # 获取班级所有学生
        students = user_dao.get_list(where="class_name = ? AND deleted_at IS NULL", params=(class_name,))
        
        attendance_data = []
        
        for student in students:
            student_attendance = {
                'user_id': student.user_id,
                'username': student.username,
                'status': 'absent'  # 默认缺席
            }
            
            # 检查是否有打卡记录
            if date:
                punch = punch_dao.get_punch_by_user_and_date(student.user_id, date)
                if punch:
                    student_attendance['status'] = 'present'
            else:
                # 获取最近的打卡记录
                recent_punches = punch_dao.get_punches_by_user(student.user_id, limit=1)
                if recent_punches:
                    student_attendance['status'] = 'present'
            
            # 检查是否有请假记录
            if date:
                leaves = leave_dao.get_list(
                    where="user_id = ? AND leave_start_date <= ? AND leave_end_date >= ? AND leave_status = 'approved' AND deleted_at IS NULL",
                    params=(student.user_id, date, date)
                )
                if leaves:
                    student_attendance['status'] = 'leave'
            
            attendance_data.append(student_attendance)
        
        return attendance_data
    
    @staticmethod
    def get_class_leave_applications(class_name):
        """获取班级请假申请"""
        # 获取班级所有学生的请假申请
        students = user_dao.get_list(where="class_name = ? AND deleted_at IS NULL", params=(class_name,))
        student_ids = [student.user_id for student in students]
        
        if not student_ids:
            return []
        
        # 构建IN查询
        placeholders = ','.join(['?'] * len(student_ids))
        leaves = leave_dao.get_list(
            where=f"user_id IN ({placeholders}) AND leave_status = 'pending' AND deleted_at IS NULL",
            params=tuple(student_ids)
        )
        
        # 格式化返回数据
        leave_applications = []
        for leave in leaves:
            user = user_dao.get_by_id(leave.user_id)
            leave_applications.append({
                'id': leave.id,
                'user_id': leave.user_id,
                'username': user.username if user else '',
                'leave_start_date': leave.leave_start_date,
                'leave_end_date': leave.leave_end_date,
                'leave_type': leave.leave_type,
                'leave_reason': leave.leave_reason,
                'leave_status': leave.leave_status,
                'created_at': leave.created_at
            })
        
        return leave_applications
    
    @staticmethod
    def get_class_punch_records(class_name, start_date=None, end_date=None):
        """获取班级打卡记录"""
        # 获取班级所有学生
        students = user_dao.get_list(where="class_name = ? AND deleted_at IS NULL", params=(class_name,))
        student_ids = [student.user_id for student in students]
        
        if not student_ids:
            return []
        
        # 构建查询条件
        conditions = ["user_id IN (" + ','.join(['?'] * len(student_ids)) + ")"]
        params = list(student_ids)
        
        if start_date:
            conditions.append("punch_date >= ?")
            params.append(start_date)
        
        if end_date:
            conditions.append("punch_date <= ?")
            params.append(end_date)
        
        # 查询打卡记录
        where_clause = " AND ".join(conditions)
        punches = punch_dao.get_list(where=where_clause, params=tuple(params), order_by="punch_date DESC")
        
        # 格式化返回数据
        punch_records = []
        for punch in punches:
            user = user_dao.get_by_id(punch.user_id)
            punch_records.append({
                'id': punch.id,
                'user_id': punch.user_id,
                'username': user.username if user else '',
                'punch_date': punch.punch_date,
                'punch_time': punch.punch_time,
                'is_makeup': punch.is_makeup,
                'created_at': punch.created_at
            })
        
        return punch_records
    
    @staticmethod
    def get_attendance_summary(class_name, start_date, end_date):
        """获取考勤汇总"""
        # 获取班级所有学生
        students = user_dao.get_list(where="class_name = ? AND deleted_at IS NULL", params=(class_name,))
        
        summary = {
            'class_name': class_name,
            'start_date': start_date,
            'end_date': end_date,
            'total_students': len(students),
            'attendance_rate': 0.0,
            'details': []
        }
        
        total_punches = 0
        total_possible_days = 0
        
        for student in students:
            # 计算学生的打卡次数
            punches = punch_dao.get_list(
                where="user_id = ? AND punch_date >= ? AND punch_date <= ?",
                params=(student.user_id, start_date, end_date)
            )
            
            # 计算学生的请假天数
            leaves = leave_dao.get_list(
                where="user_id = ? AND leave_start_date <= ? AND leave_end_date >= ? AND leave_status = 'approved'",
                params=(student.user_id, end_date, start_date)
            )
            
            # 计算学生的出勤天数
            attendance_days = len(punches)
            leave_days = len(leaves)
            
            # 计算总天数
            start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            total_days = (end - start).days + 1
            
            # 计算出勤率
            if total_days > 0:
                student_attendance_rate = (attendance_days + leave_days) / total_days
            else:
                student_attendance_rate = 0.0
            
            summary['details'].append({
                'user_id': student.user_id,
                'username': student.username,
                'attendance_days': attendance_days,
                'leave_days': leave_days,
                'absent_days': total_days - (attendance_days + leave_days),
                'attendance_rate': student_attendance_rate
            })
            
            total_punches += attendance_days
            total_possible_days += total_days
        
        # 计算班级整体出勤率
        if total_possible_days > 0:
            summary['attendance_rate'] = total_punches / total_possible_days
        
        return summary
