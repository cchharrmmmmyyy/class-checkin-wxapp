from .admin import admin_bp
from .students import student_function
from .teachers import teacher_function
from .login import login_function

__all__ = ['admin_bp', 'student_function', 'teacher_function', 'login_function']