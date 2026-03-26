/**
 * API 服务层 - 统一管理所有接口
 * 业务层调用接口统一从这里导出
 * 改接口只需修改此处，无需动业务代码
 */

import request from './request.js';
import { API_ENDPOINTS } from '../config/api.js';

const api = {
  // 认证相关
  auth: {
    login(user_id, password) {
      return request.post(API_ENDPOINTS.LOGIN, { user_id, password });
    }
  },

  // 学生相关
  student: {
    punch(userInfo, location) {
      return request.post(API_ENDPOINTS.STUDENT_PUNCH, {
        username: userInfo.username,
        user_id: userInfo.user_id,
        role: userInfo.role,
        class: userInfo.class,
        latitude: location ? location.latitude : null,
        longitude: location ? location.longitude : null
      });
    },

    getRecords(user_id) {
      return request.get(`${API_ENDPOINTS.STUDENT_RECORDS}/${user_id}`);
    },

    getClassRecords(className) {
      return request.get(`${API_ENDPOINTS.STUDENT_CLASS_RECORDS}/${className}`);
    },

    applyLeave(userInfo, leaveStartDate, leaveEndDate) {
      return request.post(API_ENDPOINTS.STUDENT_APPLY_LEAVE, {
        username: userInfo.username,
        user_id: userInfo.user_id,
        leave_start_date: leaveStartDate,
        leave_end_date: leaveEndDate
      });
    },

    getLeaveRecords(user_id) {
      return request.get(API_ENDPOINTS.STUDENT_LEAVE_RECORDS, { user_id });
    }
  },

  // 教师相关
  teacher: {
    getClassList() {
      return request.get(API_ENDPOINTS.TEACHER_CLASS_LIST);
    },

    getLeaveApplications(class_name) {
      return request.get(API_ENDPOINTS.TEACHER_LEAVE_APPLICATIONS, { class_name });
    },

    approveLeave(leave_id, status, teacher_id) {
      return request.post(API_ENDPOINTS.TEACHER_APPROVE_LEAVE, {
        id: leave_id,
        status,
        teacher_id
      });
    },

    getClassMonitor(className) {
      return request.get(`${API_ENDPOINTS.TEACHER_CLASS_MONITOR}/${className}`);
    },

    appointMonitor(student_id, class_name, teacher_id) {
      return request.post(API_ENDPOINTS.TEACHER_APPOINT_MONITOR, {
        student_id,
        class_name,
        teacher_id
      });
    },

    removeMonitor(student_id, class_name, teacher_id) {
      return request.post(API_ENDPOINTS.TEACHER_REMOVE_MONITOR, {
        student_id,
        class_name,
        teacher_id
      });
    }
  },

  admin: {
    getPunchLocation() {
      return request.get(API_ENDPOINTS.ADMIN_PUNCH_LOCATION);
    },
    
    setPunchLocation(data) {
      return request.post(API_ENDPOINTS.ADMIN_PUNCH_LOCATION, data);
    }
  }
};

export default api;
