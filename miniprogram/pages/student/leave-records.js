// pages/student/leave-records.js
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
    leaveRecords: [],
    isLoading: false
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
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    // 页面显示时加载请假记录
    this.getLeaveRecords();
  },

  /**
   * 返回上一页
   */
  onBack() {
    wx.navigateBack();
  },

  /**
   * 刷新请假记录
   */
  onRefresh() {
    this.getLeaveRecords();
  },

  /**
   * 获取请假记录
   */
  getLeaveRecords() {
    const { userInfo } = this.data;
    
    // 显示加载状态
    this.setData({
      isLoading: true
    });
    
    // 调用后端API获取请假记录
    auth.getLeaveRecords(userInfo.user_id)
      .then(res => {
        if (res.success) {
          this.setData({
            leaveRecords: res.data || []
          });
        } else {
          wx.showToast({
            title: res.message || '获取请假记录失败',
            icon: 'none',
            duration: 2000
          });
        }
      })
      .catch(err => {
        console.error('获取请假记录失败:', err);
        wx.showToast({
          title: '网络错误，获取请假记录失败',
          icon: 'none',
          duration: 2000
        });
      })
      .finally(() => {
        // 隐藏加载状态
        this.setData({
          isLoading: false
        });
      });
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

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
    this.getLeaveRecords();
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