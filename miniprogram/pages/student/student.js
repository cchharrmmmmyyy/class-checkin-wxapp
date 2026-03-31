// pages/student/student.js
import api from '../../network/api.js';
import utils from '../../utils/utils.js';

Page({
  data: {
    userInfo: {
      username: '学生',
      role: 'student',
      class: ''
    },
    lastPunchTime: '',
    themeClass: '',
    latitude: 39.908823,
    longitude: 116.397470,
    markers: [{
      id: 1,
      latitude: 39.908823,
      longitude: 116.397470,
      width: 30,
      height: 30
    }]
  },

  onLoad(options) {
    const userInfo = utils.getUserInfo();
    if (userInfo) {
      this.setData({ userInfo });
    }

    const lastPunchTime = utils.getStorage('lastPunchTime');
    if (lastPunchTime) {
      this.setData({ lastPunchTime });
    }

    const app = getApp();
    if (app.themeManager) {
      app.themeManager.applyThemeToPage(this);
      app.themeManager.onThemeChange((themeId) => {
        const theme = app.themeManager.getCurrentThemeClass();
        this.setData({ themeClass: theme });
      });
    }

    this.initLocation();
  },

  initLocation() {
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        this.setData({
          latitude: res.latitude,
          longitude: res.longitude,
          markers: [{
            id: 1,
            latitude: res.latitude,
            longitude: res.longitude,
            width: 30,
            height: 30
          }]
        });
        console.log('定位成功 - latitude:', res.latitude, 'longitude:', res.longitude);
      },
      fail: (err) => {
        console.log('定位失败', err);
        wx.showToast({
          title: '定位失败，请开启定位权限',
          icon: 'none'
        });
      }
    });
  },

  onUnload() {
    const app = getApp();
    if (app.themeManager) {
      app.themeManager.offThemeChange();
    }
  },

  async onPunchCard() {
    let location = null;
    try {
      location = await this.getLocation();
      console.log('定位信息 - latitude:', location.latitude, 'longitude:', location.longitude);
    } catch (err) {
      const errMsg = err.errMsg || '';
      if (errMsg.includes('auth deny') || errMsg.includes('permission') || errMsg.includes('authorize')) {
        wx.showModal({
          title: '提示',
          content: '需要授权定位权限才能打卡，请点击右上角"..."按钮开启定位权限',
          showCancel: false
        });
      } else if (errMsg.includes('fail')) {
        wx.showToast({
          title: '定位服务异常',
          icon: 'none'
        });
      }
    }

    const now = new Date();
    const punchTime = utils.formatDate(now, 'YYYY-MM-DD HH:mm:ss');

    api.student.punch(this.data.userInfo, location)
      .then(res => {
        if (res.success) {
          utils.showToast('打卡成功！', 'success', 2000);
          this.setData({ lastPunchTime: punchTime });
          utils.setStorage('lastPunchTime', punchTime);
        } else {
          utils.showToast(res.message || '打卡失败', 'none', 2000);
          if (res.message && res.message.includes('已打卡')) {
            this.setData({ lastPunchTime: punchTime });
            utils.setStorage('lastPunchTime', punchTime);
          }
        }
      })
      .catch(err => {
        const isAlreadyPunched = err.data && err.data.already_punched;
        const isOutOfRange = err.data && err.data.out_of_range;

        if (isOutOfRange) {
          utils.showToast(err.data.message || '不在打卡范围内', 'none', 2000);
        } else if (isAlreadyPunched || (err.message && err.message.includes('已打卡'))) {
          utils.showToast('今日已打卡', 'none', 2000);
        } else {
          utils.showToast('网络错误，打卡失败', 'none', 2000);
        }

        this.setData({ lastPunchTime: punchTime });
        utils.setStorage('lastPunchTime', punchTime);
      });
  },

  onGoToDetail() {
    utils.navigateTo('/pages/student/student-detail');
  },

  onLeaveApply() {
    utils.navigateTo('/pages/student/leave-apply');
  },

  onViewLeaveRecords() {
    utils.navigateTo('/pages/student/leave-records');
  },

  onChangeTheme() {
    const app = getApp();
    if (app.themeManager) {
      app.themeManager.showThemePicker();
    }
  },

  getLocation() {
    return new Promise((resolve, reject) => {
      wx.getLocation({
        type: 'gcj02',
        success(res) {
          resolve(res);
        },
        fail(err) {
          reject(err);
        }
      });
    });
  },

  async onShowLocation() {
    try {
      const location = await this.getLocation();
      const marker = {
        id: 1,
        latitude: location.latitude,
        longitude: location.longitude,
        width: 30,
        height: 30
      };
      this.setData({
        latitude: location.latitude,
        longitude: location.longitude,
        markers: [marker]
      });
      console.log('当前位置 - latitude:', location.latitude, 'longitude:', location.longitude);
    } catch (err) {
      const errMsg = err.errMsg || '';
      if (errMsg.includes('auth deny') || errMsg.includes('permission') || errMsg.includes('authorize')) {
        wx.showModal({
          title: '提示',
          content: '需要授权定位权限才能查看地图，请点击右上角"..."按钮开启定位权限',
          showCancel: false
        });
      } else {
        wx.showToast({
          title: '定位服务异常',
          icon: 'none'
        });
      }
    }
  }
});
