// pages/student/leave-apply.js
import api from '../../network/api.js';
import utils from '../../utils/utils.js';

Page({
  data: {
    userInfo: {
      username: '',
      user_id: '',
      class: ''
    },
    leaveStartDate: '',
    leaveEndDate: '',
    leaveDays: 0,
    showDatePicker: false,
    pickerValue: '',
    minDate: '',
    maxDate: '',
    dateType: '',
    isSubmitting: false,
    lastSubmitTime: 0,
    themeClass: ''
  },

  onLoad(options) {
    const userInfo = utils.getUserInfo();
    if (userInfo) {
      this.setData({ userInfo });
    }

    const now = new Date();
    const minDate = utils.formatDate(now, 'YYYY-MM-DD');
    const maxDate = utils.formatDate(new Date(now.getFullYear() + 1, now.getMonth(), now.getDate()), 'YYYY-MM-DD');

    this.setData({
      minDate,
      maxDate,
      pickerValue: minDate
    });

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

  onBack() {
    utils.navigateBack();
  },

  onStartDateTap() {
    this.setData({
      showDatePicker: true,
      dateType: 'start',
      pickerValue: this.data.leaveStartDate || this.data.minDate
    });
  },

  onEndDateTap() {
    this.setData({
      showDatePicker: true,
      dateType: 'end',
      pickerValue: this.data.leaveEndDate || this.data.minDate
    });
  },

  onHideDatePicker() {
    this.setData({ showDatePicker: false });
  },

  onDateChange(e) {
    this.setData({ pickerValue: e.detail.value });
  },

  onConfirmDate() {
    const { pickerValue, dateType } = this.data;

    if (!pickerValue || pickerValue === 'null') {
      utils.showToast('请选择有效的日期', 'none', 1500);
      return;
    }

    if (dateType === 'start') {
      this.setData({ leaveStartDate: pickerValue });
    } else if (dateType === 'end') {
      this.setData({ leaveEndDate: pickerValue });
    }

    this.setData({ showDatePicker: false });
    this.calculateLeaveDays();
  },

  calculateLeaveDays() {
    const { leaveStartDate, leaveEndDate } = this.data;

    if (leaveStartDate && leaveEndDate) {
      const start = new Date(leaveStartDate);
      const end = new Date(leaveEndDate);
      const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;

      this.setData({ leaveDays: days });
    }
  },

  onSubmitLeave() {
    const { userInfo, leaveStartDate, leaveEndDate, isSubmitting, lastSubmitTime } = this.data;

    if (isSubmitting || Date.now() - lastSubmitTime < 3000) {
      utils.showToast('请勿重复提交', 'none', 1500);
      return;
    }

    if (!leaveStartDate || leaveStartDate === null || leaveStartDate === 'null') {
      utils.showToast('请选择请假开始日期', 'none', 2000);
      return;
    }

    if (!leaveEndDate || leaveEndDate === null || leaveEndDate === 'null') {
      utils.showToast('请选择请假结束日期', 'none', 2000);
      return;
    }

    const startDate = new Date(leaveStartDate);
    const endDate = new Date(leaveEndDate);

    if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) {
      utils.showToast('请假日期格式错误', 'none', 2000);
      return;
    }

    if (startDate > endDate) {
      utils.showToast('结束日期不能早于开始日期', 'none', 2000);
      return;
    }

    this.setData({
      isSubmitting: true,
      lastSubmitTime: Date.now()
    });

    api.student.applyLeave(userInfo, leaveStartDate, leaveEndDate)
      .then(res => {
        if (res.success) {
          utils.showToast('请假申请提交成功', 'success', 2000);
          setTimeout(() => {
            utils.navigateBack();
          }, 2000);
        } else {
          utils.showToast(res.message || '请假申请失败', 'none', 2000);
        }
      })
      .catch(err => {
        console.error('请假申请失败:', err);
        utils.showToast('网络错误，请假申请失败', 'none', 2000);
      })
      .finally(() => {
        this.setData({ isSubmitting: false });
      });
  }
});
