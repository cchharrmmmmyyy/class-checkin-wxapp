Component({
  properties: {
    title: {
      type: String,
      value: '校园打卡'
    }
  },
  data: {
    statusBarHeight: 20
  },
  lifetimes: {
    attached() {
      const systemInfo = wx.getSystemInfoSync();
      this.setData({
        statusBarHeight: systemInfo.statusBarHeight || 20
      });
    }
  },
  methods: {
    onBack() {
      wx.navigateBack({
        fail: () => {
          wx.switchTab({
            url: '/pages/login/login'
          });
        }
      });
    },
    onLogout() {
      wx.removeStorageSync('token');
      wx.removeStorageSync('userInfo');
      wx.reLaunch({
        url: '/pages/login/login'
      });
    }
  }
});
