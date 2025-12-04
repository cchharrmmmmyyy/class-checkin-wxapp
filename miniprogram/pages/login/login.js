// pages/login/login.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    user_id: '',
    password: ''
  },
  /**
   * 学号/工号输入事件
   */
  onUserIdInput(e) {
    this.setData({
      user_id: e.detail.value
    });
  },

  /**
   * 密码输入事件
   */
  onPasswordInput(e) {
    this.setData({
      password: e.detail.value
    });
  },

  /**
   * 登录事件
   */
  onLogin() {
    const { user_id, password } = this.data;
    
    // 简单验证
    if (!user_id.trim()) {
      wx.showToast({
        title: '请输入学号/工号',
        icon: 'none'
      });
      return;
    }
    
    if (!password.trim()) {
      wx.showToast({
        title: '请输入密码',
        icon: 'none'
      });
      return;
    }
    
    // 显示加载中
    wx.showLoading({
      title: '登录中...'
    });
    
    // 准备登录数据
    const loginData = {
      user_id: user_id,
      password: password
    };
    
    // 调用后端API进行登录
    wx.request({
      url: 'http://localhost:5000/api/login',
      method: 'POST',
      data: loginData,
      success: (res) => {
        wx.hideLoading();
        
        if (res.data.success) {
          wx.showToast({
            title: '登录成功',
            icon: 'success'
          });
          
          // 保存用户信息到本地存储
          wx.setStorageSync('userInfo', res.data.user);
          
          // 根据后端返回的重定向URL进行跳转
          if (res.data.redirect_url) {
            // 如果是学生角色，跳转到学生页面
            if (res.data.user.role === 'student') {
              wx.redirectTo({
                url: '/pages/student/student'
              });
            } else if (res.data.user.role === 'teacher') {
              wx.redirectTo({
                url: '/pages/teacher/teacher'
              });
            } else if (res.data.user.role === 'monitor') {
              // 班委角色也跳转到学生页面
              wx.redirectTo({
                url: '/pages/student/student'
              });
            } else {
              wx.redirectTo({
                url: '/pages/student/student'
              });
            }
          }
        } else {
          wx.showToast({
            title: res.data.message || '登录失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        wx.showToast({
          title: '网络错误，请检查后端服务',
          icon: 'none'
        });
        console.error('登录请求失败:', err);
      }
    });
  },

  /**
   * 注册跳转
   */
  onRegister() {
    wx.showToast({
      title: '注册功能开发中',
      icon: 'none'
    });
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {

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