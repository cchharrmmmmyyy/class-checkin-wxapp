const api = require('../../../network/api.js');

Page({
  data: {
    classes: [],
    selectedClass: '',
    students: [],
    loading: false
  },

  onLoad() {
    this.loadClasses();
  },

  async loadClasses() {
    api.teacher.getClasses()
      .then(classes => {
        const classList = classes.map(c => typeof c === 'string' ? c : c.class_name);
        this.setData({ classes: classList });

        if (classList && classList.length > 0) {
          this.setData({ selectedClass: classList[0] });
          this.loadStudents();
        }
      })
      .catch(err => {
        console.error('加载班级列表失败', err);
      });
  },

  onClassChange(e) {
    const index = parseInt(e.detail.value, 10);
    const className = this.data.classes[index];
    this.setData({ selectedClass: className });
    this.loadStudents();
  },

  async loadStudents() {
    this.setData({ loading: true });

    Promise.all([
      api.teacher.getClassStudents({
        class_name: this.data.selectedClass
      }),
      api.teacher.getMonitors({
        class_name: this.data.selectedClass
      })
    ])
      .then(([students, monitors]) => {
        const monitorIds = monitors.map(m => m.user_id);
        const studentsWithMonitorStatus = students.map(s => ({
          ...s,
          is_monitor: monitorIds.includes(s.user_id)
        }));
        this.setData({ students: studentsWithMonitorStatus });
      })
      .catch(err => {
        console.error('加载学生列表失败', err);
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  onAppoint(e) {
    const student = e.currentTarget.dataset.student;

    wx.showModal({
      title: '确认',
      content: `确定任命 ${student.username} 为班委？`,
      success: (res) => {
        if (res.confirm) {
          api.teacher.appointMonitor({
            student_id: student.user_id,
            class_name: this.data.selectedClass
          })
            .then(() => {
              wx.showToast({ title: '任命成功', icon: 'success' });
              this.loadStudents();
            })
            .catch(err => {
              console.error('任命班委失败', err);
            });
        }
      }
    });
  },

  onRemove(e) {
    const student = e.currentTarget.dataset.student;

    wx.showModal({
      title: '确认',
      content: `确定撤销 ${student.username} 的班委身份？`,
      success: (res) => {
        if (res.confirm) {
          api.teacher.removeMonitor({
            student_id: student.user_id,
            class_name: this.data.selectedClass
          })
            .then(() => {
              wx.showToast({ title: '已撤销', icon: 'success' });
              this.loadStudents();
            })
            .catch(err => {
              console.error('撤销班委失败', err);
            });
        }
      }
    });
  }
});