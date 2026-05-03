# Backend 架构概览

## 目录结构

```
backend/
├── app.py                  # 应用入口
├── config.py               # 配置中心
├── routes/                 # 路由层（接口暴露）
├── services/               # 服务层（业务逻辑）
├── dao/                    # 数据访问层（数据库操作）
├── models/                 # 数据模型定义
├── db/                     # 数据库初始化 & 建表脚本
├── utils/                  # 工具模块（横切关注点）
├── templates/              # 后台管理前端页面
├── static/                 # 前端静态资源
└── .env / .env.example     # 环境变量
```

---

## 1. 入口与控制反转 — `app.py`

整个 Flask 应用的组装点。只做三件事：

- 加载配置
- 注册所有 Blueprint（路由）
- 注册全局异常处理和兜底路由

不包含任何业务逻辑。

关键设计决策：

- **SECRET_KEY 同步**：`app.secret_key = Config.SECRET_KEY`，确保 Flask 实例与 JWT 使用同一密钥，避免将来使用 session/flash 等功能时出现签名错误。
- **数据库初始化**：`check_and_init_database()` 在模块级别执行（而非仅在 `__main__` 中），确保通过 WSGI 服务器导入时也能完成初始化。
- **fallback 路由**：`/<path:path>` 仅对前端页面做 SPA 兜底，`/api/` 前缀的路径返回 JSON 404，不会将 API 请求误导向 HTML 页面。
- **admin 页面鉴权**：`/admin` 路由校验 token 中的 `role == 'admin'`，非管理员即使持有有效 token 也无法进入管理后台。
- **异常信息安全**：非 debug 模式下，全局异常处理器不返回 `str(e)` 原始信息，避免泄露数据库连接串、SQL 语句等敏感内容。

## 2. 配置中心 — `config.py`

从 `.env` 文件读取所有环境变量，通过 `Config` 类集中暴露。

配置项分为两类：

- **必填项**（`_required` / `_required_bool` / `_required_int`）：启动时即校验，缺失或为空直接抛出 `ValueError`，避免运行时意外。
- **可选项**（`_optional` / `_optional_bool` / `_optional_int`）：未配置时使用默认值，不阻断启动。适用于日志级别、CORS 域名等非核心配置。

当前配置项：

| 配置项 | 类型 | 必填 | 用途 |
|--------|------|------|------|
| `JWT_SECRET_KEY` | str | 是 | JWT 签名密钥，同时同步到 `app.secret_key` |
| `TOKEN_EXPIRE_HOURS` | int | 是 | Token 过期时间（小时） |
| `DATABASE_FILE` | str | 是 | SQLite 数据库文件路径 |
| `INSERT_TEST_DATA` | bool | 是 | 是否插入测试数据 |
| `FLASK_HOST` | str | 是 | 服务器监听地址 |
| `FLASK_PORT` | int | 是 | 服务器监听端口 |
| `FLASK_DEBUG` | bool | 是 | 调试模式（影响异常信息输出详细程度） |
| `RANDOM_PASSWORD_LENGTH` | int | 是 | 重置密码时随机密码长度 |
| `PUNCH_RECORDS_LIMIT` | int | 是 | 打卡记录查询默认条数，供 `PunchDAO.get_punches_by_user()` 使用 |

## 3. 路由层 — `routes/`

**职责：接收 HTTP 请求，校验参数，调用 Service，返回响应。**

按角色拆分，每个文件对应一类用户：

| 文件 | 对应角色 | 典型请求 |
|------|----------|----------|
| `auth.py` | 通用 | 登录、注册 |
| `student.py` | 学生 | 签到、请假、补签 |
| `teacher.py` | 教师 | 查看考勤、审批 |
| `admin.py` | 管理员 | 班级管理、用户管理 |
| `common.py` | 通用（需登录） | 个人信息、公共数据 |
| `compat.py` | 兼容层 | 旧版接口兼容（转换请求格式后转调新 Service） |

路由层 **不直接操作数据库**，只做参数校验和调用 Service。

## 4. 服务层 — `services/`

**职责：封装业务逻辑，编排 DAO 调用，处理事务边界。**

按业务领域拆分：

