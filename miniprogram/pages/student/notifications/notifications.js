const api = require('../../../network/api.js');

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

    api.notification.getList()
      .then(data => {
        this.setData({ notifications: data.items || [] });
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

    api.notification.markRead(notification.id)
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
    const unreadList = this.data.notifications.filter(n => !n.is_read);
    if (unreadList.length === 0) {
      wx.showToast({ title: '暂无未读通知', icon: 'none' });
      return;
    }

    Promise.all(unreadList.map(item => api.notification.markRead(item.id, { showError: false })))
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
