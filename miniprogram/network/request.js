const { baseUrl, timeout } = require('../config/api.js');

const TOAST_MAX_LEN = 18;

const trimToastTitle = (title) => {
  if (!title) return '请求失败';
  return String(title).slice(0, TOAST_MAX_LEN);
};

const appendQuery = (url, params) => {
  if (!params || typeof params !== 'object') return url;
  const query = Object.keys(params)
    .filter((key) => params[key] !== undefined && params[key] !== null && params[key] !== '')
    .map((key) => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    .join('&');

  if (!query) return url;
  return `${url}${url.includes('?') ? '&' : '?'}${query}`;
};

const buildAppError = (message, extra = {}) => {
  const error = new Error(message || '请求失败');
  error.code = extra.code;
  error.httpStatus = extra.httpStatus;
  error.traceId = extra.traceId;
  error.data = extra.data;
  return error;
};

const isUnifiedEnvelope = (body) => (
  !!body
  && typeof body === 'object'
  && Object.prototype.hasOwnProperty.call(body, 'code')
  && Object.prototype.hasOwnProperty.call(body, 'message')
  && Object.prototype.hasOwnProperty.call(body, 'data')
);

const maybeToast = (message, showError) => {
  if (!showError) return;
  wx.showToast({
    title: trimToastTitle(message),
    icon: 'none',
    duration: 2000
  });
};

const requestCore = (path, method = 'GET', data = {}, options = {}) => {
  const token = wx.getStorageSync('token');
  const httpMethod = String(method || 'GET').toUpperCase();
  const shouldQuery = httpMethod === 'GET' || httpMethod === 'DELETE';
  const showError = options.showError !== false;
  const finalUrl = appendQuery(`${baseUrl}${path}`, shouldQuery ? data : null);

  return new Promise((resolve, reject) => {
    wx.request({
      url: finalUrl,
      method: httpMethod,
      timeout: timeout || 10000,
      data: shouldQuery ? undefined : data,
      header: {
        'Content-Type': 'application/json',
        'X-Client-Type': 'miniprogram',
        Authorization: token ? `Bearer ${token}` : '',
        ...(options.headers || {})
      },
      success(res) {
        const body = res.data || {};
        const statusCode = res.statusCode;
        const traceId = body.trace_id || res.header?.['x-trace-id'] || res.header?.['X-Trace-Id'];

        if (!isUnifiedEnvelope(body)) {
          const contractErrorMessage = '响应格式错误';
          maybeToast(contractErrorMessage, showError);
          reject(buildAppError(contractErrorMessage, {
            code: 'INVALID_RESPONSE_ENVELOPE',
            httpStatus: statusCode,
            traceId,
            data: body
          }));
          return;
        }

        if (body.code === 200) {
          resolve(body.data);
          return;
        }

        const errorMessage = body.message || `请求失败(${statusCode})`;
        maybeToast(errorMessage, showError);
        reject(buildAppError(errorMessage, {
          code: body.code,
          httpStatus: statusCode,
          traceId,
          data: body.data
        }));
      },
      fail(err) {
        maybeToast('网络异常，请检查网络连接', showError);
        reject(buildAppError('网络异常，请检查网络连接', {
          code: 'NETWORK_ERROR',
          data: err
        }));
      }
    });
  });
};

const request = (url, method, data, options) => requestCore(url, method, data, options);
request.get = (url, params = {}, options = {}) => requestCore(url, 'GET', params, options);
request.post = (url, payload = {}, options = {}) => requestCore(url, 'POST', payload, options);
request.put = (url, payload = {}, options = {}) => requestCore(url, 'PUT', payload, options);
request.delete = (url, params = {}, options = {}) => requestCore(url, 'DELETE', params, options);

module.exports = {
  request,
  get: request.get,
  post: request.post,
  put: request.put,
  delete: request.delete
};
