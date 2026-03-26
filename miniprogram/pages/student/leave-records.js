// pages/student/leave-records.js
import api from '../../network/api.js';
import utils from '../../utils/utils.js';

Page({
  data: {
    userInfo: {
      username: '',
      user_id: '',
      class: ''
    },
    leaveRecords: [],
    isLoading: false,
    themeClass: ''
  },

  onLoad(options) {
    const userInfo = utils.getUserInfo();
    if (userInfo) {
      this.setData({ userInfo });
    }

    const app = getApp();
    if (app.themeManager) {
      app.themeManager.applyThemeToPage(this);
      app.themeManager.onThemeChange((themeId) => {
        const theme = app.themeManager.getCurrentThemeClass();
        this.setData({ themeClass: theme });
      });
    }
  },

  onUnload() {
    const app = getApp();
    if (app.themeManager) {
      app.themeManager.offThemeChange();
    }
  },

  onShow() {
    this.getLeaveRecords();
  },

  onBack() {
    utils.navigateBack();
  },

  onRefresh() {
    this.getLeaveRecords();
  },

  getLeaveRecords() {
    const { userInfo } = this.data;

    this.setData({ isLoading: true });

    api.student.getLeaveRecords(userInfo.user_id)
      .then(res => {
        if (res.success) {
          this.setData({ leaveRecords: res.data || [] });
        } else {
          utils.showToast(res.message || '获取请假记录失败', 'none', 2000);
        }
      })
      .catch(err => {
        console.error('获取请假记录失败:', err);
        utils.showToast('网络错误，获取请假记录失败', 'none', 2000);
      })
      .finally(() => {
        this.setData({ isLoading: false });
      });
  },

  onPullDownRefresh() {
    this.getLeaveRecords();
    wx.stopPullDownRefresh();
  }
});
