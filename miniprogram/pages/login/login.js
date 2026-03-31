// pages/login/login.js
import api from '../../network/api.js';
import utils from '../../utils/utils.js';

Page({
  data: {
    user_id: '',
    password: '',
    themeClass: ''
  },

  onLoad() {
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

  onUserIdInput(e) {
    this.setData({ user_id: e.detail.value });
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value });
  },

  async onLogin() {
    const { user_id, password } = this.data;

    if (!user_id.trim()) {
      utils.showToast('请输入学号/工号', 'none');
      return;
    }

    if (!password.trim()) {
      utils.showToast('请输入密码', 'none');
      return;
    }

    utils.showLoading('登录中...');

    try {
      const res = await api.auth.login(user_id, password);
      utils.hideLoading();

      if (res.success) {
        utils.showToast('登录成功', 'success');
        
        // 保存用户信息和token
        const userData = { ...res.user };
        if (res.token) {
          userData.token = res.token;
        }
        utils.setUserInfo(userData);

        if (res.redirect_url) {
          const role = res.user.role;
          let redirectUrl = '/pages/student/student';
          if (role === 'teacher') {
            redirectUrl = '/pages/teacher/teacher';
          }
          utils.redirectTo(redirectUrl);
        }
      } else {
        utils.showToast(res.message || '登录失败', 'none');
      }
    } catch (err) {
      utils.hideLoading();
      let errorMessage = '登录失败，请重试';

      if (err.statusCode) {
        switch (err.statusCode) {
          case 401:
            errorMessage = '学号/工号或密码错误';
            break;
          case 403:
            errorMessage = '账号被禁用，请联系管理员';
            break;
          case 500:
            errorMessage = '服务器内部错误，请稍后再试';
            break;
          default:
            errorMessage = `登录失败 (错误码: ${err.statusCode})`;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }

      utils.showToast(errorMessage, 'none', 3000);
      console.error('登录失败详情:', { error: err, user_id, timestamp: new Date().toISOString() });
    }
  },


});
