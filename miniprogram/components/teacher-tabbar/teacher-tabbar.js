// components/teacher-tabbar/teacher-tabbar.js
Component({
  properties: {
    active: {
      type: Number,
      value: 0
    }
  },

  methods: {
    onSwitchTab(e) {
      const { url } = e.currentTarget.dataset;
      
      const pages = getCurrentPages();
      const currentPage = pages[pages.length - 1];
      const currentUrl = `/${currentPage.route}`;
      
      if (currentUrl === url) {
        return;
      }
      
      wx.redirectTo({
        url: url,
        fail: () => {
          wx.switchTab({
            url: url
          });
        }
      });
    }
  }
});
