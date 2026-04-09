const { request } = require('../../../network/request.js');

Page({
  data: {
    type: '',
    leaveList: [],
    makeupList: [],
    loading: false
  },

  onLoad(options) {
    const type = options.type || 'leave';
    this.setData({ type });

    wx.setNavigationBarTitle({
      title: type === 'leave' ? '请假待审批' : '补卡待审批'
    });

    this.loadData();
  },

  onShow() {
    this.loadData();
  },

  async loadData() {
    this.setData({ loading: true });

    try {
      if (this.data.type === 'leave') {
        const list = await request('/student/monitor/class-leaves', 'GET');
        this.setData({ leaveList: list || [] });
      } else {
        const list = await request('/student/monitor/class-makeups', 'GET');
        this.setData({ makeupList: list || [] });
      }
    } catch (err) {
      console.error('加载待审批列表失败', err);
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      });
    } finally {
      this.setData({ loading: false });
    }
  },

  onPullDownRefresh() {
    this.loadData().finally(() => {
      wx.stopPullDownRefresh();
    });
  }
});
