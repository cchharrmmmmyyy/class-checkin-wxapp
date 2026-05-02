const { request } = require('../../../network/request.js');

Page({
  data: {
    userInfo: null,
    currentDate: '',
    className: '',
    summary: null,
    attendanceRate: '0',
    unpunchedStudents: [],
    pendingLeave: [],
    pendingMakeup: [],
    loading: false
  },

  onLoad() {
    const app = getApp();
    const userInfo = app.globalData.userInfo || {};
    this.setData({
      userInfo,
      className: userInfo.class_name || userInfo.class || ''
    });

    const today = new Date();
    this.setData({ currentDate: today.toISOString().split('T')[0] });
  },

  onShow() {
    this.loadData();
  },

  onPullDownRefresh() {
    this.loadData().finally(() => {
      wx.stopPullDownRefresh();
    });
  },

  onDateChange(e) {
    this.setData({ currentDate: e.detail.value });
    this.loadData();
  },

  async loadData() {
    this.setData({ loading: true });

    try {
      const [summary, leavePending, makeupPending] = await Promise.all([
        request('/student/monitor/class-punch-status', 'GET', {
          date: this.data.currentDate
        }).catch(err => {
          console.error('加载打卡概览失败', err);
          return null;
        }),
        request('/student/monitor/class-leaves', 'GET').catch(err => {
          console.error('加载请假待审批失败', err);
          return [];
        }),
        request('/student/monitor/class-makeups', 'GET').catch(err => {
          console.error('加载补卡待审批失败', err);
          return [];
        })
      ]);
      const summaryData = summary;
      const attendanceRate = summaryData && summaryData.attendance_rate
        ? (summaryData.attendance_rate * 100).toFixed(2)
        : '0.00';

      this.setData({
        summary: summaryData,
        attendanceRate,
        unpunchedStudents: summaryData ? (summaryData.unpunched_students || []) : [],
        pendingLeave: leavePending || [],
        pendingMakeup: makeupPending || []
      });
    } catch (err) {
      console.error('加载数据失败', err);
    } finally {
      this.setData({ loading: false });
    }
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
