// API工具函数，用于与后端通信

// 后端API基础URL
const BASE_URL = 'http://192.168.31.113:5000/api'

/**
 * 封装微信小程序的请求方法
 * @param {string} url 请求地址
 * @param {object} options 请求选项
 * @returns {Promise} 请求结果
 */
function request(url, options = {}) {
  return new Promise((resolve, reject) => {
    console.log(`发起请求: ${BASE_URL}${url}, 方法: ${options.method || 'GET'}, 数据:`, options.data)
    
    wx.request({
      url: `${BASE_URL}${url}`,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'content-type': 'application/json',
        ...options.header
      },
      success: (res) => {
        console.log(`请求响应: 状态码 ${res.statusCode}, 数据:`, res.data)
        
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          // 对于400等错误，尝试从响应中获取错误消息
          const errorMessage = res.data && res.data.message ? res.data.message : `请求失败: ${res.statusCode}`
          const errorData = res.data || {}
          
          console.error(`请求失败: ${errorMessage}`)
          
          // 创建一个带有额外信息的错误对象
          const error = new Error(errorMessage)
          error.data = errorData  // 添加原始响应数据
          error.statusCode = res.statusCode
          
          reject(error)
        }
      },
      fail: (err) => {
        console.error(`请求网络错误:`, err)
        reject(err)
      }
    })
  })
}

/**
 * 用户登录
 * @param {string} user_id 学号/工号
 * @param {string} password 密码
 * @returns {Promise} 登录结果
 */
function login(user_id, password) {
  return request('/login', {
    method: 'POST',
    data: { user_id, password }
  })
}

/**
 * 提交打卡记录
 * @param {object} userInfo 用户信息
 * @returns {Promise} 打卡结果
 */
function submitPunchRecord(userInfo) {
  return request('/student/punch', {
    method: 'POST',
    data: {
      username: userInfo.username,
      user_id: userInfo.user_id,
      role: userInfo.role,
      class: userInfo.class
    }
  })
}

/**
 * 获取个人打卡记录
 * @param {string} user_id 学号/工号
 * @returns {Promise} 打卡记录列表
 */
function getMyPunchRecords(user_id) {
  return request(`/student/records/${user_id}`)
}

/**
 * 获取班级打卡记录
 * @param {string} className 班级名称
 * @returns {Promise} 班级打卡记录列表
 */
function getClassPunchRecords(className) {
  return request(`/student/class-records/${className}`)
}

/**
 * 获取班级列表
 * @returns {Promise} 班级列表
 */
function getClassList() {
  return request('/teacher/class-list')
}

/**
 * 学生提交请假申请
 * @param {object} userInfo 用户信息
 * @param {string} leaveStartDate 请假开始日期
 * @param {string} leaveEndDate 请假结束日期
 * @returns {Promise} 请假申请结果
 */
function submitLeaveApplication(userInfo, leaveStartDate, leaveEndDate) {
  return request('/student/apply-leave', {
    method: 'POST',
    data: {
      username: userInfo.username,
      user_id: userInfo.user_id,
      leave_start_date: leaveStartDate,
      leave_end_date: leaveEndDate
    }
  })
}

/**
 * 学生获取请假记录
 * @param {string} user_id 学生ID
 * @returns {Promise} 请假记录列表
 */
function getLeaveRecords(user_id) {
  return request(`/student/leave-records?user_id=${user_id}`)
}

/**
 * 教师获取待审批请假申请
 * @param {string} class_name 班级名称
 * @returns {Promise} 请假申请列表
 */
function getLeaveApplications(class_name) {
  return request(`/teacher/leave-applications?class_name=${class_name}`)
}

/**
 * 教师审批请假申请
 * @param {string} leave_id 请假申请ID
 * @param {string} status 审批状态（approved/rejected）
 * @param {string} teacher_id 教师ID
 * @returns {Promise} 审批结果
 */
function approveLeave(leave_id, status, teacher_id) {
  return request('/teacher/approve-leave', {
    method: 'POST',
    data: {
      id: leave_id,
      status: status,
      teacher_id: teacher_id
    }
  })
}

/**
 * 获取班级班委信息
 * @param {string} className 班级名称
 * @returns {Promise} 班委信息
 */
function getClassMonitor(className) {
  return request(`/teacher/class-monitor/${className}`)
}

/**
 * 任命班委
 * @param {string} student_id 学生ID
 * @param {string} class_name 班级名称
 * @param {string} teacher_id 教师ID
 * @returns {Promise} 任命结果
 */
function appointMonitor(student_id, class_name, teacher_id) {
  return request('/teacher/appoint-monitor', {
    method: 'POST',
    data: {
      student_id,
      class_name,
      teacher_id
    }
  })
}

/**
 * 撤销班委
 * @param {string} student_id 学生ID
 * @param {string} class_name 班级名称
 * @param {string} teacher_id 教师ID
 * @returns {Promise} 撤销结果
 */
function removeMonitor(student_id, class_name, teacher_id) {
  return request('/teacher/remove-monitor', {
    method: 'POST',
    data: {
      student_id,
      class_name,
      teacher_id
    }
  })
}

module.exports = {
  login,
  submitPunchRecord,
  getMyPunchRecords,
  getClassPunchRecords,
  getClassList,
  submitLeaveApplication,
  getLeaveRecords,
  getLeaveApplications,
  approveLeave,
  getClassMonitor,
  appointMonitor,
  removeMonitor
}