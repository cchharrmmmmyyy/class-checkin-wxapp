const test = require('node:test');
const assert = require('node:assert/strict');

const REQUEST_MODULE_PATH = './request.js';

const loadRequestModule = () => {
  delete require.cache[require.resolve(REQUEST_MODULE_PATH)];
  return require(REQUEST_MODULE_PATH);
};

const createWxMock = ({ response, fail, token = 'mock-token' }) => {
  const calls = {
    requestOptions: null,
    toasts: []
  };

  global.wx = {
    getStorageSync: () => token,
    showToast: (options) => {
      calls.toasts.push(options);
    },
    request: (options) => {
      calls.requestOptions = options;
      if (fail) {
        options.fail(fail);
        return;
      }
      options.success(response);
    }
  };

  return calls;
};

test('GET 请求按统一响应信封成功返回 data，并拼接 query/header', async () => {
  const calls = createWxMock({
    response: {
      statusCode: 200,
      data: {
        code: 200,
        message: 'ok',
        data: { list: [1, 2, 3] }
      },
      header: {}
    }
  });
  const { get } = loadRequestModule();

  const result = await get('/student/records', {
    class_id: 1,
    keyword: 'abc'
  });

  assert.deepEqual(result, { list: [1, 2, 3] });
  assert.ok(calls.requestOptions.url.includes('/student/records?'));
  assert.ok(calls.requestOptions.url.includes('class_id=1'));
  assert.ok(calls.requestOptions.url.includes('keyword=abc'));
  assert.equal(calls.requestOptions.header.Authorization, 'Bearer mock-token');
  assert.equal(calls.toasts.length, 0);
});

test('统一响应信封业务错误会 reject，并保留 code/traceId', async () => {
  createWxMock({
    response: {
      statusCode: 200,
      data: {
        code: 40301,
        message: '无权限',
        data: null,
        trace_id: 'trace-abc'
      },
      header: {}
    }
  });
  const { post } = loadRequestModule();

  await assert.rejects(
    post('/teacher/approve-leave', { id: 1 }),
    (error) => {
      assert.equal(error.message, '无权限');
      assert.equal(error.code, 40301);
      assert.equal(error.httpStatus, 200);
      assert.equal(error.traceId, 'trace-abc');
      return true;
    }
  );
});

test('历史 success 格式不再兼容，按契约错误处理', async () => {
  createWxMock({
    response: {
      statusCode: 200,
      data: {
        success: true,
        message: 'ok',
        data: { id: 1 }
      },
      header: {}
    }
  });
  const { get } = loadRequestModule();

  await assert.rejects(
    get('/student/profile'),
    (error) => {
      assert.equal(error.message, '响应格式错误');
      assert.equal(error.code, 'INVALID_RESPONSE_ENVELOPE');
      assert.equal(error.httpStatus, 200);
      return true;
    }
  );
});

test('2xx 非信封 body 不再透传，按契约错误处理', async () => {
  createWxMock({
    response: {
      statusCode: 201,
      data: {
        id: 1,
        name: 'raw-body'
      },
      header: {}
    }
  });
  const { post } = loadRequestModule();

  await assert.rejects(
    post('/admin/punch-location', { lat: 1 }),
    (error) => {
      assert.equal(error.message, '响应格式错误');
      assert.equal(error.code, 'INVALID_RESPONSE_ENVELOPE');
      assert.equal(error.httpStatus, 201);
      assert.deepEqual(error.data, { id: 1, name: 'raw-body' });
      return true;
    }
  );
});

test('网络失败返回 NETWORK_ERROR', async () => {
  createWxMock({
    fail: { errMsg: 'request:fail timeout' }
  });
  const { get } = loadRequestModule();

  await assert.rejects(
    get('/login'),
    (error) => {
      assert.equal(error.code, 'NETWORK_ERROR');
      assert.equal(error.message, '网络异常，请检查网络连接');
      return true;
    }
  );
});
