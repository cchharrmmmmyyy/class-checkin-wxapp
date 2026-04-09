Component({
  properties: {
    current: {
      type: Number,
      value: 0
    }
  },

  data: {
    selected: 0,
    tabList: [
      {
        pagePath: '/pages/student/index/index',
        text: '首页',
        icon: 'home',
        selectedIcon: 'home-active'
      },
      {
        pagePath: '/pages/student/records/records',
        text: '记录',
        icon: 'records',
        selectedIcon: 'records-active'
      },
      {
        pagePath: '/pages/student/profile/profile',
        text: '我的',
        icon: 'profile',
        selectedIcon: 'profile-active'
      }
    ]
  },

  attached() {
    this.updateSelected();
  },

  methods: {
    updateSelected() {
      const app = getApp();
      const userInfo = app.globalData.userInfo;
      if (!userInfo) return;

      const currentPage = getCurrentPages();
      if (currentPage.length > 0) {
        const currentPath = currentPage[currentPage.length - 1].route;
        const index = this.data.tabList.findIndex(item => item.pagePath === `/${currentPath}`);
        if (index !== -1) {
          this.setData({ selected: index });
        }
      }
    },

    switchTab(e) {
      const index = e.currentTarget.dataset.index;
      const pagePath = this.data.tabList[index].pagePath;

      wx.switchTab({ url: pagePath });
    }
  }
});