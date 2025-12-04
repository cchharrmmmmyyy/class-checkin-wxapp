// pages/teacher/teacher.js
const auth = require('../../utils/auth.js')

Page({

  /**
   * 页面的初始数据
   */
  data: {
    userInfo: {
      username: '教师',
      role: 'teacher',
      class: ''
    },
    studentId: '', // 用于任命班委的学号输入
    classRecords: [], // 班级打卡记录
    punchRate: 0, // 打卡率
    isLoading: false, // 加载状态
    selectedClass: '', // 当前选择的班级
    classList: [], // 可选班级列表
    showClassPicker: false, // 是否显示班级选择器
    currentMonitors: [], // 当前班级的班委信息列表（支持多个班委）
    leaveApplications: [], // 待审批请假申请列表
    isLoadingLeave: false // 请假申请加载状态
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    // 从本地存储获取用户信息
    const userInfo = wx.getStorageSync('userInfo');
    if (userInfo) {
      this.setData({
        userInfo: userInfo
      });
      
      // 获取班级列表
      this.loadClassList();
    }
  },

  /**
   * 加载班级列表
   */
  loadClassList() {
    wx.showLoading({
      title: '加载班级列表...'
    });

    // 调用auth方法获取班级列表
    auth.getClassList()
      .then(res => {
        wx.hideLoading();
        
        // 检查响应是否成功
        if (res.success) {
          const classList = res.data || [];
          
          this.setData({
            classList: classList
          });
          
          // 如果还没有选择班级，默认选择第一个班级
          if (!this.data.selectedClass && classList.length > 0) {
            this.setData({
              selectedClass: classList[0]
            });
          }
          
          // 获取班级打卡记录
          this.loadClassRecords();
        } else {
          wx.showToast({
            title: res.message || '获取班级列表失败',
            icon: 'none'
          });
        }
      })
      .catch(err => {
        wx.hideLoading();
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        });
        console.error('获取班级列表失败:', err);
      });
  },

  /**
   * 显示班级选择器
   */
  onShowClassPicker() {
    this.setData({
      showClassPicker: true
    });
  },

  /**
   * 隐藏班级选择器
   */
  onHideClassPicker() {
    this.setData({
      showClassPicker: false
    });
  },

  /**
   * 选择班级
   */
  onSelectClass(e) {
    const selectedClass = e.currentTarget.dataset.class;
    this.setData({
      selectedClass: selectedClass,
      showClassPicker: false
    });
    
    // 加载所选班级的打卡记录
    this.loadClassRecords();
  },

  /**
   * 加载班级打卡记录
   */
  loadClassRecords() {
    if (!this.data.selectedClass) {
      wx.showToast({
        title: '请选择班级',
        icon: 'none'
      });
      return;
    }

    this.setData({ isLoading: true });
    
    // 同时获取班级打卡记录、班委信息和请假申请
    Promise.all([
      auth.getClassPunchRecords(this.data.selectedClass),
      this.getClassMonitor(this.data.selectedClass),
      this.getLeaveApplications(this.data.selectedClass)
    ])
      .then(([recordsRes, monitorRes, leaveRes]) => {
        // 处理打卡记录
        if (recordsRes.success) {
          const records = recordsRes.data;
          const totalStudents = records.length;
          const punchedStudents = records.filter(student => student.punched).length;
          const punchRate = totalStudents > 0 ? Math.round((punchedStudents / totalStudents) * 100) : 0;
          
          this.setData({
            classRecords: records,
            punchRate: punchRate
          });
        } else {
          wx.showToast({
            title: recordsRes.message || '获取班级打卡记录失败',
            icon: 'none'
          });
        }
        
        // 处理班委信息
        if (monitorRes.success) {
          this.setData({
            currentMonitors: monitorRes.data
          });
        } else {
          console.error('获取班委信息失败:', monitorRes.message);
        }
        
        // 处理请假申请
        if (leaveRes.success) {
          this.setData({
            leaveApplications: leaveRes.data || []
          });
        } else {
          console.error('获取请假申请失败:', leaveRes.message);
        }
        
        this.setData({ isLoading: false });
      })
      .catch(err => {
        console.error('获取班级信息失败:', err);
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        });
        this.setData({ isLoading: false });
      });
  },
  
  /**
   * 获取待审批请假申请
   */
  getLeaveApplications(className) {
    this.setData({ isLoadingLeave: true });
    
    return auth.getLeaveApplications(className)
      .then(res => {
        this.setData({ isLoadingLeave: false });
        return res;
      })
      .catch(err => {
        this.setData({ isLoadingLeave: false });
        console.error('获取请假申请失败:', err);
        return { success: false, message: '获取请假申请失败' };
      });
  },

  /**
   * 获取班级班委信息
   */
  getClassMonitor(className) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `http://localhost:5000/api/teacher/class-monitor/${className}`,
        method: 'GET',
        success: (res) => {
          resolve(res.data);
        },
        fail: (err) => {
          reject(err);
        }
      });
    });
  },

  /**
   * 学号输入事件
   */
  onStudentIdInput(e) {
    this.setData({
      studentId: e.detail.value
    });
  },

  /**
   * 任命班委
   */
  onAppointMonitor() {
    const { studentId } = this.data;
    
    if (!studentId.trim()) {
      wx.showToast({
        title: '请输入学号',
        icon: 'none'
      });
      return;
    }

    wx.showModal({
      title: '确认任命',
      content: `确定要任命学号为 ${studentId} 的学生为班委吗？`,
      success: (res) => {
        if (res.confirm) {
          this.appointMonitor(studentId);
        }
      }
    });
  },

  /**
   * 执行任命班委操作
   */
  appointMonitor(studentId) {
    wx.showLoading({
      title: '任命中...'
    });

    const requestData = {
      student_id: studentId,
      teacher_id: this.data.userInfo.user_id,
      class_name: this.data.selectedClass
    };
    
    console.log('发送任命班委请求:', requestData);
    console.log('当前用户信息:', this.data.userInfo);

    // 调用后端API任命班委
    wx.request({
      url: 'http://localhost:5000/api/teacher/appoint-monitor',
      method: 'POST',
      data: requestData,
      success: (res) => {
        console.log('任命班委响应:', res);
        wx.hideLoading();
        
        if (res.data.success) {
          wx.showToast({
            title: '任命成功',
            icon: 'success'
          });
          
          // 清空输入框
          this.setData({
            studentId: ''
          });
          
          // 更新班委信息
          this.getClassMonitor(this.data.selectedClass)
            .then(monitorRes => {
              if (monitorRes.success) {
                this.setData({
                  currentMonitors: monitorRes.data || []
                });
              }
            });
          
          // 刷新班级打卡记录
          this.loadClassRecords();
        } else {
          wx.showToast({
            title: res.data.message || '任命失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        console.error('任命班委请求失败:', err);
        wx.hideLoading();
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        });
        console.error('任命班委失败:', err);
      }
    });
  },

  /**
   * 移除班委
   */
  onRemoveMonitor(e) {
    const studentId = e.currentTarget.dataset.studentId;
    const monitor = this.data.currentMonitors.find(m => m.user_id === studentId);
    
    if (!monitor) {
      wx.showToast({
        title: '班委信息错误',
        icon: 'none'
      });
      return;
    }

    wx.showModal({
      title: '确认移除',
      content: `确定要移除班委 ${monitor.username} (${monitor.user_id}) 吗？`,
      success: (res) => {
        if (res.confirm) {
          this.removeMonitor(studentId);
        }
      }
    });
  },

  /**
   * 执行移除班委操作
   */
  removeMonitor(studentId) {
    wx.showLoading({
      title: '移除中...'
    });

    // 调用后端API移除班委
    wx.request({
      url: 'http://localhost:5000/api/teacher/remove-monitor',
      method: 'POST',
      data: {
        student_id: studentId,
        teacher_id: this.data.userInfo.user_id
      },
      success: (res) => {
        console.log('移除班委响应:', res);
        wx.hideLoading();
        
        if (res.data.success) {
          wx.showToast({
            title: '移除成功',
            icon: 'success'
          });
          
          // 更新班委信息
          this.getClassMonitor(this.data.selectedClass)
            .then(monitorRes => {
              if (monitorRes.success) {
                this.setData({
                  currentMonitors: monitorRes.data || []
                });
              }
            });
          
          // 刷新班级打卡记录
          this.loadClassRecords();
        } else {
          wx.showToast({
            title: res.data.message || '移除失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        console.error('移除班委请求失败:', err);
        wx.hideLoading();
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        });
      }
    });
  },

  /**
   * 刷新班级打卡记录
   */
  onRefreshRecords() {
    this.loadClassRecords();
  },

  /**
   * 同意请假申请
   */
  onApproveLeave(e) {
    const leaveId = e.currentTarget.dataset.leaveId;
    this.handleLeaveApproval(leaveId, 'approved');
  },

  /**
   * 拒绝请假申请
   */
  onRejectLeave(e) {
    const leaveId = e.currentTarget.dataset.leaveId;
    this.handleLeaveApproval(leaveId, 'rejected');
  },

  /**
   * 处理请假审批
   */
  handleLeaveApproval(leaveId, status) {
    const { userInfo } = this.data;
    
    wx.showLoading({
      title: status === 'approved' ? '同意中...' : '拒绝中...'
    });
    
    // 调用后端API处理请假审批
    auth.approveLeave(leaveId, status, userInfo.user_id)
      .then(res => {
        wx.hideLoading();
        
        if (res.success) {
          wx.showToast({
            title: status === 'approved' ? '同意成功' : '拒绝成功',
            icon: 'success'
          });
          
          // 重新加载所有数据，包括请假申请列表
          this.loadClassRecords();
        } else {
          wx.showToast({
            title: res.message || '审批失败',
            icon: 'none'
          });
        }
      })
      .catch(err => {
        wx.hideLoading();
        console.error('请假审批失败:', err);
        wx.showToast({
          title: '网络错误，请重试',
          icon: 'none'
        });
      });
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    // 页面显示时刷新数据
    if (this.data.selectedClass) {
      this.loadClassRecords();
    }
  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {
    this.loadClassRecords();
    wx.stopPullDownRefresh();
  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  }
})