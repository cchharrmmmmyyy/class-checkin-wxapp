const api = require('../../../network/api.js');

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
    this.loadData().finally(() => {
      wx.stopPullDownRefresh();
    });
  },

  onTabChange(e) {
    const index = parseInt(e.currentTarget.dataset.index, 10);
    this.setData({ activeTab: index });
  },

  async loadData() {
    this.setData({ loading: true });

    try {
      const [leaveRes, makeupRes] = await Promise.all([
        api.teacher.getLeavePending(),
        api.teacher.getMakeupPending()
      ]);
      this.setData({ 
        leaveList: leaveRes.items || [], 
        makeupList: makeupRes.items || [] 
      });
    } catch (err) {
      console.error('加载审批列表失败', err);
    } finally {
      this.setData({ loading: false });
    }
  },

  onApprove(e) {
    const { id, type } = e.currentTarget.dataset;

    wx.showModal({
      title: '确认',
      content: '确定通过该申请？',
      success: async (res) => {
        if (res.confirm) {
          const apiPath = type === 'leave' ? 'approveLeave' : 'approveMakeup';
          const requestData = type === 'leave' ? { leave_id: id, status: 'approved' } : { makeup_id: id, status: 'approved' };
          api.teacher[apiPath](requestData)
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
          const apiPath = type === 'leave' ? 'approveLeave' : 'approveMakeup';
          const requestData = type === 'leave' ? { leave_id: id, status: 'rejected' } : { makeup_id: id, status: 'rejected' };
          api.teacher[apiPath](requestData)
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