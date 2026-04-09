const BASE_URL = 'http://localhost:5000/api';

const request = (url, method, data) => {
  const token = wx.getStorageSync('token');
  return new Promise((resolve, reject) => {
    wx.request({
      url: BASE_URL + url,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success(res) {
        if (res.statusCode === 200) {
          if (res.data.code === 200) {
            resolve(res.data.data);
          } else {
            wx.showToast({
              title: res.data.message || '请求失败',
              icon: 'none',
              duration: 2000
            });
            const error = new Error(res.data.message || '请求失败');
            error.code = res.data.code;
            reject(error);
          }
        } else {
          wx.showToast({
            title: res.data?.message || `请求失败 (${res.statusCode})`,
            icon: 'none',
            duration: 2000
          });
          const error = new Error(res.data?.message || '请求失败');
          error.code = res.data?.code || res.statusCode;
          reject(error);
        }
      },
      fail(err) {
        wx.showToast({
          title: '网络异常，请检查网络连接',
          icon: 'none'
        });
        reject(err);
      }
    });
  });
};

module.exports = { request };