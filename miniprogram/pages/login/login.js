const { request } = require('../../network/request.js');

Page({
  data: {
    user_id: '',
    password: ''
  },

  onLoad() {
    const token = wx.getStorageSync('token');
    if (token) {
      const userInfo = wx.getStorageSync('userInfo');
      if (userInfo) {
        getApp().navigateByRole(userInfo.role);
      }
    }
  },

  onUserIdInput(e) {
    this.setData({ user_id: e.detail.value });
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value });
  },

  async onLogin() {
    const { user_id, password } = this.data;

    if (!user_id || user_id.length < 6 || user_id.length > 12) {
      wx.showToast({ title: '账号为6-12位', icon: 'none' });
      return;
    }

    if (!password || password.length < 6 || password.length > 20) {
      wx.showToast({ title: '密码为6-20位', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '登录中...', mask: true });

    try {
      const data = await request('/login', 'POST', { user_id, password });
      wx.setStorageSync('token', data.token);
      wx.setStorageSync('userInfo', data.user);
      getApp().globalData.token = data.token;
      getApp().globalData.userInfo = data.user;
      wx.showToast({ title: '登录成功', icon: 'success' });
      setTimeout(() => {
        getApp().navigateByRole(data.user.role);
      }, 1000);
    } catch (err) {
      console.error('登录失败', err);
      if (err.code === 1003) {
        wx.showModal({
          title: '账户已锁定',
          content: '连续5次密码错误，请1小时后再试',
          showCancel: false
        });
      }
    } finally {
      wx.hideLoading();
    }
  }
});