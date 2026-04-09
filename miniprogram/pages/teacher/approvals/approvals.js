const { request } = require('../../../network/request.js');

Page({
  data: {
    activeTab: 0,
    tabs: ['请假审批', '补卡审批'],
    leaveList: [],
    makeupList: [],
    loading: false
  },

  onLoad() {
    this.loadData();
  },

  onPullDownRefresh() {
    this.loadData()
      .finally(() => {
        wx.stopPullDownRefresh();
      });
  },

  onTabChange(e) {
    const index = e.detail.index;
    this.setData({ activeTab: index });
  },

  async loadData() {
    this.setData({ loading: true });

    Promise.all([
      request('/teacher/leave/pending', 'GET')
        .then(leaveList => {
          this.setData({ leaveList });
        })
        .catch(err => {
          console.error('加载请假审批列表失败', err);
        }),
      request('/teacher/makeup/pending', 'GET')
        .then(makeupList => {
          this.setData({ makeupList });
        })
        .catch(err => {
          console.error('加载补卡审批列表失败', err);
        })
    ])
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  onApprove(e) {
    const { id, type } = e.currentTarget.dataset;

    wx.showModal({
      title: '确认',
      content: '确定通过该申请？',
      success: async (res) => {
        if (res.confirm) {
          const apiPath = type === 'leave' ? '/teacher/leave/approve' : '/teacher/makeup/approve';
          request(apiPath, 'POST', { id, status: 'approved' })
            .then(() => {
              wx.showToast({ title: '已通过', icon: 'success' });
              this.loadData();
            })
            .catch(err => {
              console.error('审批失败', err);
            });
        }
      }
    });
  },

  onReject(e) {
    const { id, type } = e.currentTarget.dataset;

    wx.showModal({
      title: '确认',
      content: '确定拒绝该申请？',
      success: async (res) => {
        if (res.confirm) {
          const apiPath = type === 'leave' ? '/teacher/leave/approve' : '/teacher/makeup/approve';
          request(apiPath, 'POST', { id, status: 'rejected' })
            .then(() => {
              wx.showToast({ title: '已拒绝', icon: 'success' });
              this.loadData();
            })
            .catch(err => {
              console.error('审批失败', err);
            });
        }
      }
    });
  }
});