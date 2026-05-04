# Routes 层重构计划

> 审查日期：2026-05-04
> 状态：待执行

---

## 一、审查发现汇总

共发现 **12 类问题**，按严重度分级如下：

| 严重度 | 问题 | 涉及文件 |
|--------|------|---------|
| 🔴 P0 | 响应格式不统一 | 全部 6 个路由文件 |
| 🔴 P0 | 错误码体系混乱 | auth / student / teacher / admin / common |
| 🔴 P0 | admin.py 严重超限（986 行） | admin.py |
| 🟡 P1 | 业务逻辑泄漏到路由层 | student.py / admin.py |
| 🟡 P1 | auth.py 嵌套函数模式异常 | auth.py |
| 🟡 P1 | 参数校验不一致 | 多个文件 |
| 🟢 P2 | RESTful 路径不规范 | 多个文件 |
| 🟢 P2 | 导入风格不一致 | 多个文件 |
| 🟢 P2 | 未使用变量 | student.py |
| 🟢 P2 | 路由端点功能重复 | student.py vs common.py |
| 🟢 P2 | 错误响应缺少 data 字段 | 多个文件 |
| 🟢 P3 | HTTP 状态码不够语义化 | 全部路由文件 |

---

## 二、P0 重构项

### 2.1 统一响应格式

**现状：** 项目已有 `utils/api_response.py` 提供 `success()` / `error()` 函数，但仅 `compat.py` 正确使用，其余 5 个文件全部手动 `jsonify({'code': 200, 'message': 'success', 'data': result})`。

**目标：** 所有路由文件统一使用 `success()` / `error()` 返回响应。

**改动范围：**

| 文件 | 改动说明 |
|------|---------|
| auth.py | 3 个端点：`login` / `change_password` / `get_current_user` |
| student.py | 9 个端点：全部 |
| teacher.py | 9 个端点：全部 |
| admin.py | ~25 个端点：全部 |
| common.py | 4 个端点：全部 |

**示例：**

```python
# Before
return jsonify({'code': 200, 'message': 'success', 'data': result}), 200

# After
from utils.api_response import success
return success(result)

# Before（错误）
return jsonify({'code': 1000, 'message': '学号/工号和密码不能为空'}), 400

# After（错误）
from utils.api_response import error
return error('学号/工号和密码不能为空', 1000, 400)
```

---

### 2.2 建立统一错误码常量

**现状：** 错误码为散落的魔法数字，同类错误在不同文件中使用不同码值。

| 当前码 | 文件 | 含义 |
|--------|------|------|
| 1000 | auth.py | 学号/密码为空 |
| 1007 | auth.py | 原密码/新密码为空 |
| 4001 | student.py | 补卡日期/原因为空、班级信息不存在 |
| 4002 | teacher.py | 请假记录ID为空 |
| 4003 | teacher.py | 审批状态为空 |
| 4004 | teacher.py | 补卡记录ID为空 |
| 4005 | teacher.py | 审批状态为空（重复） |
| 4006 | teacher.py | 学生学号为空 |
| 4007 | teacher.py | 学生学号为空（重复） |
| 5000 | admin.py | 用户名/密码/角色/用户ID为空 |
| 8001 | common.py | 通知ID为空 |

**目标：** 在 `utils/` 下新建 `error_codes.py`，按业务领域定义错误码常量，所有路由文件引用常量。

**错误码规划：**

| 码段 | 领域 | 示例 |
|------|------|------|
| 1000–1099 | 通用参数校验 | `PARAM_MISSING=1001`, `PARAM_INVALID=1002` |
| 2000–2099 | 认证鉴权 | `TOKEN_MISSING=2001`, `TOKEN_EXPIRED=2002`, `ROLE_DENIED=2003` |
| 3000–3099 | 打卡签到 | `PUNCH_DUPLICATE=3001`, `PUNCH_OUT_OF_RANGE=3002` |
| 4000–4099 | 请假管理 | `LEAVE_NOT_FOUND=4001`, `LEAVE_STATUS_INVALID=4002` |
| 5000–5099 | 补签管理 | `MAKEUP_NOT_FOUND=5001`, `MAKEUP_DATE_INVALID=5002` |
| 6000–6099 | 用户管理 | `USER_NOT_FOUND=6001`, `USER_ID_EMPTY=6002` |
| 7000–7099 | 班级/组织 | `CLASS_NOT_FOUND=7001`, `CLASS_NAME_EMPTY=7002` |
| 8000–8099 | 通知 | `NOTIFICATION_NOT_FOUND=8001` |
| 9000–9099 | 管理后台 | `ADMIN_OPERATION_DENIED=9001` |

