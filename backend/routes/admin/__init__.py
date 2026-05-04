from .user import admin_user_bp
from .org import admin_org_bp
from .teaching import admin_teaching_bp
from .rule import admin_rule_bp
from .attendance import admin_attendance_bp
from .dashboard import admin_dashboard_bp

__all__ = [
    'admin_user_bp', 'admin_org_bp', 'admin_teaching_bp',
    'admin_rule_bp', 'admin_attendance_bp', 'admin_dashboard_bp'
]
