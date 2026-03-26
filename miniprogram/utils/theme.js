/**
 * 主题管理器 - 换肤功能实现
 * 使用方法：
 * 1. 在 app.wxss 中引入 theme.wxss
 * 2. 在页面的 json 配置中引入 theme.wxss
 * 3. 调用 ThemeManager.setTheme('theme-blue') 切换主题
 */

const THEME_STORAGE_KEY = 'app_theme';
const THEME_LIST = [
  { id: 'default', name: '默认绿色', className: '' },
  { id: 'theme-blue', name: '蓝色海洋', className: 'theme-blue' },
  { id: 'theme-purple', name: '紫色浪漫', className: 'theme-purple' },
  { id: 'theme-red', name: '红色热情', className: 'theme-red' },
  { id: 'theme-dark', name: '暗夜模式', className: 'theme-dark' }
];

class ThemeManager {
  constructor() {
    this.currentTheme = 'default';
    this.listeners = [];
    this.init();
  }

  init() {
    const savedTheme = wx.getStorageSync(THEME_STORAGE_KEY);
    if (savedTheme) {
      this.currentTheme = savedTheme;
    }
    this.applyTheme(this.currentTheme);
  }

  getThemeList() {
    return THEME_LIST;
  }

  getCurrentTheme() {
    return this.currentTheme;
  }

  getCurrentThemeClass() {
    const theme = THEME_LIST.find(t => t.id === this.currentTheme);
    return theme ? theme.className : '';
  }

  setTheme(themeId) {
    if (!THEME_LIST.find(t => t.id === themeId)) {
      console.warn(`主题 ${themeId} 不存在`);
      return false;
    }

    this.currentTheme = themeId;
    wx.setStorageSync(THEME_STORAGE_KEY, themeId);
    this.applyTheme(themeId);
    this.notifyListeners(themeId);
    return true;
  }

  applyTheme(themeId) {
    const theme = THEME_LIST.find(t => t.id === themeId);
    const themeClass = theme ? theme.className : '';

    const pages = getCurrentPages();
    const currentPage = pages[pages.length - 1];

    if (currentPage) {
      const data = {};
      data['themeClass'] = themeClass;
      currentPage.setData(data);
    }

    if (typeof this.updateAppTheme === 'function') {
      this.updateAppTheme(themeClass);
    }
  }

  applyThemeToPage(page) {
    const theme = THEME_LIST.find(t => t.id === this.currentTheme);
    const themeClass = theme ? theme.className : '';
    
    if (page) {
      page.setData({ themeClass });
    }
  }

  onThemeChange(callback) {
    if (typeof callback === 'function') {
      this.listeners.push(callback);
    }
  }

  offThemeChange(callback) {
    const index = this.listeners.indexOf(callback);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }

  notifyListeners(themeId) {
    this.listeners.forEach(callback => {
      try {
        callback(themeId);
      } catch (e) {
        console.error('主题切换回调执行失败:', e);
      }
    });
  }

  showThemePicker() {
    return new Promise((resolve) => {
      const themeList = THEME_LIST.map(t => t.name);
      const currentIndex = THEME_LIST.findIndex(t => t.id === this.currentTheme);

      wx.showActionSheet({
        itemList: themeList,
        success: (res) => {
          const selectedTheme = THEME_LIST[res.tapIndex];
          this.setTheme(selectedTheme.id);
          resolve(selectedTheme);
        },
        fail: () => {
          resolve(null);
        }
      });
    });
  }
}

const themeManager = new ThemeManager();

export default themeManager;
export { ThemeManager, THEME_LIST };