| 文件 | 领域 |
|------|------|
| `punch_service.py` | 签到打卡 |
| `leave_service.py` | 请假管理 |
| `makeup_service.py` | 补签管理 |
| `auth_service.py` | 认证鉴权 |
| `admin_service.py` | 管理后台 |
| `teacher_service.py` | 教师功能 |
| `notification_service.py` | 消息推送 |
| `statistics_service.py` | 统计汇总 |
| `config_service.py` | 配置管理 |
| `log_service.py` | 操作日志 |
| `monitor_service.py` | 系统监控 |

Service 是业务的核心，路由层不关心"怎么做"，Service 不关心"怎么暴露"。

## 5. 数据访问层 — `dao/`

**职责：封装所有 SQL 操作，每个 DAO 对应一张表。**

- `base_dao.py` — 抽象基类，提供通用的 CRUD 方法
- 其余文件各对应一张数据库表（如 `punch_dao.py` → `punches` 表）

DAO 只做数据库读写，不包含业务判断。

## 6. 数据模型 — `models/`

**职责：定义与数据库表映射的 Python 类（ORM 模型）。**

一个文件对应一张表，字段与数据库列一一对应。供 DAO 层和 Service 层使用，确保数据结构在系统内一致。

## 7. 数据库脚本 — `db/`

| 路径 | 作用 |
|------|------|
| `db/schema/` | 按编号顺序排列的建表 SQL（01~17），可顺序执行重建完整库表 |
| `db/init_db.py` | 初始化脚本：执行建表 + 可选的测试数据插入 |

## 8. 工具模块 — `utils/`

横切关注点，被各层共用：

| 文件 | 功能 |
|------|------|
| `api_response.py` | 统一 JSON 响应格式（`success()` / `error()`） |
| `auth.py` | JWT Token 生成与解析 |
| `db.py` | 数据库连接获取 |
| `exceptions.py` | 自定义业务异常 `ServiceException` |
| `geo.py` | 地理位置计算（打卡围栏判断） |

## 9. 前端资源 — `templates/` + `static/`

后台管理系统的 SSR 页面（Flask 直接渲染 `login.html` / `admin.html`），使用 Vue 3 + Element Plus 构建。微信小程序端不经过这里，直接调 API。

---

## 功能导航：改某个功能该去哪里看

自顶向下，按调用链路列出。从路由找入口，沿 Service → DAO → Model 追踪，最后到 SQL Schema。

### 登录 / 认证

| 层级 | 文件 |
|------|------|
| 路由 | `routes/auth.py` |
| 服务 | `services/auth_service.py` |
| DAO | `dao/user_dao.py` |
| 模型 | `models/user.py` |
| 工具 | `utils/auth.py`（JWT 生成/校验）、`utils/db.py`（密码哈希） |
| 建表 | `db/schema/06_users.sql` |

### 学生打卡签到

| 层级 | 文件 |
|------|------|
| 路由 | `routes/student.py` → `punch()` |
| 服务 | `services/punch_service.py` |
| DAO | `dao/punch_dao.py`、`dao/punch_geofence_dao.py`、`dao/punch_time_slot_dao.py`、`dao/leave_dao.py` |
| 模型 | `models/punch.py`、`models/punch_geofence.py`、`models/punch_time_slot.py` |
| 工具 | `utils/geo.py`（距离计算） |
| 配置 | `services/config_service.py` → `dao/punch_config_dao.py` |
| 建表 | `db/schema/08_punch_geofences.sql`、`09_punch_time_slots.sql`、`10_punch_rules.sql`、`11_punches.sql`、`14_punch_config.sql` |

### 学生请假

| 层级 | 文件 |
|------|------|
| 路由 | `routes/student.py` → `apply_leave()` / `get_leave_records()` |
| 服务 | `services/leave_service.py` |
| DAO | `dao/leave_dao.py` |
| 模型 | `models/leave.py` |
| 建表 | `db/schema/12_leaves.sql` |

### 学生补签

| 层级 | 文件 |
|------|------|
| 路由 | `routes/student.py` → `apply_makeup()` / `get_makeup_records()` |
| 服务 | `services/makeup_service.py` |
| DAO | `dao/makeup_request_dao.py`、`dao/punch_dao.py` |
| 模型 | `models/makeup_request.py` |
| 建表 | `db/schema/13_makeup_requests.sql` |

