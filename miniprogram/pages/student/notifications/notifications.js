const { request } = require('../../../network/request.js');

Page({
  data: {
    notifications: [],
    loading: false
  },

  onLoad() {
    this.loadNotifications();
  },

  onPullDownRefresh() {
    this.loadNotifications()
      .finally(() => {
        wx.stopPullDownRefresh();
      });
  },

  async loadNotifications() {
    this.setData({ loading: true });

    request('/student/notifications', 'GET')
      .then(notifications => {
        this.setData({ notifications });
      })
      .catch(err => {
        console.error('加载通知失败', err);
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  onNotificationTap(e) {
    const index = parseInt(e.currentTarget.dataset.index, 10);
    const notification = this.data.notifications[index];

    if (notification.is_read) return;

    request('/notifications/mark-read', 'POST', { id: notification.id })
      .then(() => {
        const notifications = this.data.notifications;
        notifications[index].is_read = true;
        this.setData({ notifications });
      })
      .catch(err => {
        console.error('标记已读失败', err);
      });
  },

  onMarkAllRead() {
    request('/notifications/mark-all-read', 'POST')
      .then(() => {
        const notifications = this.data.notifications.map(n => ({ ...n, is_read: true }));
        this.setData({ notifications });
        wx.showToast({ title: '已全部标记已读', icon: 'success' });
      })
      .catch(err => {
        console.error('标记全部已读失败', err);
      });
  }
});