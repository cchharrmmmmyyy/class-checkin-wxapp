"""
路由模块
注册所有蓝图
"""
from .auth import auth_bp
from .student import student_bp
from .teacher import teacher_bp
from .admin import (
    admin_user_bp, admin_org_bp, admin_teaching_bp,
    admin_rule_bp, admin_attendance_bp, admin_dashboard_bp
)
from .common import common_bp

__all__ = [
    'auth_bp', 'student_bp', 'teacher_bp',
    'admin_user_bp', 'admin_org_bp', 'admin_teaching_bp',
    'admin_rule_bp', 'admin_attendance_bp', 'admin_dashboard_bp',
    'common_bp'
]
