/**
 * 工具函数库
 */

const utils = {
  /**
   * 显示提示信息
   */
  showToast(title, icon = 'none', duration = 2000) {
    wx.showToast({ title, icon, duration });
  },

  /**
   * 显示加载中
   */
  showLoading(title = '加载中...') {
    wx.showLoading({ title, mask: true });
  },

  /**
   * 隐藏加载中
   */
  hideLoading() {
    wx.hideLoading();
  },

  /**
   * 显示确认对话框
   */
  showModal(title, content) {
    return new Promise((resolve) => {
      wx.showModal({
        title,
        content,
        success: (res) => {
          resolve(res.confirm);
        },
        fail: () => {
          resolve(false);
        }
      });
    });
  },

  /**
   * 获取用户信息
   */
  getUserInfo() {
    return wx.getStorageSync('userInfo') || null;
  },

  /**
   * 保存用户信息
   */
  setUserInfo(userInfo) {
    wx.setStorageSync('userInfo', userInfo);
  },

  /**
   * 清除用户信息
   */
  clearUserInfo() {
    wx.removeStorageSync('userInfo');
  },

  /**
   * 获取本地存储数据
   */
  getStorage(key, defaultValue = null) {
    const value = wx.getStorageSync(key);
    return value !== '' ? value : defaultValue;
  },

  /**
   * 设置本地存储数据
   */
  setStorage(key, value) {
    wx.setStorageSync(key, value);
  },

  /**
   * 移除本地存储数据
   */
  removeStorage(key) {
    wx.removeStorageSync(key);
  },

  /**
   * 格式化日期
   */
  formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
    const d = date instanceof Date ? date : new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    const seconds = String(d.getSeconds()).padStart(2, '0');

    return format
      .replace('YYYY', year)
      .replace('MM', month)
      .replace('DD', day)
      .replace('HH', hours)
      .replace('mm', minutes)
      .replace('ss', seconds);
  },

  /**
   * 获取当前时间戳
   */
  getTimestamp() {
    return Date.now();
  },

  /**
   * 页面跳转
   */
  navigateTo(url) {
    wx.navigateTo({ url });
  },

  /**
   * 替换当前页面
   */
  redirectTo(url) {
    wx.redirectTo({ url });
  },

  /**
   * 切换到 tabBar 页面
   */
  switchTab(url) {
    wx.switchTab({ url });
  },

  /**
   * 返回上一页
   */
  navigateBack(delta = 1) {
    wx.navigateBack({ delta });
  },

  /**
   * 重新加载页面
   */
  reload() {
    const pages = getCurrentPages();
    const currentPage = pages[pages.length - 1];
    if (currentPage) {
      currentPage.onLoad(currentPage.options);
    }
  },

  /**
   * 防抖函数
   */
  debounce(fn, delay = 300) {
    let timer = null;
    return function (...args) {
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => {
        fn.apply(this, args);
      }, delay);
    };
  },

  /**
   * 节流函数
   */
  throttle(fn, delay = 300) {
    let last = 0;
    return function (...args) {
      const now = Date.now();
      if (now - last > delay) {
        last = now;
        fn.apply(this, args);
      }
    };
  },

  /**
   * 深拷贝
   */
  deepClone(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj.getTime());
    if (obj instanceof Array) return obj.map(item => this.deepClone(item));
    if (obj instanceof Object) {
      const clonedObj = {};
      for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
          clonedObj[key] = this.deepClone(obj[key]);
        }
      }
      return clonedObj;
    }
  },

  /**
   * 验证手机号
   */
  isValidPhone(phone) {
    return /^1[3-9]\d{9}$/.test(phone);
  },

  /**
   * 验证邮箱
   */
  isValidEmail(email) {
    return /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/.test(email);
  }
};

export default utils;
