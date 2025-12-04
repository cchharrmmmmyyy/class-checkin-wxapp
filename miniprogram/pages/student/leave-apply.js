// pages/student/leave-apply.js
const auth = require('../../utils/auth.js')

Page({

  /**
   * 页面的初始数据
   */
  data: {
    userInfo: {
      username: '',
      user_id: '',
      class: ''
    },
    leaveStartDate: '',
    leaveEndDate: '',
    leaveDays: 0,
    showDatePicker: false,
    pickerValue: '',
    minDate: '',
    maxDate: '',
    dateType: '', // 'start' or 'end'
    isSubmitting: false, // 防止重复提交的状态标志
    lastSubmitTime: 0 // 上次提交时间，用于防止短时间内重复提交
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
    }
    
    // 设置日期选择器的最小和最大日期
    const now = new Date();
    const minDate = now.getFullYear() + '-' + (now.getMonth() + 1).toString().padStart(2, '0') + '-' + now.getDate().toString().padStart(2, '0');
    const maxDate = (now.getFullYear() + 1) + '-' + (now.getMonth() + 1).toString().padStart(2, '0') + '-' + now.getDate().toString().padStart(2, '0');
    
    this.setData({
      minDate: minDate,
      maxDate: maxDate,
      pickerValue: minDate
    });
  },

  /**
   * 返回上一页
   */
  onBack() {
    wx.navigateBack();
  },

  /**
   * 显示开始日期选择器
   */
  onStartDateTap() {
    this.setData({
      showDatePicker: true,
      dateType: 'start',
      pickerValue: this.data.leaveStartDate || this.data.minDate
    });
  },

  /**
   * 显示结束日期选择器
   */
  onEndDateTap() {
    this.setData({
      showDatePicker: true,
      dateType: 'end',
      pickerValue: this.data.leaveEndDate || this.data.minDate
    });
  },

  /**
   * 隐藏日期选择器
   */
  onHideDatePicker() {
    this.setData({
      showDatePicker: false
    });
  },

  /**
   * 日期选择器值变化
   */
  onDateChange(e) {
    this.setData({
      pickerValue: e.detail.value
    });
  },

  /**
   * 确认选择日期
   */
  onConfirmDate() {
    const { pickerValue, dateType } = this.data;
    
    // 确保pickerValue不为空
    if (!pickerValue || pickerValue === 'null') {
      wx.showToast({
        title: '请选择有效的日期',
        icon: 'none',
        duration: 1500
      });
      return;
    }
    
    if (dateType === 'start') {
      this.setData({
        leaveStartDate: pickerValue
      });
    } else if (dateType === 'end') {
      this.setData({
        leaveEndDate: pickerValue
      });
    }
    
    this.setData({
      showDatePicker: false
    });
    
    // 计算请假天数
    this.calculateLeaveDays();
  },

  /**
   * 计算请假天数
   */
  calculateLeaveDays() {
    const { leaveStartDate, leaveEndDate } = this.data;
    
    if (leaveStartDate && leaveEndDate) {
      const start = new Date(leaveStartDate);
      const end = new Date(leaveEndDate);
      const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;
      
      this.setData({
        leaveDays: days
      });
    }
  },

  /**
   * 提交请假申请
   */
  onSubmitLeave() {
    const { userInfo, leaveStartDate, leaveEndDate, isSubmitting, lastSubmitTime } = this.data;
    
    // 防止重复提交：检查是否正在提交或短时间内重复提交（3秒内）
    if (isSubmitting || Date.now() - lastSubmitTime < 3000) {
      wx.showToast({
        title: '请勿重复提交',
        icon: 'none',
        duration: 1500
      });
      return;
    }
    
    // 加强日期验证
    if (!leaveStartDate || leaveStartDate === null || leaveStartDate === 'null') {
      wx.showToast({
        title: '请选择请假开始日期',
        icon: 'none',
        duration: 2000
      });
      return;
    }
    
    if (!leaveEndDate || leaveEndDate === null || leaveEndDate === 'null') {
      wx.showToast({
        title: '请选择请假结束日期',
        icon: 'none',
        duration: 2000
      });
      return;
    }
    
    // 验证日期顺序
    const startDate = new Date(leaveStartDate);
    const endDate = new Date(leaveEndDate);
    
    if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
      wx.showToast({
        title: '请假日期格式错误',
        icon: 'none',
        duration: 2000
      });
      return;
    }
    
    if (startDate > endDate) {
      wx.showToast({
        title: '结束日期不能早于开始日期',
        icon: 'none',
        duration: 2000
      });
      return;
    }
    
    // 设置提交状态，防止重复提交
    this.setData({
      isSubmitting: true,
      lastSubmitTime: Date.now()
    });
    
    // 调用后端API提交请假申请
    auth.submitLeaveApplication(userInfo, leaveStartDate, leaveEndDate)
      .then(res => {
        if (res.success) {
          // 显示成功提示
          wx.showToast({
            title: '请假申请提交成功',
            icon: 'success',
            duration: 2000
          });
          
          // 延迟返回上一页
          setTimeout(() => {
            wx.navigateBack();
          }, 2000);
        } else {
          // 显示失败提示
          wx.showToast({
            title: res.message || '请假申请失败',
            icon: 'none',
            duration: 2000
          });
        }
      })
      .catch(err => {
        console.error('请假申请失败:', err);
        wx.showToast({
          title: '网络错误，请假申请失败',
          icon: 'none',
          duration: 2000
        });
      })
      .finally(() => {
        // 无论成功失败，都要重置提交状态
        this.setData({
          isSubmitting: false
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