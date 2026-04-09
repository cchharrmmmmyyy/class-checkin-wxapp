const { request } = require('../../../network/request.js');

Page({
  data: {
    userInfo: null,
    showPasswordModal: false,
    oldPassword: '',
    newPassword: ''
  },

  onLoad() {
    const app = getApp();
    this.setData({ userInfo: app.globalData.userInfo });
  },

  goToMonitorManage() {
    wx.navigateTo({ url: '/pages/teacher/monitor/manage' });
  },

  goToApprovals() {
    wx.navigateTo({ url: '/pages/teacher/approvals/approvals' });
  },

  onChangePassword() {
    this.setData({ showPasswordModal: true, oldPassword: '', newPassword: '' });
  },

  onCancelPassword() {
    this.setData({ showPasswordModal: false });
  },

  stopPropagation() {},

  onOldPasswordInput(e) {
    this.setData({ oldPassword: e.detail.value });
  },

  onNewPasswordInput(e) {
    this.setData({ newPassword: e.detail.value });
  },

  async onSubmitPassword() {
    const { oldPassword, newPassword } = this.data;

    if (!oldPassword || oldPassword.length < 6) {
      wx.showToast({ title: '请输入至少6位旧密码', icon: 'none' });
      return;
    }

    if (!newPassword || newPassword.length < 6 || newPassword.length > 20) {
      wx.showToast({ title: '新密码为6-20位', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '提交中...', mask: true });

    request('/change-password', 'POST', {
      old_password: oldPassword,
      new_password: newPassword
    })
      .then(() => {
        wx.showToast({ title: '密码修改成功', icon: 'success' });
        this.setData({ showPasswordModal: false });
      })
      .catch(err => {
        console.error('修改密码失败', err);
      })
      .finally(() => {
        wx.hideLoading();
      });
  },

  onLogout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          const app = getApp();
          app.clearUserInfo();
          wx.redirectTo({ url: '/pages/login/login' });
        }
      }
    });
  }
});