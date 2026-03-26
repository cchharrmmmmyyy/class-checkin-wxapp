// pages/teacher/teacher.js
import api from '../../network/api.js';
import utils from '../../utils/utils.js';

Page({
  data: {
    userInfo: {
      username: '教师',
      role: 'teacher',
      class: ''
    },
    studentId: '',
    classRecords: [],
    punchRate: 0,
    isLoading: false,
    selectedClass: '',
    classList: [],
    showClassPicker: false,
    currentMonitors: [],
    leaveApplications: [],
    isLoadingLeave: false,
    themeClass: ''
  },

  onLoad(options) {
    const userInfo = utils.getUserInfo();
    if (userInfo) {
      this.setData({ userInfo });
      this.loadClassList();
    }

    const app = getApp();
    if (app.themeManager) {
      app.themeManager.applyThemeToPage(this);
      app.themeManager.onThemeChange((themeId) => {
        const theme = app.themeManager.getCurrentThemeClass();
        this.setData({ themeClass: theme });
      });
    }
  },

  onUnload() {
    const app = getApp();
    if (app.themeManager) {
      app.themeManager.offThemeChange();
    }
  },

  loadClassList() {
    utils.showLoading('加载班级列表...');

    api.teacher.getClassList()
      .then(res => {
        utils.hideLoading();

        if (res.success) {
          const classList = res.data || [];
          this.setData({ classList });

          if (!this.data.selectedClass && classList.length > 0) {
            this.setData({ selectedClass: classList[0] });
          }

          this.loadClassRecords();
        } else {
          utils.showToast(res.message || '获取班级列表失败', 'none');
        }
      })
      .catch(err => {
        utils.hideLoading();
        utils.showToast('网络错误，请重试', 'none');
        console.error('获取班级列表失败:', err);
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
    this.loadClassRecords();
  },

  loadClassRecords() {
    if (!this.data.selectedClass) {
      utils.showToast('请选择班级', 'none');
      return;
    }

    this.setData({ isLoading: true });

    Promise.all([
      api.student.getClassRecords(this.data.selectedClass),
      api.teacher.getClassMonitor(this.data.selectedClass),
      api.teacher.getLeaveApplications(this.data.selectedClass)
    ])
      .then(([recordsRes, monitorRes, leaveRes]) => {
        if (recordsRes.success) {
          const records = recordsRes.data;
          const totalStudents = records.length;
          const punchedStudents = records.filter(student => student.punched).length;
          const punchRate = totalStudents > 0 ? Math.round((punchedStudents / totalStudents) * 100) : 0;

          this.setData({
            classRecords: records,
            punchRate
          });
        } else {
          utils.showToast(recordsRes.message || '获取班级打卡记录失败', 'none');
        }

        if (monitorRes.success) {
          this.setData({ currentMonitors: monitorRes.data });
        }

        if (leaveRes.success) {
          this.setData({ leaveApplications: leaveRes.data || [] });
        }

        this.setData({ isLoading: false });
      })
      .catch(err => {
        console.error('获取班级信息失败:', err);
        utils.showToast('网络错误，请重试', 'none');
        this.setData({ isLoading: false });
      });
  },

  getLeaveApplications(className) {
    this.setData({ isLoadingLeave: true });

    return api.teacher.getLeaveApplications(className)
      .then(res => {
        this.setData({ isLoadingLeave: false });
        return res;
      })
      .catch(err => {
        this.setData({ isLoadingLeave: false });
        console.error('获取请假申请失败:', err);
        return { success: false, message: '获取请假申请失败' };
      });
  },

  getClassMonitor(className) {
    return api.teacher.getClassMonitor(className);
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

        const monitorRes = await this.getClassMonitor(this.data.selectedClass);
        if (monitorRes.success) {
          this.setData({ currentMonitors: monitorRes.data || [] });
        }

        this.loadClassRecords();
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

        const monitorRes = await this.getClassMonitor(this.data.selectedClass);
        if (monitorRes.success) {
          this.setData({ currentMonitors: monitorRes.data || [] });
        }

        this.loadClassRecords();
      } else {
        utils.showToast(res.message || '移除失败', 'none');
      }
    } catch (err) {
      console.error('移除班委请求失败:', err);
      utils.hideLoading();
      utils.showToast('网络错误，请重试', 'none');
    }
  },

  onRefreshRecords() {
    this.loadClassRecords();
  },

  onApproveLeave(e) {
    const leaveId = e.currentTarget.dataset.leaveId;
    this.handleLeaveApproval(leaveId, 'approved');
  },

  onRejectLeave(e) {
    const leaveId = e.currentTarget.dataset.leaveId;
    this.handleLeaveApproval(leaveId, 'rejected');
  },

  handleLeaveApproval(leaveId, status) {
    const { userInfo } = this.data;

    utils.showLoading(status === 'approved' ? '同意中...' : '拒绝中...');

    api.teacher.approveLeave(leaveId, status, userInfo.user_id)
      .then(res => {
        utils.hideLoading();

        if (res.success) {
          utils.showToast(status === 'approved' ? '同意成功' : '拒绝成功', 'success');
          this.loadClassRecords();
        } else {
          utils.showToast(res.message || '审批失败', 'none');
        }
      })
      .catch(err => {
        utils.hideLoading();
        console.error('请假审批失败:', err);
        utils.showToast('网络错误，请重试', 'none');
      });
  },

  onChangeTheme() {
    const app = getApp();
    if (app.themeManager) {
      app.themeManager.showThemePicker();
    }
  },

  onShow() {
    if (this.data.selectedClass) {
      this.loadClassRecords();
    }
  },

  onPullDownRefresh() {
    this.loadClassRecords();
    wx.stopPullDownRefresh();
  }
});
