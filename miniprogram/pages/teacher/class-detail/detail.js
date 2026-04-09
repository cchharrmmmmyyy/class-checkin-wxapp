const { request } = require('../../../network/request.js');

Page({
  data: {
    className: '',
    currentDate: '',
    summary: null,
    students: [],
    filteredStudents: [],
    filterStatus: '全部',
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
    const filterStatus = this.data.statusOptions[index];
    const { students } = this.data;
    let filteredStudents = students;

    if (filterStatus !== '全部') {
      const statusMap = {
        '已打卡': 'present',
        '未打卡': 'absent',
        '请假': 'leave'
      };
      filteredStudents = students.filter(s => s.status === statusMap[filterStatus]);
    }

    this.setData({ filterStatus, filteredStudents });
  },

  async loadData() {
    try {
      const summary = await request('/teacher/class/punch-summary', 'GET', {
        class_name: this.data.className,
        date: this.data.currentDate
      });

      const students = summary ? (summary.details || []) : [];
      const filterStatus = this.data.filterStatus;
      let filteredStudents = students;

      if (filterStatus !== '全部') {
        const statusMap = {
          '已打卡': 'present',
          '未打卡': 'absent',
          '请假': 'leave'
        };
        filteredStudents = students.filter(s => s.status === statusMap[filterStatus]);
      }

      this.setData({
        students,
        filteredStudents,
        summary
      });
    } catch (err) {
      console.error('加载班级详情失败', err);
    }
  }
});