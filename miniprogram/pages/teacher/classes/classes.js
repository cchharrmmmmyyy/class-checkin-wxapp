const api = require('../../../network/api.js');

Page({
  data: {
    classes: [],
    loading: false
  },

  onLoad() {
    this.loadClasses();
  },

  onPullDownRefresh() {
    this.loadClasses().finally(() => {
      wx.stopPullDownRefresh();
    });
  },

  async loadClasses() {
    this.setData({ loading: true });

    api.teacher.getClasses()
      .then(async classes => {
        const classesWithStats = await Promise.all(
          classes.map(async (cls) => {
            const className = typeof cls === 'string' ? cls : cls.class_name;
            try {
              const [summary, leaveRes, makeupRes] = await Promise.all([
                api.teacher.getClassPunchSummary({
                  class_name: className,
                  date: new Date().toISOString().split('T')[0]
                }).catch(() => null),
                api.teacher.getLeavePending({
                  class_name: className
                }).catch(() => ({ items: [] })),
                api.teacher.getMakeupPending({
                  class_name: className
                }).catch(() => ({ items: [] }))
              ]);

              return {
                class_name: className,
                attendance_rate: summary && summary.attendance_rate
                  ? (summary.attendance_rate * 100).toFixed(2)
                  : '0.00',
                pending_count: (leaveRes.total || 0) + (makeupRes.total || 0)
              };
            } catch {
              return { class_name: className, attendance_rate: '0.00', pending_count: 0 };
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