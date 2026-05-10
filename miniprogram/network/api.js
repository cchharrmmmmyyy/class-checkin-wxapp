/**
 * API 服务层 —— 统一管理所有后端接口。
 * 业务层调用接口的唯一入口，改接口只需修改此处。
 */

const request = require('./request.js');
const { API_ENDPOINTS } = require('../config/api.js');

const api = {
  // ================================================================
  // 认证
  // ================================================================

  auth: {
    /**
     * @param {string} user_id
     * @param {string} password
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<{ token: string, user: object }>}
     */
    login(user_id, password, options = {}) {
      return request.post(API_ENDPOINTS.LOGIN, { user_id, password }, options);
    },

    /**
     * @param {string} old_password
     * @param {string} new_password
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<object>}
     */
    changePassword(old_password, new_password, options = {}) {
      return request.post(API_ENDPOINTS.CHANGE_PASSWORD, { old_password, new_password }, options);
    }
  },

  // ================================================================
  // 学生
  // ================================================================

  student: {
    /**
     * @param {{ user_id: string, username?: string, role?: string, class?: string }} userInfo
     * @param {{ latitude: number, longitude: number }|null} location
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<object>}
     */
    punch(userInfo, location, options = {}) {
      return request.post(API_ENDPOINTS.STUDENT_PUNCH, {
        user_id: userInfo.user_id,
        latitude: location ? location.latitude : null,
        longitude: location ? location.longitude : null
      }, options);
    },

    /**
     * @param {{ page?: number, size?: number }} [params]
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<{ items: object[], total?: number }>}
     */
    getPunchRecords(params = {}, options = {}) {
      return request.get(API_ENDPOINTS.STUDENT_PUNCH_RECORDS, params, options);
    },

    /**
     * @param {{ start_date: string, end_date: string, leave_type?: string, reason: string }} data
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<object>}
     */
    applyLeave(data, options = {}) {
      return request.post(API_ENDPOINTS.STUDENT_LEAVE_APPLY, data, options);
    },

    /**
     * @param {{ status?: string, page?: number, size?: number }} [params]
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<{ items: object[], total?: number }>}
     */
    getLeaveRecords(params = {}, options = {}) {
      return request.get(API_ENDPOINTS.STUDENT_LEAVE_RECORDS, params, options);
    },

    /**
     * @param {{ target_date: string, reason: string }} data
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<object>}
     */
    applyMakeup(data, options = {}) {
      return request.post(API_ENDPOINTS.STUDENT_MAKEUP_APPLY, data, options);
    },

    /**
     * @param {{ page?: number, size?: number }} [params]
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<{ items: object[], total?: number }>}
     */
    getMakeupRecords(params = {}, options = {}) {
      return request.get(API_ENDPOINTS.STUDENT_MAKEUP_RECORDS, params, options);
    }
  },

  // ================================================================
  // 班委
  // ================================================================

  monitor: {
    /**
     * @param {{ date?: string }} [params]
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<object>}
     */
    getClassPunchStatus(params = {}, options = {}) {
      return request.get(API_ENDPOINTS.MONITOR_CLASS_PUNCH_STATUS, params, options);
    },

    /**
     * @param {{ page?: number, size?: number }} [params]
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<object[]>}
     */
    getClassLeaves(params = {}, options = {}) {
      return request.get(API_ENDPOINTS.MONITOR_CLASS_LEAVES, params, options);
    },

    /**
     * @param {{ page?: number, size?: number }} [params]
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<object[]>}
     */
    getClassMakeups(params = {}, options = {}) {
      return request.get(API_ENDPOINTS.MONITOR_CLASS_MAKEUPS, params, options);
    }
  },

  // ================================================================
  // 教师
  // ================================================================

  teacher: {
    /**
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<string[]>}
     */
    getClasses(options = {}) {
      return request.get(API_ENDPOINTS.TEACHER_CLASSES, {}, options);
    },

    /**
     * @param {{ class_name: string, page?: number, size?: number }} params
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<{ items: object[], total?: number }>}
     */
    getClassStudents(params = {}, options = {}) {
      return request.get(API_ENDPOINTS.TEACHER_CLASS_STUDENTS, params, options);
    },

    /**
     * @param {{ class_name: string, date?: string }} params
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<object>}
     */
    getClassPunchSummary(params = {}, options = {}) {
      return request.get(API_ENDPOINTS.TEACHER_CLASS_PUNCH_SUMMARY, params, options);
    },

    /**
     * @param {{ class_name?: string, page?: number, size?: number }} [params]
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<{ items: object[], total?: number }>}
     */
    getLeavePending(params = {}, options = {}) {
      return request.get(API_ENDPOINTS.TEACHER_LEAVE_PENDING, params, options);
    },

    /**
     * @param {{ leave_id: number|string, status: string }} data
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<object>}
     */
    approveLeave(data, options = {}) {
      return request.post(API_ENDPOINTS.TEACHER_LEAVE_APPROVE, data, options);
    },

    /**
     * @param {{ class_name?: string, page?: number, size?: number }} [params]
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<{ items: object[], total?: number }>}
     */
    getMakeupPending(params = {}, options = {}) {
      return request.get(API_ENDPOINTS.TEACHER_MAKEUP_PENDING, params, options);
    },

    /**
     * @param {{ makeup_id: number|string, status: string, punch_time?: string, latitude?: number, longitude?: number }} data
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<object>}
     */
    approveMakeup(data, options = {}) {
      return request.post(API_ENDPOINTS.TEACHER_MAKEUP_APPROVE, data, options);
    },

    /**
     * @param {{ class_name?: string, page?: number, size?: number }} [params]
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<object[]>}
     */
    getMonitors(params = {}, options = {}) {
      return request.get(API_ENDPOINTS.TEACHER_MONITORS, params, options);
    },

    /**
     * @param {{ student_id: string, class_name?: string }} data
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<object>}
     */
    appointMonitor(data, options = {}) {
      return request.post(API_ENDPOINTS.TEACHER_MONITOR_APPOINT, data, options);
    },

    /**
     * @param {{ student_id: string, class_name?: string }} params
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<object>}
     */
    removeMonitor(params = {}, options = {}) {
      return request.delete(API_ENDPOINTS.TEACHER_MONITOR_REMOVE, params, options);
    }
  },

  // ================================================================
  // 通知
  // ================================================================

  notification: {
    /**
     * @param {{ type?: string, unread_only?: boolean, page?: number, size?: number }} [params]
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<{ items: object[], total?: number }>}
     */
    getList(params = {}, options = {}) {
      return request.get(API_ENDPOINTS.NOTIFICATIONS, params, options);
    },

    /**
     * @param {number|string} notification_id
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<object>}
     */
    markRead(notification_id, options = {}) {
      return request.post(API_ENDPOINTS.NOTIFICATIONS_MARK_READ, { notification_id }, options);
    },

    /**
     * @param {{ type?: string }} [params]
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<{ count: number }>}
     */
    getUnreadCount(params = {}, options = {}) {
      return request.get(API_ENDPOINTS.NOTIFICATIONS_UNREAD_COUNT, params, options);
    }
  },

  // ================================================================
  // 管理员
  // ================================================================

  admin: {
    /**
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<object>}
     */
    getPunchLocation(options = {}) {
      return request.get(API_ENDPOINTS.ADMIN_PUNCH_LOCATION, {}, options);
    },

    /**
     * @param {object} data
     * @param {{ showError?: boolean, headers?: object }} [options]
     * @returns {Promise<object>}
     */
    setPunchLocation(data, options = {}) {
      return request.post(API_ENDPOINTS.ADMIN_PUNCH_LOCATION, data, options);
    }
  }
};

module.exports = api;
