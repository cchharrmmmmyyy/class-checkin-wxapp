# utils/ — 工具模块

横切关注点，被 routes、services、dao 各层共用。每个文件提供独立的功能领域。

## 文件说明

### `__init__.py`
导出 `ServiceException` 供其他模块方便引用。

### `exceptions.py`
**自定义业务异常** — 提供 `ServiceException` 类。

属性：
- `message` — 错误描述文本
- `code` — 业务错误码（整数）
- `http_status` — HTTP 状态码

用法：Service 或 DAO 层遇到业务错误时 `raise ServiceException("原因", code=400, http_status=400)`。`app.py` 中注册了全局异常处理器自动将其转为统一 JSON 响应。

### `db.py`
**数据库工具** — 封装所有 SQLite 操作。

函数：
- `get_connection()` — 获取数据库连接（`Row` 工厂模式，返回字典式行）
- `hash_password(password)` — bcrypt 哈希密码
- `verify_password(password, stored_hash)` — 验证密码
- `execute_query(sql, params)` — 执行查询，返回列表
- `execute_query_one(sql, params)` — 执行查询，返回单行
- `execute_update(sql, params)` — 执行写操作（INSERT/UPDATE/DELETE），返回影响行数

### `auth.py`
**认证工具** — JWT Token 管理与装饰器。

- `generate_token(user_id, username, role, user_class)` — 生成 HS256 签名的 JWT
- `decode_token(token)` — 解码并验证 Token
- `token_required` — Flask 装饰器，从 `Authorization` 头提取 Bearer Token 并注入 `g.current_user`
- `role_required(allowed_roles)` — Flask 装饰器，校验用户角色是否在允许列表内，需配合 `token_required` 使用
- `web_token_required` — 增强版装饰器，同时检查 Header 和 Cookie（`adminToken`），用于管理后台页面鉴权

### `api_response.py`
**统一响应格式** — 确保所有 API 返回格式一致。

函数：
- `success(data, message, code=0, http_status=200)` — 成功响应
- `error(message, code=-1, http_status=400, data=None)` — 错误响应

响应格式：`{ "code": 0, "message": "ok", "data": {...} }`

- `mark_legacy_route(response)` — 给响应添加 `Deprecation` 和 `Sunset` 头（兼容层使用）

### `geo.py`
**地理位置计算** — 提供 `calculate_distance(lat1, lon1, lat2, lon2)` 函数。

使用 Haversine 公式计算两 GPS 坐标间的地表距离，返回米。用于打卡时判断用户位置是否在围栏有效范围内。
