const { request } = require('../../../network/request.js');

Page({
  data: {
    classes: [],
    loading: false
  },

  onLoad() {
    this.loadClasses();
  },

  onPullDownRefresh() {
    this.loadClasses()
      .finally(() => {
        wx.stopPullDownRefresh();
      });
  },

  async loadClasses() {
    this.setData({ loading: true });

    request('/teacher/classes', 'GET')
      .then(async classes => {
        const classesWithStats = await Promise.all(
          classes.map(async (cls) => {
            try {
              const [summary, leavePending, makeupPending] = await Promise.all([
                request('/teacher/class/punch-summary', 'GET', {
                  class_name: cls.class_name,
                  date: new Date().toISOString().split('T')[0]
                }).catch(() => null),
                request('/teacher/leave/pending', 'GET', {
                  class_name: cls.class_name
                }).catch(() => []),
                request('/teacher/makeup/pending', 'GET', {
                  class_name: cls.class_name
                }).catch(() => [])
              ]);

              return {
                ...cls,
                attendance_rate: summary ? summary.attendance_rate : 0,
                pending_count: (leavePending ? leavePending.length : 0) + (makeupPending ? makeupPending.length : 0)
              };
            } catch {
              return { ...cls, attendance_rate: 0, pending_count: 0 };
            }
          })
        );
        this.setData({ classes: classesWithStats });
      })
      .catch(err => {
        console.error('加载班级列表失败', err);
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  goToClassDetail(e) {
    const className = e.currentTarget.dataset.classname;
    wx.navigateTo({
      url: `/pages/teacher/class-detail/detail?class=${className}`
    });
  }
});