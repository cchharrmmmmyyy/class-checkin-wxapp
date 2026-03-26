// pages/student/student-detail.js
import api from '../../network/api.js';
import utils from '../../utils/utils.js';

Page({
  data: {
    userInfo: {
      username: '学生',
      role: 'student',
      class: ''
    },
    showResults: false,
    myRecords: [],
    classRecords: [],
    resultTitle: '',
    themeClass: ''
  },

  onLoad(options) {
    const userInfo = utils.getUserInfo();
    if (userInfo) {
      this.setData({ userInfo });
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

  onQueryMyRecords() {
    utils.showLoading();

    api.student.getRecords(this.data.userInfo.user_id)
      .then(res => {
        utils.hideLoading();

        if (res.success) {
          this.setData({
            showResults: true,
            myRecords: res.data,
            classRecords: [],
            resultTitle: '我的打卡记录'
          });
          utils.showToast('查询成功', 'success', 1000);
        } else {
          utils.showToast(res.message || '查询失败', 'none', 2000);
        }
      })
      .catch(err => {
        utils.hideLoading();
        console.error('查询打卡记录失败:', err);

        const mockRecords = [
          { punch_date: '2024-01-15', status: '已打卡' },
          { punch_date: '2024-01-14', status: '已打卡' },
          { punch_date: '2024-01-13', status: '已打卡' }
        ];

        this.setData({
          showResults: true,
          myRecords: mockRecords,
          classRecords: [],
          resultTitle: '我的打卡记录（离线数据）'
        });

        utils.showToast('网络错误，显示离线数据', 'none', 2000);
      });
  },

  onQueryClassRecords() {
    utils.showLoading();

    api.student.getClassRecords(this.data.userInfo.class)
      .then(res => {
        utils.hideLoading();

        if (res.success) {
          this.setData({
            showResults: true,
            classRecords: res.data,
            myRecords: [],
            resultTitle: '班级今日打卡情况'
          });
          utils.showToast('查询成功', 'success', 1000);
        } else {
          utils.showToast(res.message || '查询失败', 'none', 2000);
        }
      })
      .catch(err => {
        utils.hideLoading();
        console.error('查询班级打卡记录失败:', err);

        const mockClassRecords = [
          { username: 'student1', punched: true, punchTime: '08:25:30' },
          { username: 'student2', punched: true, punchTime: '08:30:15' },
          { username: 'student3', punched: false, punchTime: '' },
          { username: 'student4', punched: true, punchTime: '08:28:45' },
          { username: 'student5', punched: false, punchTime: '' }
        ];

        this.setData({
          showResults: true,
          classRecords: mockClassRecords,
          myRecords: [],
          resultTitle: '班级今日打卡情况（离线数据）'
        });

        utils.showToast('网络错误，显示离线数据', 'none', 2000);
      });
  },

  onApplyLeave() {
    utils.navigateTo('/pages/student/leave-apply');
  }
});
