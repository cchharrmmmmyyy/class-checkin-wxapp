// API 接口地址统一配置
// 改接口只需修改此处，无需动业务代码

const env = 'development'; // development: 开发环境, production: 生产环境

const API_CONFIG = {
  development: {
    baseUrl: 'http://10.148.40.146:5000/api',
    timeout: 10000
  },
  production: {
    baseUrl: 'https://your-production-domain.com/api',
    timeout: 15000
  }
};

const API_ENDPOINTS = {
  // 认证相关
  LOGIN: '/login',
  
  // 学生相关
  STUDENT_PUNCH: '/student/punch',
  STUDENT_RECORDS: '/student/records',
  STUDENT_CLASS_RECORDS: '/student/class-records',
  STUDENT_APPLY_LEAVE: '/student/apply-leave',
  STUDENT_LEAVE_RECORDS: '/student/leave-records',
  
  // 教师相关
  TEACHER_CLASS_LIST: '/teacher/class-list',
  TEACHER_LEAVE_APPLICATIONS: '/teacher/leave-applications',
  TEACHER_APPROVE_LEAVE: '/teacher/approve-leave',
  TEACHER_CLASS_MONITOR: '/teacher/class-monitor',
  TEACHER_APPOINT_MONITOR: '/teacher/appoint-monitor',
  TEACHER_REMOVE_MONITOR: '/teacher/remove-monitor',
  
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
