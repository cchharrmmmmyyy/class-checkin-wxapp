const { request } = require('../../../network/request.js');

Page({
  data: {
    startDate: '',
    endDate: '',
    leaveType: '事假',
    reason: '',
    leaveTypes: ['事假', '病假', '其他']
  },

  onStartDateChange(e) {
    this.setData({ startDate: e.detail.value });
  },

  onEndDateChange(e) {
    this.setData({ endDate: e.detail.value });
  },

  onLeaveTypeChange(e) {
    const index = e.detail.value;
    this.setData({ leaveType: this.data.leaveTypes[index] });
  },

  onReasonInput(e) {
    this.setData({ reason: e.detail.value });
  },

  async onSubmit() {
    const { startDate, endDate, reason } = this.data;

    if (!startDate) {
      wx.showToast({ title: '请选择开始日期', icon: 'none' });
      return;
    }

    if (!endDate) {
      wx.showToast({ title: '请选择结束日期', icon: 'none' });
      return;
    }

    if (new Date(startDate) < new Date(new Date().toDateString())) {
      wx.showToast({ title: '开始日期不能早于今天', icon: 'none' });
      return;
    }

    if (new Date(endDate) < new Date(startDate)) {
      wx.showToast({ title: '结束日期不能早于开始日期', icon: 'none' });
      return;
    }

    if (!reason || !reason.trim()) {
      wx.showToast({ title: '请填写请假事由', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '提交中...', mask: true });

    request('/student/leave/apply', 'POST', {
      start_date: startDate,
      end_date: endDate,
      leave_type: this.data.leaveType,
      reason: reason
    })
      .then(() => {
        wx.showToast({ title: '提交成功', icon: 'success' });
        setTimeout(() => {
          wx.navigateBack();
        }, 1500);
      })
      .catch(err => {
        console.error('提交请假申请失败', err);
      })
      .finally(() => {
        wx.hideLoading();
      });
  }
});