# 重构记录

## 2026-05-04 — app.py & config.py 代码审查修复

### config.py

| 行号 | 重构项 | 说明 |
|------|--------|------|
| 7-10 | `_required` 函数简化 | 合并 `None` 和空字符串两次判断为 `os.environ.get(key, '')` + `if not value` 一次判断 |
| 30-53 | 新增 `_optional` 系列函数 | 添加 `_optional`、`_optional_bool`、`_optional_int`，支持带默认值的可选配置项，为后续扩展预留 |

### app.py

| 行号 | 重构项 | 说明 |
|------|--------|------|
| 12 | 同步 SECRET_KEY 到 Flask 实例 | 新增 `app.secret_key = Config.SECRET_KEY`，避免将来使用 session/flash 时签名错误 |
| 31-33 | 异常信息安全 | 非 debug 模式下隐藏 `str(e)` 原始信息，仅返回通用提示，防止泄露数据库连接串等敏感内容 |
| 38-43 | `/admin` 路由角色校验 | 增加 `payload.get('role') == 'admin'` 检查，非管理员即使持有有效 token 也无法进入管理后台 |
| 51-54 | fallback 路由排除 API | `/api/` 前缀路径返回 JSON 404，不再将不存在的 API 请求误导向 `login.html` |
| 58 | 数据库初始化移至模块级 | `check_and_init_database()` 从 `if __name__` 移到模块级别，通过 WSGI 服务器导入时也能执行初始化 |
| — | 删除冗余 `index` 路由 | 原 `@app.route('/')` 与 fallback 功能重复，已移除，`/` 路径由 fallback 兜底处理 |

### dao/punch_dao.py

| 行号 | 重构项 | 说明 |
|------|--------|------|
| 3 | 引入 Config | 新增 `from config import Config` |
| 117-119 | `get_punches_by_user` 默认值 | `limit` 参数默认值从硬编码 `30` 改为 `None`，运行时读取 `Config.PUNCH_RECORDS_LIMIT`，使配置项真正生效 |
