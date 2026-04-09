const { request } = require('../../../network/request.js');

Page({
  data: {
    userInfo: null,
    currentDate: '',
    className: '',
    summary: null,
    unpunchedStudents: [],
    pendingLeave: [],
    pendingMakeup: [],
    loading: false
  },

  onLoad() {
    const app = getApp();
    this.setData({
      userInfo: app.globalData.userInfo,
      className: app.globalData.userInfo.class_name
    });

    const today = new Date();
    this.setData({ currentDate: today.toISOString().split('T')[0] });
  },

  onShow() {
    this.loadData();
  },

  onPullDownRefresh() {
    this.loadData()
      .finally(() => {
        wx.stopPullDownRefresh();
      });
  },

  onDateChange(e) {
    this.setData({ currentDate: e.detail.value });
    this.loadData();
  },

  async loadData() {
    this.setData({ loading: true });

    Promise.all([
      request('/teacher/class/punch-summary', 'GET', {
        class_name: this.data.className,
        date: this.data.currentDate
      }).catch(err => {
        console.error('加载打卡概览失败', err);
        return null;
      }),
      request('/teacher/leave/pending', 'GET', {
        class_name: this.data.className
      }).catch(err => {
        console.error('加载请假待审批失败', err);
        return [];
      }),
      request('/teacher/makeup/pending', 'GET', {
        class_name: this.data.className
      }).catch(err => {
        console.error('加载补卡待审批失败', err);
        return [];
      })
    ])
      .then(([summary, leavePending, makeupPending]) => {
        this.setData({
          summary,
          unpunchedStudents: summary ? (summary.unpunched_students || []) : [],
          pendingLeave: leavePending || [],
          pendingMakeup: makeupPending || []
        });
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  onRemindStudent(e) {
    const student = e.currentTarget.dataset.student;
    wx.showToast({ title: `已提醒 ${student.username}`, icon: 'success' });
  },

  goToPendingLeave() {
    wx.navigateTo({
      url: `/pages/student/monitor/pending-detail?type=leave`
    });
  },

  goToPendingMakeup() {
    wx.navigateTo({
      url: `/pages/student/monitor/pending-detail?type=makeup`
    });
  }
});