**文件结构：**

```
utils/error_codes.py    # 错误码常量定义
```

---

### 2.3 拆分 admin.py

**现状：** `admin.py` 共 986 行，混合 7 个业务领域。

**目标：** 按业务领域拆分为 7 个子模块，每个不超过 300 行。

**拆分方案：**

| 新文件 | URL 前缀 | 职责 | 预估行数 |
|--------|---------|------|---------|
| `admin_auth.py` | `/api/admin` | 管理员登录 | ~30 |
| `admin_user.py` | `/api/admin` | 用户 CRUD、重置密码 | ~120 |
| `admin_org.py` | `/api/admin` | 校区/院系/专业/年级/班级 CRUD | ~250 |
| `admin_teaching.py` | `/api/admin` | 教学安排 CRUD | ~80 |
| `admin_rule.py` | `/api/admin` | 时间段/围栏/打卡规则 CRUD | ~200 |
| `admin_attendance.py` | `/api/admin` | 考勤记录 CRUD、导出 | ~200 |
| `admin_dashboard.py` | `/api/admin` | 仪表盘统计、全局配置 | ~60 |

**`__init__.py` 更新：**

```python
from .admin_auth import admin_auth_bp
from .admin_user import admin_user_bp
from .admin_org import admin_org_bp
from .admin_teaching import admin_teaching_bp
from .admin_rule import admin_rule_bp
from .admin_attendance import admin_attendance_bp
from .admin_dashboard import admin_dashboard_bp
```

**`app.py` 注册蓝图更新：** 将原来的 `admin_bp` 替换为 7 个子蓝图。

**迁移策略：** 所有 URL 路径保持不变，仅拆分文件内部组织。

---

## 三、P1 重构项

### 3.1 修复 auth.py 嵌套函数模式

**现状：** `change_password` 和 `get_current_user` 使用嵌套函数包装 `token_required`。

**目标：** 改为与其他路由一致的装饰器直接叠加模式。

```python
# Before
@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    from utils.auth import token_required
    @token_required
    def _change_password():
        ...
    return _change_password()

# After
@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    ...
```

---

### 3.2 将业务逻辑从路由层移至 Service 层

**3.2.1 student.py 请假状态过滤**

将 `get_leave_records()` 中的状态过滤逻辑移至 `LeaveService.get_user_leave_records()`，增加 `status` 参数。

```python
# Before（路由层过滤）
result = LeaveService.get_user_leave_records(user_id, page=page, size=size)
if status and 'items' in result:
    result['items'] = [r for r in result['items'] if r.get('leave_status') == status]
    result['total'] = len(result['items'])

# After（Service 层过滤）
result = LeaveService.get_user_leave_records(user_id, status=status, page=page, size=size)
```

**3.2.2 admin.py CSV 导出状态映射**

将 `export_attendance()` 中的状态映射逻辑移至 `AdminService` 或新建 `ExportService`。

**3.2.3 admin.py `_parse_bool_arg` 工具函数**

移至 `utils/` 目录。

---

### 3.3 统一参数校验策略

**目标：** 所有路由端点的必填参数都进行非空校验，且校验方式一致。

**需补充校验的端点：**

| 文件 | 端点 | 缺失校验 |
|------|------|---------|
| student.py | `punch()` | latitude / longitude 非空、数字类型 |
| student.py | `apply_leave()` | start_date / end_date 非空、格式 |
| admin.py | `create_campus()` | name 非空 |
| admin.py | `create_department()` | name / campus_id 非空 |
| admin.py | `create_time_slot()` | start_time / end_time 非空 |

---

## 四、P2 重构项

### 4.1 RESTful 路径规范化

> ⚠️ 此项涉及前端适配，需与前端同步修改。建议在兼容层中保留旧路径，标记 `Deprecation` 头。

