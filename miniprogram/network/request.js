/**
 * 统一网络请求封装
 * 特性：
 * - 统一错误处理
 * - 请求/响应拦截器
 * - 自动 token 注入
 * - 统一 Loading 控制
 * - 请求缓存支持
 */

import { baseUrl, timeout, API_ENDPOINTS } from '../config/api.js';

const requestCache = new Map();
const DEFAULT_LOADING = false;

class RequestManager {
  constructor() {
    this.loadingCount = 0;
  }

  showLoading(show = true) {
    if (show) {
      this.loadingCount++;
      if (this.loadingCount === 1) {
        wx.showLoading({ title: '加载中...', mask: true });
      }
    }
  }

  hideLoading(show = true) {
    if (show) {
      this.loadingCount--;
      if (this.loadingCount <= 0) {
        this.loadingCount = 0;
        wx.hideLoading();
      }
    }
  }

  getToken() {
    const userInfo = wx.getStorageSync('userInfo');
    return userInfo ? userInfo.token : '';
  }

  request(options) {
    const {
      url,
      method = 'GET',
      data = {},
      header = {},
      useLoading = DEFAULT_LOADING,
      useCache = false,
      cacheTime = 60000,
      retryCount = 0,
      retryMax = 2
    } = options;

    const fullUrl = url.startsWith('http') ? url : `${baseUrl}${url}`;
    const cacheKey = `${method}:${fullUrl}:${JSON.stringify(data)}`;

    if (useCache && requestCache.has(cacheKey)) {
      const cached = requestCache.get(cacheKey);
      if (Date.now() - cached.timestamp < cacheTime) {
        return Promise.resolve(cached.data);
      }
      requestCache.delete(cacheKey);
    }

    const authToken = this.getToken();
    const requestHeader = {
      'content-type': 'application/json',
      ...header
    };

    if (authToken) {
      requestHeader['Authorization'] = `Bearer ${authToken}`;
    }

    this.showLoading(useLoading);

    return new Promise((resolve, reject) => {
      wx.request({
        url: fullUrl,
        method,
        data,
        header: requestHeader,
        timeout: timeout,
        success: (res) => {
          this.hideLoading(useLoading);
          
          if (res.statusCode >= 200 && res.statusCode < 300) {
            if (useCache) {
              requestCache.set(cacheKey, {
                data: res.data,
                timestamp: Date.now()
              });
            }
            resolve(res.data);
          } else if (res.statusCode === 401) {
            this.handleUnauthorized();
            reject(this.createError(res, '未授权，请重新登录'));
          } else if (res.statusCode === 403) {
            reject(this.createError(res, '无权限访问'));
          } else if (res.statusCode >= 500) {
            reject(this.createError(res, '服务器错误，请稍后重试'));
          } else {
            const message = res.data && res.data.message ? res.data.message : `请求失败: ${res.statusCode}`;
            reject(this.createError(res, message));
          }
        },
        fail: (err) => {
          this.hideLoading(useLoading);
          
          if (retryCount < retryMax) {
            console.log(`请求失败，${retryCount + 1}秒后重试...`);
            setTimeout(() => {
              this.request({ ...options, retryCount: retryCount + 1 })
                .then(resolve)
                .catch(reject);
            }, 1000);
            return;
          }
          
          let errorMessage = '网络连接失败';
          if (err.errMsg) {
            if (err.errMsg.includes('timeout')) {
              errorMessage = '网络连接超时';
            } else if (err.errMsg.includes('no network')) {
              errorMessage = '请检查网络连接';
            }
          }
          reject(this.createError(err, errorMessage));
        }
      });
    });
  }

  createError(res, message) {
    const error = new Error(message);
    error.statusCode = res.statusCode;
    error.data = res.data;
    error.errMsg = res.errMsg;
    return error;
  }

  handleUnauthorized() {
    wx.removeStorageSync('userInfo');
    wx.showToast({
      title: '登录已过期，请重新登录',
      icon: 'none'
    });
    setTimeout(() => {
      wx.redirectTo({ url: '/pages/login/login' });
    }, 1500);
  }

  get(url, params = {}, options = {}) {
    let queryString = '';
    if (Object.keys(params).length > 0) {
      queryString = '?' + Object.entries(params)
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
        .join('&');
    }
    return this.request({
      url: url + queryString,
      method: 'GET',
      ...options
    });
  }

  post(url, data = {}, options = {}) {
    return this.request({
      url,
      method: 'POST',
      data,
      ...options
    });
  }

  put(url, data = {}, options = {}) {
    return this.request({
      url,
      method: 'PUT',
      data,
      ...options
    });
  }

  delete(url, data = {}, options = {}) {
    return this.request({
      url,
      method: 'DELETE',
      data,
      ...options
    });
  }
}

const requestManager = new RequestManager();

const request = {
  get: (url, params, options) => requestManager.get(url, params, options),
  post: (url, data, options) => requestManager.post(url, data, options),
  put: (url, data, options) => requestManager.put(url, data, options),
  delete: (url, data, options) => requestManager.delete(url, data, options),
  request: (options) => requestManager.request(options)
};

export default request;
export { requestManager };
