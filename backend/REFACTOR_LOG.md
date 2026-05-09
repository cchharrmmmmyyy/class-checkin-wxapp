# 重构记录

## 2026-05-09 — DAO 层全面重构：统一继承 BaseDAO + 消除重复代码

### 背景

代码审查发现 `dao/` 层存在 3 个 Critical 问题：
1. BaseDAO 泛型基类设计完善但**全部 16 个 DAO 均未继承**它，导致 ~400 行重复的连接管理代码
2. `makeup_request_dao.py` 存在 `create()` 重复定义 Bug（后定义覆盖前定义）
3. 7 个方法返回 raw `sqlite3.Row` 而非 Model 对象，破坏抽象

### 重构内容

#### 1. `base_dao.py` 增强

| 变更 | 说明 |
|------|------|
| 新增 `SAFE_ORDER_BY_PATTERN` | 正则校验原始 ORDER BY 字符串（`column ASC/DESC`），允许白名单之外的排序 |
| 新增 `_resolve_order_by()` | 统一解析：先查白名单，失败则走安全正则，都不匹配抛异常 |
| 新增 `delete()` | 自动路由：支持软删除的表调 `soft_delete()`，否则调 `hard_delete()` |
| 新增 `hard_delete()` | 物理删除方法（`DELETE FROM ... WHERE id = ?`） |
| 增强 `_row_to_model()` | 自动过滤 Model 不存在的列（通过 `dataclasses.fields()`），兼容视图查询 |
| 扩展 `ORDER_BY_WHITELIST` | 新增 `class_name_asc/desc`、`user_id_asc/desc`、`priority_asc/desc` 等 8 个条目 |

#### 2. 全部 16 个 DAO 重构为继承 BaseDAO

每个 DAO 文件减少 ~30 行模板代码，仅保留表特定的自定义方法。

| 文件 | 继承 BaseDAO | 消除的主要问题 |
|------|:---:|:---|
| `campus_dao.py` | `BaseDAO[Campus]` | 硬删除 + 模板代码消除 |
| `department_dao.py` | `BaseDAO[Department]` | 同上 |
| `major_dao.py` | `BaseDAO[Major]` | 同上 |
| `grade_dao.py` | `BaseDAO[Grade]` | 同上 |
| `class_dao.py` | `BaseDAO[Class]` | 复合主键 `class_name` |
| `class_teacher_dao.py` | `BaseDAO[ClassTeacher]` | 保留复合主键 `(class_name, teacher_id)` CRUD |
| `user_dao.py` | `BaseDAO[User]` | 移除密码哈希业务逻辑 |
| `punch_geofence_dao.py` | `BaseDAO[PunchGeofence]` | 移除 update 中的兜底默认值业务逻辑 |
| `punch_time_slot_dao.py` | `BaseDAO[PunchTimeSlot]` | ~80 行 → 2 行 |
| `punch_rule_dao.py` | `BaseDAO[PunchRule]` | 仅保留字段默认值 |
| `punch_dao.py` | `BaseDAO[Punch]` | 移除 Config 依赖、移除 `create_punch()` 重复方法 |
| `leave_dao.py` | `BaseDAO[Leave]` | 修复 raw Row 返回、移除 `create_leave_record()` 重复方法 |
| `makeup_request_dao.py` | `BaseDAO[MakeupRequest]` | **修复 `create()` 重复定义 Bug**、修复 raw Row 返回 |
| `notification_dao.py` | `BaseDAO[Notification]` | 保留外部事务连接支持 |
| `operation_log_dao.py` | `BaseDAO[OperationLog]` | 保留外部事务连接支持 |
| `punch_config_dao.py` | `BaseDAO[PunchConfig]` | `get_config()` 复用 `get_by_id(1)` |

#### 3. 服务层同步更新

同步更新 3 个 Service 文件以适配新的 DAO API：

| 文件 | 变更 |
|------|------|
| `services/leave_service.py` | `leave['status']` → `leave.status`（属性访问）；`create_leave_record()` → `create(dict)` |
| `services/punch_service.py` | `create_punch()` → `create(dict)`；`get_punches_by_user(limit=1)` 由调用方传参 |
| `services/makeup_service.py` | `create(user_id, date, reason)` → `create(dict)`；`get_connection()` → `_get_connection()`；属性访问 |

#### 4. 统计

| 指标 | 重构前 | 重构后 | 变化 |
|------|:---:|:---:|:---:|
| DAO 总代码行 | ~1350 行 | ~580 行 | **-57%** |
| 重复连接管理代码 | ~400 行 | ~80 行（仅自定义方法需要） | **-80%** |
| SQL 注入防护覆盖 | 0 个 DAO | 全部 16 个 DAO | **16×** |
| 事务支持统一度 | 仅 2 个 DAO | 统一 BaseDAO 提供 | **全部** |
| Bug 修复 | `makeup_request_dao.create()` 不可用、7 处 raw Row | 全部已修复 | **2 类 Bug** |

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
