// pages/teacher/monitor-manage.js
import api from '../../network/api.js';
import utils from '../../utils/utils.js';

Page({
  data: {
    userInfo: {},
    selectedClass: '',
    classList: [],
    showClassPicker: false,
    currentMonitors: [],
    studentId: ''
  },

  onLoad() {
    const userInfo = utils.getUserInfo();
    if (userInfo) {
      this.setData({ userInfo });
      this.loadClassList();
    }
  },

  onShow() {
    if (this.data.selectedClass) {
      this.loadCurrentMonitors();
    }
  },

  loadClassList() {
    api.teacher.getClassList()
      .then(res => {
        if (res.success) {
          const classList = res.data || [];
          this.setData({ classList });

          if (!this.data.selectedClass && classList.length > 0) {
            this.setData({ selectedClass: classList[0] });
            this.loadCurrentMonitors();
          }
        }
      })
      .catch(err => {
        console.error('获取班级列表失败:', err);
      });
  },

  loadCurrentMonitors() {
    if (!this.data.selectedClass) return;

    api.teacher.getClassMonitor(this.data.selectedClass)
      .then(res => {
        if (res.success) {
          this.setData({ currentMonitors: res.data || [] });
        }
      })
      .catch(err => {
        console.error('获取班委列表失败:', err);
      });
  },

  onShowClassPicker() {
    this.setData({ showClassPicker: true });
  },

  onHideClassPicker() {
    this.setData({ showClassPicker: false });
  },

  onSelectClass(e) {
    const selectedClass = e.currentTarget.dataset.class;
    this.setData({
      selectedClass,
      showClassPicker: false
    });
    this.loadCurrentMonitors();
  },

  onStudentIdInput(e) {
    this.setData({ studentId: e.detail.value });
  },

  onAppointMonitor() {
    const { studentId } = this.data;

    if (!studentId.trim()) {
      utils.showToast('请输入学号', 'none');
      return;
    }

    utils.showModal('确认任命', `确定要任命学号为 ${studentId} 的学生为班委吗？`)
      .then(confirmed => {
        if (confirmed) {
          this.appointMonitor(studentId);
        }
      });
  },

  async appointMonitor(studentId) {
    utils.showLoading('任命中...');

    try {
      const res = await api.teacher.appointMonitor(studentId, this.data.selectedClass, this.data.userInfo.user_id);
      utils.hideLoading();

      if (res.success) {
        utils.showToast('任命成功', 'success');
        this.setData({ studentId: '' });
        this.loadCurrentMonitors();
      } else {
        utils.showToast(res.message || '任命失败', 'none');
      }
    } catch (err) {
      console.error('任命班委请求失败:', err);
      utils.hideLoading();
      utils.showToast('网络错误，请重试', 'none');
    }
  },

  onRemoveMonitor(e) {
    const studentId = e.currentTarget.dataset.studentId;
    const monitor = this.data.currentMonitors.find(m => m.user_id === studentId);

    if (!monitor) {
      utils.showToast('班委信息错误', 'none');
      return;
    }

    utils.showModal('确认移除', `确定要移除班委 ${monitor.username} (${monitor.user_id}) 吗？`)
      .then(confirmed => {
        if (confirmed) {
          this.removeMonitor(studentId);
        }
      });
  },

  async removeMonitor(studentId) {
    utils.showLoading('移除中...');

    try {
      const res = await api.teacher.removeMonitor(studentId, this.data.selectedClass, this.data.userInfo.user_id);
      utils.hideLoading();

      if (res.success) {
        utils.showToast('移除成功', 'success');
        this.loadCurrentMonitors();
      } else {
        utils.showToast(res.message || '移除失败', 'none');
      }
    } catch (err) {
      console.error('移除班委请求失败:', err);
      utils.hideLoading();
      utils.showToast('网络错误，请重试', 'none');
    }
  },

  onPullDownRefresh() {
    this.loadCurrentMonitors();
    wx.stopPullDownRefresh();
  }
});
