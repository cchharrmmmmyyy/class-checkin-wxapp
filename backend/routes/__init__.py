"""
路由模块
注册所有蓝图
"""
from .auth import auth_bp
from .student import student_bp
from .teacher import teacher_bp
from .admin import admin_bp
from .common import common_bp

__all__ = ['auth_bp', 'student_bp', 'teacher_bp', 'admin_bp', 'common_bp']