### 教师审批请假/补签

| 层级 | 文件 |
|------|------|
| 路由 | `routes/teacher.py` → `approve_leave()` / `approve_makeup()` |
| 服务 | `services/leave_service.py`（审批方法）、`services/makeup_service.py`（审批方法） |
| DAO | `dao/leave_dao.py`、`dao/makeup_request_dao.py` |

### 教师管理班级 / 班委

| 层级 | 文件 |
|------|------|
| 路由 | `routes/teacher.py` → `appoint_monitor()` / `remove_monitor()` / `get_class_students()` |
| 服务 | `services/teacher_service.py` |
| DAO | `dao/user_dao.py`、`dao/class_teacher_dao.py` |
| 模型 | `models/user.py`、`models/class_teacher.py` |
| 建表 | `db/schema/06_users.sql`、`07_class_teachers.sql` |

### 班委查看班级考勤

| 层级 | 文件 |
|------|------|
| 路由 | `routes/student.py` → 三个 `/monitor/` 端点 |
| 服务 | `services/monitor_service.py` |
| DAO | `dao/user_dao.py`、`dao/punch_dao.py`、`dao/leave_dao.py` |

### 管理后台 CRUD（组织架构 / 用户 / 打卡规则）

| 层级 | 文件 |
|------|------|
| 路由 | `routes/admin.py`（全部端点） |
| 服务 | `services/admin_service.py` |
| DAO | `dao/campus_dao.py`、`dao/department_dao.py`、`dao/major_dao.py`、`dao/grade_dao.py`、`dao/class_dao.py`、`dao/user_dao.py`、`dao/class_teacher_dao.py`、`dao/punch_geofence_dao.py`、`dao/punch_time_slot_dao.py`、`dao/punch_rule_dao.py` |
| 模型 | `models/` 下对应同名文件 |
| 建表 | `db/schema/01~10` |

### 管理员仪表盘 / 统计 / 导出

| 层级 | 文件 |
|------|------|
| 路由 | `routes/admin.py` → `dashboard_stats()` / `dashboard_trend()` / `export_attendance()` |
| 服务 | `services/statistics_service.py`、`services/admin_service.py`（导出相关） |
| DAO | `dao/punch_dao.py`、`dao/leave_dao.py`、`dao/user_dao.py` |

### 通知消息

| 层级 | 文件 |
|------|------|
| 路由 | `routes/common.py`（标记已读等）、各角色路由中也有通知端点 |
| 服务 | `services/notification_service.py` |
| DAO | `dao/notification_dao.py` |
| 模型 | `models/notification.py` |
| 建表 | `db/schema/16_notifications.sql` |

### 操作日志审计

| 层级 | 文件 |
|------|------|
| 路由 | `routes/common.py` → `get_operation_logs()` |
| 服务 | `services/log_service.py` |
| DAO | `dao/operation_log_dao.py` |
| 模型 | `models/operation_log.py` |
| 建表 | `db/schema/15_operation_logs.sql` |

### 旧版 API 兼容

| 层级 | 文件 |
|------|------|
| 路由 | `routes/compat.py`（转换格式后调新版 Service，2026-07-31 前移除） |

### 全局配置 / 异常 / 响应格式

| 关注点 | 文件 |
|--------|------|
| 应用组装 | `app.py` |
| 环境变量 | `config.py` |
| 统一 JSON 响应 | `utils/api_response.py` |
| 自定义异常 | `utils/exceptions.py` |
| JWT 与装饰器 | `utils/auth.py` |
| 数据库连接 | `utils/db.py` |
| 地理计算 | `utils/geo.py` |
| 数据库初始化 | `db/init_db.py` |

---

## 请求流转示意

```
微信小程序 / 浏览器
        │
        ▼
   ┌─────────┐
   │ routes/ │  参数校验、权限检查
   └────┬────┘
        ▼
   ┌──────────┐
   │ services/│  业务逻辑编排
   └────┬─────┘
        ▼
   ┌──────┐
   │ dao/ │  SQL 操作
   └──┬───┘
      ▼
   SQLite 数据库
```

核心原则：**上层依赖下层，下层不感知上层。** routes → services → dao → db，每层只与下一层打交道。
