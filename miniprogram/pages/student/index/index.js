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
        const today = new Date().toISOString().split('T')[0];
        const punch = records.find(r => r.punch_date === today);
        if (punch) {
          this.setData({
            hasPunched: true,
            punchTime: punch.punch_time,
            punchLocation: punch.latitude ? '已记录位置' : '未知地点',
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

  checkLocationAuth() {
    return new Promise((resolve, reject) => {
      wx.getSetting({
        success: (res) => {
          if (res.authSetting['scope.userLocation']) {
            resolve(true);
          } else {
            wx.showModal({
              title: '需要位置权限',
              content: '打卡功能需要获取您的位置信息，请授权定位权限',
              confirmText: '去授权',
              cancelText: '取消',
              success: (modalRes) => {
                if (modalRes.confirm) {
                  wx.openSetting({
                    success: (openRes) => {
                      if (openRes.authSetting['scope.userLocation']) {
                        resolve(true);
                      } else {
                        reject(new Error('未授权位置权限'));
                      }
                    },
                    fail: () => {
                      reject(new Error('打开设置失败'));
                    }
                  });
                } else {
                  reject(new Error('用户取消授权'));
                }
              }
            });
          }
        },
        fail: () => {
          reject(new Error('获取设置失败'));
        }
      });
    });
  },

  getLocation() {
    return new Promise((resolve, reject) => {
      this.checkLocationAuth()
        .then(() => {
          wx.getLocation({
            type: 'gcj02',
            success: (res) => {
              console.log('定位成功:', res.latitude, res.longitude);
              resolve(res);
            },
            fail: (err) => {
              console.error('定位失败:', err);
              wx.showModal({
                title: '定位失败',
                content: '无法获取位置信息，请检查定位服务是否开启',
                showCancel: true,
                confirmText: '重试',
                cancelText: '取消',
                success: (modalRes) => {
                  if (modalRes.confirm) {
                    this.getLocation().then(resolve).catch(reject);
                  } else {
                    reject(new Error('用户取消定位'));
                  }
                }
              });
            }
          });
        })
        .catch((err) => {
          reject(err);
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