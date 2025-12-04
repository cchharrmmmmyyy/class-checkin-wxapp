// pages/student/student.js
const auth = require('../../utils/auth.js')

Page({

  /**
   * 页面的初始数据
   */
  data: {
    userInfo: {
      username: '学生',
      role: 'student',
      class: ''
    },
    lastPunchTime: ''
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
    
    // 获取上次打卡时间
    const lastPunchTime = wx.getStorageSync('lastPunchTime');
    if (lastPunchTime) {
      this.setData({
        lastPunchTime: lastPunchTime
      });
    }
  },

  /**
   * 打卡功能
   */
  onPunchCard() {
    const now = new Date();
    const punchTime = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()} ${now.getHours()}:${now.getMinutes()}:${now.getSeconds()}`;
    
    // 调用后端API提交打卡记录
    auth.submitPunchRecord(this.data.userInfo)
      .then(res => {
        if (res.success) {
          // 显示打卡成功提示
          wx.showToast({
            title: '打卡成功！',
            icon: 'success',
            duration: 2000
          });
          
          // 更新打卡时间
          this.setData({
            lastPunchTime: punchTime
          });
          
          // 保存到本地存储
          wx.setStorageSync('lastPunchTime', punchTime);
          
          console.log('打卡时间：', punchTime);
        } else {
          // 显示打卡失败信息
          wx.showToast({
            title: res.message || '打卡失败',
            icon: 'none',
            duration: 2000
          });
          
          // 如果是重复打卡，更新本地存储的打卡时间
          if (res.message && res.message.includes('已打卡')) {
            this.setData({
              lastPunchTime: punchTime
            });
            wx.setStorageSync('lastPunchTime', punchTime);
          }
        }
      })
      .catch(err => {
        console.error('打卡请求失败:', err);
        
        // 检查是否是重复打卡错误
        const isAlreadyPunched = err.data && err.data.already_punched;
        
        if (isAlreadyPunched || (err.message && err.message.includes('已打卡'))) {
          wx.showToast({
            title: '今日已打卡',
            icon: 'none',
            duration: 2000
          });
          
          // 更新本地存储的打卡时间
          this.setData({
            lastPunchTime: punchTime
          });
          wx.setStorageSync('lastPunchTime', punchTime);
        } else {
          wx.showToast({
            title: '网络错误，打卡失败',
            icon: 'none',
            duration: 2000
          });
          
          // 如果网络请求失败，仍然保存到本地存储作为备份
          this.setData({
            lastPunchTime: punchTime
          });
          wx.setStorageSync('lastPunchTime', punchTime);
        }
      });
  },

  /**
   * 跳转到详情页面
   */
  onGoToDetail() {
    wx.navigateTo({
      url: '/pages/student/student-detail'
    });
  },

  /**
   * 跳转到请假申请页面
   */
  onLeaveApply() {
    wx.navigateTo({
      url: '/pages/student/leave-apply'
    });
  },

  /**
   * 跳转到请假记录页面
   */
  onViewLeaveRecords() {
    wx.navigateTo({
      url: '/pages/student/leave-records'
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