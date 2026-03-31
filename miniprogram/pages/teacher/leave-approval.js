// pages/teacher/leave-approval.js
import api from '../../network/api.js';
import utils from '../../utils/utils.js';

Page({
  data: {
    userInfo: {},
    selectedClass: '',
    classList: [],
    showClassPicker: false,
    leaveApplications: [],
    isLoading: false
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
      this.loadLeaveApplications();
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
            this.loadLeaveApplications();
          }
        }
      })
      .catch(err => {
        console.error('获取班级列表失败:', err);
      });
  },

  loadLeaveApplications() {
    if (!this.data.selectedClass) return;

    this.setData({ isLoading: true });

    api.teacher.getLeaveApplications(this.data.selectedClass)
      .then(res => {
        this.setData({ isLoading: false });
        if (res.success) {
          this.setData({ leaveApplications: res.data || [] });
        }
      })
      .catch(err => {
        this.setData({ isLoading: false });
        console.error('获取请假申请失败:', err);
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
    this.loadLeaveApplications();
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
          this.loadLeaveApplications();
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

  onPullDownRefresh() {
    this.loadLeaveApplications();
    wx.stopPullDownRefresh();
  }
});
