// pages/student/student-detail.js
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
    showResults: false,
    myRecords: [],
    classRecords: [],
    resultTitle: ''
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
   * 查询个人打卡记录
   */
  onQueryMyRecords() {
    // 显示加载中提示
    wx.showLoading({
      title: '加载中...',
    });
    
    // 调用后端API获取个人打卡记录
    auth.getMyPunchRecords(this.data.userInfo.user_id)
      .then(res => {
        wx.hideLoading();
        
        if (res.success) {
          this.setData({
            showResults: true,
            myRecords: res.data,
            classRecords: [],
            resultTitle: '我的打卡记录'
          });
          
          wx.showToast({
            title: '查询成功',
            icon: 'success',
            duration: 1000
          });
        } else {
          wx.showToast({
            title: res.message || '查询失败',
            icon: 'none',
            duration: 2000
          });
        }
      })
      .catch(err => {
        wx.hideLoading();
        console.error('查询打卡记录失败:', err);
        
        // 如果网络请求失败，使用模拟数据
        const mockRecords = [
          { punch_date: '2024-01-15', status: '已打卡' },
          { punch_date: '2024-01-14', status: '已打卡' },
          { punch_date: '2024-01-13', status: '已打卡' }
        ];
        
        this.setData({
          showResults: true,
          myRecords: mockRecords,
          classRecords: [],
          resultTitle: '我的打卡记录（离线数据）'
        });
        
        wx.showToast({
          title: '网络错误，显示离线数据',
          icon: 'none',
          duration: 2000
        });
      });
  },

  /**
   * 查询班级打卡情况
   */
  onQueryClassRecords() {
    // 显示加载中提示
    wx.showLoading({
      title: '加载中...',
    });
    
    // 调用后端API获取班级打卡记录
    auth.getClassPunchRecords(this.data.userInfo.class)
      .then(res => {
        wx.hideLoading();
        
        if (res.success) {
          this.setData({
            showResults: true,
            classRecords: res.data,
            myRecords: [],
            resultTitle: '班级今日打卡情况'
          });
          
          wx.showToast({
            title: '查询成功',
            icon: 'success',
            duration: 1000
          });
        } else {
          wx.showToast({
            title: res.message || '查询失败',
            icon: 'none',
            duration: 2000
          });
        }
      })
      .catch(err => {
        wx.hideLoading();
        console.error('查询班级打卡记录失败:', err);
        
        // 如果网络请求失败，使用模拟数据
        const mockClassRecords = [
          { username: 'student1', punched: true, punchTime: '08:25:30' },
          { username: 'student2', punched: true, punchTime: '08:30:15' },
          { username: 'student3', punched: false, punchTime: '' },
          { username: 'student4', punched: true, punchTime: '08:28:45' },
          { username: 'student5', punched: false, punchTime: '' }
        ];
        
        this.setData({
          showResults: true,
          classRecords: mockClassRecords,
          myRecords: [],
          resultTitle: '班级今日打卡情况（离线数据）'
        });
        
        wx.showToast({
          title: '网络错误，显示离线数据',
          icon: 'none',
          duration: 2000
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