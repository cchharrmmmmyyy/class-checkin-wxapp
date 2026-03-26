import themeManager from './utils/theme.js';

App({
  onLaunch() {
    themeManager.init();
  },

  globalData: {
    userInfo: null
  },

  themeManager: themeManager
});
