const { request } = require('../../../network/request.js');

Page({
  data: {
    className: '',
    currentDate: '',
    summary: null,
    students: [],
    filterStatus: 'all',
    statusOptions: ['全部', '已打卡', '未打卡', '请假']
  },

  onLoad(options) {
    if (options.class) {
      this.setData({ className: options.class });
    }

    const today = new Date();
    this.setData({ currentDate: today.toISOString().split('T')[0] });

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

  onFilterChange(e) {
    const index = e.detail.value;
    this.setData({ filterStatus: this.data.statusOptions[index] });
  },

  async loadData() {
    try {
      const [students, summary] = await Promise.all([
        request('/teacher/class/students', 'GET', {
          class_name: this.data.className
        }),
        request('/teacher/class/punch-summary', 'GET', {
          class_name: this.data.className,
          date: this.data.currentDate
        })
      ]);

      this.setData({
        students: students || [],
        summary
      });
    } catch (err) {
      console.error('加载班级详情失败', err);
    }
  },

  getFilteredStudents() {
    const { students, filterStatus } = this.data;

    if (filterStatus === '全部' || filterStatus === 'all') {
      return students;
    }

    return students.filter(s => s.status === filterStatus);
  }
});