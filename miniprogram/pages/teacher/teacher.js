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
    classRecords: [],
    punchRate: 0,
    isLoading: false,
    selectedClass: '',
    classList: [],
    showClassPicker: false
  },

  onLoad(options) {
    const userInfo = utils.getUserInfo();
    if (userInfo) {
      this.setData({ userInfo });
      this.loadClassList();
    }
  },

  onShow() {
    if (this.data.selectedClass) {
      this.loadClassRecords();
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
          }

          this.loadClassRecords();
        } else {
          utils.showToast(res.message || '获取班级列表失败', 'none');
        }
      })
      .catch(err => {
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

    api.student.getClassRecords(this.data.selectedClass)
      .then(res => {
        if (res.success) {
          const records = res.data;
          const totalStudents = records.length;
          const punchedStudents = records.filter(student => student.punched).length;
          const punchRate = totalStudents > 0 ? Math.round((punchedStudents / totalStudents) * 100) : 0;

          this.setData({
            classRecords: records,
            punchRate,
            isLoading: false
          });
        } else {
          utils.showToast(res.message || '获取班级打卡记录失败', 'none');
          this.setData({ isLoading: false });
        }
      })
      .catch(err => {
        console.error('获取班级信息失败:', err);
        utils.showToast('网络错误，请重试', 'none');
        this.setData({ isLoading: false });
      });
  },

  onPullDownRefresh() {
    this.loadClassRecords();
    wx.stopPullDownRefresh();
  }
});
