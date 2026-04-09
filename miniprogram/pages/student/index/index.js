const { request } = require('../../../network/request.js');

Page({
  data: {
    userInfo: null,
    todayPunch: null,
    hasPunched: false,
    punchTime: '',
    punchLocation: '',
    unreadCount: 0
  },

  onLoad() {
    const app = getApp();
    this.setData({ userInfo: app.globalData.userInfo });
  },

  onShow() {
    this.loadTodayPunch();
    this.loadUnreadCount();
  },

  onPullDownRefresh() {
    Promise.all([this.loadTodayPunch(), this.loadUnreadCount()])
      .finally(() => {
        wx.stopPullDownRefresh();
      });
  },

  async loadTodayPunch() {
    try {
      const records = await request('/student/punch-records', 'GET', { limit: 1 });
      if (records && records.length > 0) {
        const today = new Date().toDateString();
        const punch = records.find(r => new Date(r.date).toDateString() === today);
        if (punch) {
          this.setData({
            hasPunched: true,
            punchTime: punch.time,
            punchLocation: punch.location || '未知地点',
            todayPunch: punch
          });
        }
      }
    } catch (err) {
      console.error('加载打卡记录失败', err);
    }
  },

  async loadUnreadCount() {
    try {
      const notifications = await request('/student/notifications', 'GET');
      const unreadCount = notifications.filter(n => !n.is_read).length;
      this.setData({ unreadCount });
    } catch (err) {
      console.error('加载通知失败', err);
    }
  },

  goToNotifications() {
    wx.navigateTo({ url: '/pages/student/notifications/notifications' });
  },

  async onPunch() {
    if (this.data.hasPunched) {
      wx.showToast({ title: '今日已打卡', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '正在打卡...', mask: true });

    try {
      const location = await this.getLocation();
      const userInfo = this.data.userInfo;
      await request('/student/punch', 'POST', {
        user_id: userInfo.user_id,
        latitude: location.latitude,
        longitude: location.longitude
      });
      wx.showToast({ title: '打卡成功', icon: 'success' });
      this.loadTodayPunch();
    } catch (err) {
      console.error('打卡失败', err);
      if (err.code === 1004) {
        wx.showModal({
          title: '打卡失败',
          content: '不在允许的打卡范围内',
          showCancel: false
        });
      }
    } finally {
      wx.hideLoading();
    }
  },

  getLocation() {
    return new Promise((resolve, reject) => {
      wx.getLocation({
        type: 'gcj02',
        success: resolve,
        fail: () => {
          wx.showModal({
            title: '定位失败',
            content: '请开启位置权限后重试',
            showCancel: false
          });
          reject(new Error('获取位置失败'));
        }
      });
    });
  },

  goToLeaveApply() {
    wx.navigateTo({ url: '/pages/student/leave/apply' });
  },

  goToMakeupApply() {
    wx.navigateTo({ url: '/pages/student/makeup/apply' });
  }
});