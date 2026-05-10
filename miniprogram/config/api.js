// API 接口地址统一配置
// 改接口只需修改此处，无需动业务代码
//
// 上线前注意：
//   1. 将 env 改为 'production'
//   2. 将 production.baseUrl 替换为实际 API 域名

const env = 'development'; // development: 开发环境, production: 生产环境

const API_CONFIG = {
  development: {
    baseUrl: 'http://127.0.0.1:5000/api',
    timeout: 10000
  },
  production: {
    baseUrl: 'https://your-domain.com/api',  // TODO: 上线前替换为实际域名
    timeout: 15000
  }
};

const API_ENDPOINTS = {
  // 认证相关
  LOGIN: '/login',
  CHANGE_PASSWORD: '/change-password',

  // 学生相关
  STUDENT_PUNCH: '/student/punch',
  STUDENT_PUNCH_RECORDS: '/student/punch-records',
  STUDENT_LEAVE_APPLY: '/student/leave/apply',
  STUDENT_LEAVE_RECORDS: '/student/leave/records',
  STUDENT_MAKEUP_APPLY: '/student/makeup/apply',
  STUDENT_MAKEUP_RECORDS: '/student/makeup/records',

  // 班委相关
  MONITOR_CLASS_PUNCH_STATUS: '/student/monitor/class-punch-status',
  MONITOR_CLASS_LEAVES: '/student/monitor/class-leaves',
  MONITOR_CLASS_MAKEUPS: '/student/monitor/class-makeups',

  // 教师相关
  TEACHER_CLASSES: '/teacher/classes',
  TEACHER_CLASS_STUDENTS: '/teacher/class/students',
  TEACHER_CLASS_PUNCH_SUMMARY: '/teacher/class/punch-summary',
  TEACHER_LEAVE_PENDING: '/teacher/leave/pending',
  TEACHER_LEAVE_APPROVE: '/teacher/leave/approve',
  TEACHER_MAKEUP_PENDING: '/teacher/makeup/pending',
  TEACHER_MAKEUP_APPROVE: '/teacher/makeup/approve',
  TEACHER_MONITORS: '/teacher/monitors',
  TEACHER_MONITOR_APPOINT: '/teacher/monitor/appoint',
  TEACHER_MONITOR_REMOVE: '/teacher/monitor/remove',

  // 通知相关
  NOTIFICATIONS: '/notifications',
  NOTIFICATIONS_MARK_READ: '/notifications/mark-read',
  NOTIFICATIONS_UNREAD_COUNT: '/notifications/unread-count',

  // 管理员相关
  ADMIN_PUNCH_LOCATION: '/admin/punch-location'
};

const CURRENT_CONFIG = API_CONFIG[env];

module.exports = {
  baseUrl: CURRENT_CONFIG.baseUrl,
  timeout: CURRENT_CONFIG.timeout,
  API_ENDPOINTS,
  env
};
