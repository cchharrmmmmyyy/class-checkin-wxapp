const api = require('../../../network/api.js');

Page({
  data: {
    targetDate: '',
    reason: ''
  },

  onTargetDateChange(e) {
    this.setData({ targetDate: e.detail.value });
  },

  onReasonInput(e) {
    this.setData({ reason: e.detail.value });
  },

  async onSubmit() {
    const { targetDate, reason } = this.data;

    if (!targetDate) {
      wx.showToast({ title: '请选择补卡日期', icon: 'none' });
      return;
    }

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const selectedDate = new Date(targetDate);
    const threeDaysAgo = new Date(today);
    threeDaysAgo.setDate(threeDaysAgo.getDate() - 2);

    if (selectedDate < threeDaysAgo || selectedDate > today) {
      wx.showToast({ title: '补卡日期仅限近3天内', icon: 'none' });
      return;
    }

    if (!reason || !reason.trim()) {
      wx.showToast({ title: '请填写补卡原因', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '提交中...', mask: true });

    api.student.applyMakeup({
      target_date: targetDate,
      reason: reason
    })
      .then(() => {
        wx.showToast({ title: '提交成功', icon: 'success' });
        setTimeout(() => {
          wx.navigateBack();
        }, 1500);
      })
      .catch(err => {
        console.error('提交补卡申请失败', err);
      })
      .finally(() => {
        wx.hideLoading();
      });
  }
});