const BASE_URL = 'http://localhost:5000/api';

App({
  globalData: {
    userInfo: null,
    token: null
  },

  onLaunch() {
    const token = wx.getStorageSync('token');
    const userInfo = wx.getStorageSync('userInfo');
    if (token && userInfo) {
      this.globalData.token = token;
      this.globalData.userInfo = userInfo;
    }
  },

  getUserInfo: function() {
    return this.globalData.userInfo;
  },

  setUserInfo: function(userInfo, token) {
    if (token) {
      wx.setStorageSync('token', token);
      this.globalData.token = token;
    }
    if (userInfo) {
      wx.setStorageSync('userInfo', userInfo);
      this.globalData.userInfo = userInfo;
    }
  },

  clearUserInfo: function() {
    wx.removeStorageSync('token');
    wx.removeStorageSync('userInfo');
    this.globalData.token = null;
    this.globalData.userInfo = null;
  },

  navigateByRole: function(role) {
    if (role === 'student' || role === 'monitor') {
      wx.reLaunch({ url: '/pages/student/index/index' });
    } else if (role === 'teacher') {
      wx.reLaunch({ url: '/pages/teacher/classes/classes' });
    } else if (role === 'admin') {
      wx.showModal({ content: '请使用浏览器访问管理后台' });
    }
  }
});