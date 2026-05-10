const api = require('../../../network/api.js');

Page({
  data: {
    activeTab: 0,
    tabs: ['打卡记录', '请假记录', '补卡记录'],
    punchRecords: [],
    leaveRecords: [],
    makeupRecords: [],
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false
  },

  onLoad() {
    this.loadPunchRecords();
  },

  onTabChange(e) {
    const index = parseInt(e.currentTarget.dataset.index, 10);
    this.setData({ activeTab: index, page: 1, hasMore: true });

    if (index === 0) {
      this.loadPunchRecords();
    } else if (index === 1) {
      this.loadLeaveRecords();
    } else {
      this.loadMakeupRecords();
    }
  },

  async loadPunchRecords() {
    this.setData({ loading: true });

    api.student.getPunchRecords({
      page: this.data.page,
      size: this.data.pageSize
    })
      .then(data => {
        const items = data.items || [];
        this.setData({
          punchRecords: this.data.page === 1 ? items : [...this.data.punchRecords, ...items],
          hasMore: items.length >= this.data.pageSize
        });
      })
      .catch(err => {
        console.error('加载打卡记录失败', err);
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  async loadLeaveRecords() {
    this.setData({ loading: true });

    api.student.getLeaveRecords({
      page: this.data.page,
      size: this.data.pageSize
    })
      .then(data => {
        const items = data.items || [];
        this.setData({
          leaveRecords: this.data.page === 1 ? items : [...this.data.leaveRecords, ...items],
          hasMore: items.length >= this.data.pageSize
        });
      })
      .catch(err => {
        console.error('加载请假记录失败', err);
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  async loadMakeupRecords() {
    this.setData({ loading: true });

    api.student.getMakeupRecords({
      page: this.data.page,
      size: this.data.pageSize
    })
      .then(data => {
        const items = data.items || [];
        this.setData({
          makeupRecords: this.data.page === 1 ? items : [...this.data.makeupRecords, ...items],
          hasMore: items.length >= this.data.pageSize
        });
      })
      .catch(err => {
        console.error('加载补卡记录失败', err);
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  onReachBottom() {
    if (!this.data.hasMore || this.data.loading) return;

    this.setData({ page: this.data.page + 1 });

    if (this.data.activeTab === 0) {
      this.loadPunchRecords();
    } else if (this.data.activeTab === 1) {
      this.loadLeaveRecords();
    } else {
      this.loadMakeupRecords();
    }
  },

  onPullDownRefresh() {
    this.setData({ page: 1, hasMore: true });

    if (this.data.activeTab === 0) {
      this.loadPunchRecords();
    } else if (this.data.activeTab === 1) {
      this.loadLeaveRecords();
    } else {
      this.loadMakeupRecords();
    }

    wx.stopPullDownRefresh();
  }
});