| 当前路径 | 建议改为 | 说明 |
|---------|---------|------|
| `POST /api/admin/login` | `POST /api/admin/sessions` | login 不是资源 |
| `POST /api/admin/users/reset-password` | `POST /api/admin/users/{id}/password-reset` | 资源嵌套动作 |
| `POST /api/student/leave/apply` | `POST /api/student/leaves` | apply 是动词 |
| `POST /api/student/makeup/apply` | `POST /api/student/makeups` | apply 是动词 |
| `POST /api/teacher/leave/approve` | `PATCH /api/teacher/leaves/{id}` | approve 是动词 |
| `POST /api/teacher/makeup/approve` | `PATCH /api/teacher/makeups/{id}` | approve 是动词 |
| `POST /api/teacher/monitor/appoint` | `POST /api/teacher/class-monitors` | appoint 是动词 |
| `DELETE /api/teacher/monitor/remove` | `DELETE /api/teacher/class-monitors/{id}` | remove 是动词 |
| `POST /api/notifications/mark-read` | `PATCH /api/notifications/{id}` | mark-read 是动词 |

---

### 4.2 统一导入风格

**规则：** 所有导入放在文件顶部，禁止函数内导入。

| 文件 | 需移至顶部的导入 |
|------|----------------|
| auth.py | `from utils.auth import token_required` |
| admin.py | `from services import AuthService` |
| teacher.py | `from services import StatisticsService` |
| teacher.py | `from datetime import date` |
| student.py | `from services import StatisticsService` |

---

### 4.3 清理未使用变量

| 文件 | 行 | 变量 | 处理 |
|------|----|------|------|
| student.py | 26 | `device_id` | 删除或传给 Service |
| student.py | 238 | `user_id` | 删除 |
| student.py | 267 | `user_id` | 删除 |

---

### 4.4 消除路由端点功能重复

`GET /api/student/notifications`（student.py）与 `GET /api/notifications`（common.py）功能重复。

**方案：** 删除 `student.py` 中的 `get_notifications()`，前端统一使用 `common.py` 的版本。如需限制角色，由前端控制入口可见性。

---

### 4.5 错误响应补全 data 字段

所有手动构造的错误响应改用 `error()` 函数后自动包含 `data` 字段（值为 `None`），此项随 2.1 一并完成。

---

## 五、P3 重构项

### 5.1 HTTP 状态码语义化

| 场景 | 当前 | 建议 |
|------|------|------|
| 创建资源成功 | 200 | 201 Created |
| 删除资源成功 | 200 | 204 No Content |
| 查询/更新成功 | 200 | 200 OK（不变） |

> ⚠️ 此项需前端配合适配，建议低优先级推进。

---

## 六、执行顺序

```
Phase 1 — 基础设施（不改动路由文件内容，只新增工具）
  ├── 新建 utils/error_codes.py
  └── 新建 utils/parse_args.py（_parse_bool_arg 迁入）

Phase 2 — P0 重构
  ├── 2.1 全部路由文件统一使用 success() / error()
  ├── 2.2 全部路由文件引用 error_codes 常量
  └── 2.3 拆分 admin.py → 7 个子模块

Phase 3 — P1 重构
  ├── 3.1 修复 auth.py 嵌套函数
  ├── 3.2 业务逻辑移至 Service 层
  └── 3.3 补充参数校验

Phase 4 — P2 重构
  ├── 4.1 RESTful 路径规范化（需前端配合）
  ├── 4.2 统一导入风格
  ├── 4.3 清理未使用变量
  ├── 4.4 消除重复端点
  └── 4.5 错误响应补全 data（随 2.1 完成）

Phase 5 — P3 重构
  └── 5.1 HTTP 状态码语义化（需前端配合）
```

---

## 七、兼容性说明

- Phase 1–3 不改变任何 URL 路径和请求/响应结构，前端无感知
- Phase 4 的 RESTful 路径变更需在兼容层保留旧路径，设置 `Deprecation` / `Sunset` 响应头
- Phase 5 的状态码变更需前端适配

---

## 八、验收标准

1. 所有路由文件使用 `success()` / `error()` 返回响应，无手动 `jsonify` 拼接
2. 所有错误码引用 `error_codes.py` 常量，无魔法数字
3. `admin.py` 拆分后每个子模块不超过 300 行
4. `auth.py` 无嵌套函数模式
5. 路由层无业务逻辑（过滤、映射、计算）
6. 所有必填参数有非空校验
7. 所有导入在文件顶部
8. 无未使用变量
9. 无功能重复端点
