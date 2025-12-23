// pages/login/login.js
const auth = require('../../utils/auth');

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
  async onLogin() {
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
    
    try {
      // 调用auth.js中的login函数进行登录
      const res = await auth.login(user_id, password);
      
      wx.hideLoading();
      
      if (res.success) {
        wx.showToast({
          title: '登录成功',
          icon: 'success'
        });
        
        // 保存用户信息到本地存储
        wx.setStorageSync('userInfo', res.user);
        
        // 根据后端返回的重定向URL进行跳转
        if (res.redirect_url) {
          // 如果是学生角色，跳转到学生页面
          if (res.user.role === 'student') {
            wx.redirectTo({
              url: '/pages/student/student'
            });
          } else if (res.user.role === 'teacher') {
            wx.redirectTo({
              url: '/pages/teacher/teacher'
            });
          } else if (res.user.role === 'monitor') {
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
          title: res.message || '登录失败',
          icon: 'none'
        });
      }
    } catch (err) {
      wx.hideLoading();
      
      // 更详细的错误处理
      let errorMessage = '登录失败，请重试';
      
      // 判断错误类型
      if (err.errMsg && err.errMsg.includes('request:fail')) {
        // 网络请求失败
        if (err.errMsg.includes('timeout')) {
          errorMessage = '网络连接超时，请检查网络设置';
        } else if (err.errMsg.includes('fail')) {
          errorMessage = '网络连接失败，请检查后端服务是否正常运行';
        }
      } else if (err.statusCode) {
        // HTTP状态码错误
        switch (err.statusCode) {
          case 401:
            errorMessage = '学号/工号或密码错误';
            break;
          case 403:
            errorMessage = '账号被禁用，请联系管理员';
            break;
          case 404:
            errorMessage = '登录服务不可用，请联系技术支持';
            break;
          case 500:
            errorMessage = '服务器内部错误，请稍后再试';
            break;
          default:
            errorMessage = `登录失败 (错误码: ${err.statusCode})`;
        }
      } else if (err.message) {
        // 后端返回的错误信息
        errorMessage = err.message;
      }
      
      wx.showToast({
        title: errorMessage,
        icon: 'none',
        duration: 3000
      });
      
      console.error('登录失败详情:', {
        error: err,
        user_id: user_id,
        timestamp: new Date().toISOString()
      });
    }
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