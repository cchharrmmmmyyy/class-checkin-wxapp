# 班级考勤系统 API 文档

## 概述

- **Base URL**: `http://{host}:{port}/api`
- **认证方式**: JWT Bearer Token（`Authorization: Bearer <token>`），管理后台同时支持从 Cookie 读取 Token
- **响应格式**: 统一 JSON 信封

```json
{
  "code": 200,
  "message": "success",
  "data": { }
}
```

- **分页响应格式**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "size": 20,
    "total_pages": 5
  }
}
```

- **角色说明**:
  | 角色 | 说明 |
  |------|------|
  | `student` | 学生，可打卡、请假、补卡 |
  | `monitor` | 班委，学生权限 + 班级考勤概况 |
  | `teacher` | 教师，管理班级、审批请假/补卡、任命班委 |
  | `admin` | 管理员，全部后台管理功能（Web 端） |

---

## 1. 认证

### 1.1 登录

> **POST** `/api/login`

**请求体** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 学号/工号，长度 6-12 |
| password | string | 是 | 密码，长度 6-20 |

**说明**: 请求头 `X-Client-Type` 为 `miniprogram` 表示小程序登录，否则视为 Web 端登录（仅允许 `admin` 角色，并设置 Cookie）。

**成功响应**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "eyJhbGciOi...",
    "user": {
      "user_id": "2021001",
      "username": "张三",
      "role": "student",
      "class": "计算机2101"
    }
  }
}
```

**错误码**:

| code | 说明 |
|------|------|
| 1001 | 学号/工号和密码不能为空 |
| 1002 | 学号/工号或密码错误 |
| 1003 | 无管理员权限（Web 端非 admin 登录） |

---

### 1.2 修改密码

> **POST** `/api/change-password`

**权限**: 所有已登录用户

**请求体** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | 是 | 原密码 |
| new_password | string | 是 | 新密码 |

**成功响应**:

```json
{
  "code": 200,
  "message": "success",
  "data": { "success": true, "message": "密码修改成功" }
}
```

---

## 2. 学生端

> 前缀 `/api/student` | 权限: `student` / `monitor`

### 2.1 打卡

> **POST** `/api/student/punch`

**请求体** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| latitude | number | 是 | 纬度 |
| longitude | number | 是 | 经度 |

**成功响应**:

```json
{
  "code": 200,
  "message": "success",
  "data": { "id": 1, "user_id": "2021001", "punch_date": "2026-05-10", "punch_time": "08:30:00" }
}
```

---

### 2.2 获取打卡记录

> **GET** `/api/student/punch-records`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| start_date | string | 否 | - | 开始日期 (YYYY-MM-DD) |
| end_date | string | 否 | - | 结束日期 (YYYY-MM-DD) |
| page | int | 否 | 1 | 页码 |
| size | int | 否 | 50 | 每页条数 |

**成功响应**: 分页格式，`items` 中每项结构：

```json
{
  "id": 1,
  "user_id": "2021001",
  "punch_date": "2026-05-10",
  "punch_time": "08:30:00",
  "latitude": 30.123,
  "longitude": 120.456,
  "is_makeup": false
}
```

---

### 2.3 申请请假

> **POST** `/api/student/leave/apply`

**请求体** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start_date | string | 是 | 开始日期 (YYYY-MM-DD) |
| end_date | string | 是 | 结束日期 (YYYY-MM-DD) |
| leave_type | string | 否 | 请假类型，默认 `personal` |
| reason | string | 否 | 请假原因 |

**成功响应**:

```json
{
  "code": 200,
  "message": "success",
  "data": { "id": 1, "user_id": "2021001", "leave_status": "pending" }
}
```

---

### 2.4 获取请假记录

> **GET** `/api/student/leave/records`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| status | string | 否 | - | 按状态筛选 (`pending` / `approved` / `rejected`) |
| page | int | 否 | 1 | 页码 |
| size | int | 否 | 50 | 每页条数 |

**成功响应**: 分页格式，`items` 中每项结构：

```json
{
  "id": 1,
  "user_id": "2021001",
  "leave_start_date": "2026-05-12",
  "leave_end_date": "2026-05-13",
  "leave_type": "sick",
  "leave_reason": "感冒发烧",
  "leave_status": "pending",
  "created_at": "2026-05-10T08:30:00"
}
```

---

### 2.5 申请补卡

> **POST** `/api/student/makeup/apply`

**请求体** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| target_date | string | 是 | 需要补卡的日期 (YYYY-MM-DD) |
| reason | string | 否 | 补卡原因 |

**成功响应**:

```json
{
  "code": 200,
  "message": "success",
  "data": { "id": 1, "user_id": "2021001", "status": "pending" }
}
```

---

### 2.6 获取补卡记录

> **GET** `/api/student/makeup/records`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | int | 否 | 1 | 页码 |
| size | int | 否 | 50 | 每页条数 |

**成功响应**: 分页格式，`items` 中每项结构：

```json
{
  "id": 1,
  "user_id": "2021001",
  "target_date": "2026-05-09",
  "reason": "忘记打卡",
  "status": "approved",
  "created_at": "2026-05-10T08:30:00"
}
```

---

### 2.7 班级打卡概况（班委）

> **GET** `/api/student/monitor/class-punch-status`

**权限**: `monitor`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| date | string | 否 | 当天 | 查询日期 (YYYY-MM-DD) |

**成功响应**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "class_name": "计算机2101",
    "date": "2026-05-10",
    "total_students": 30,
    "present": 25,
    "leave": 2,
    "absent": 3,
    "attendance_rate": 0.9,
    "details": [
      { "user_id": "2021001", "username": "张三", "real_name": "张三", "status": "present", "punch_time": "08:30:00" },
      { "user_id": "2021002", "username": "李四", "real_name": "李四", "status": "absent" }
    ]
  }
}
```

---

### 2.8 班级请假概况（班委）

> **GET** `/api/student/monitor/class-leaves`

**权限**: `monitor`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | int | 否 | 1 | 页码 |
| size | int | 否 | 50 | 每页条数 |

**成功响应**: 分页格式，提供班级内所有待审批请假申请。

---

### 2.9 班级补卡概况（班委）

> **GET** `/api/student/monitor/class-makeups`

**权限**: `monitor`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | int | 否 | 1 | 页码 |
| size | int | 否 | 50 | 每页条数 |

**成功响应**: 分页格式，提供班级内所有待审批补卡申请。

---

## 3. 教师端

> 前缀 `/api/teacher` | 权限: `teacher`

### 3.1 获取所教班级列表

> **GET** `/api/teacher/classes`

**成功响应**:

```json
{
  "code": 200,
  "message": "success",
  "data": [
    { "class_name": "计算机2101", "grade_id": 1, "student_count": 30 },
    { "class_name": "计算机2102", "grade_id": 1, "student_count": 28 }
  ]
}
```

---

### 3.2 获取班级学生列表

> **GET** `/api/teacher/class/students`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| class_name | string | 否 | 教师所属班级 | 班级名称 |
| page | int | 否 | 1 | 页码 |
| size | int | 否 | 50 | 每页条数 |

**成功响应**: 分页格式，每项含学生信息（user_id, username, real_name, role 等）。

---

### 3.3 获取班级打卡汇总

> **GET** `/api/teacher/class/punch-summary`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| class_name | string | 否 | 教师所属班级 | 班级名称 |
| date | string | 否 | 当天 | 查询日期 (YYYY-MM-DD) |

**成功响应**: 与 [2.7 班级打卡概况](#27-班级打卡概况班委) 结构相同。

---

### 3.4 获取待审批请假列表

> **GET** `/api/teacher/leave/pending`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| class_name | string | 否 | 教师所属班级 | 班级名称 |
| page | int | 否 | 1 | 页码 |
| size | int | 否 | 50 | 每页条数 |

**成功响应**: 分页格式，`items` 中每项包含请假记录及申请人信息。

---

### 3.5 审批请假申请

> **POST** `/api/teacher/leave/approve`

**请求体** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| leave_id | int | 是 | 请假记录 ID |
| status | string | 是 | 审批结果：`approved` / `rejected` |

**成功响应**:

```json
{
  "code": 200,
  "message": "success",
  "data": { "success": true, "message": "请假申请已审批" }
}
```

---

### 3.6 获取待审批补卡列表

> **GET** `/api/teacher/makeup/pending`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| class_name | string | 否 | 教师所属班级 | 班级名称 |
| page | int | 否 | 1 | 页码 |
| size | int | 否 | 50 | 每页条数 |

**成功响应**: 分页格式，`items` 中每项包含补卡记录及申请人信息。

---

### 3.7 审批补卡申请

> **POST** `/api/teacher/makeup/approve`

**请求体** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| makeup_id | int | 是 | 补卡记录 ID |
| status | string | 是 | 审批结果：`approved` / `rejected` |
| punch_time | string | 通过时必填 | 补卡时间 (HH:MM:SS) |
| latitude | number | 通过时必填 | 纬度 |
| longitude | number | 通过时必填 | 经度 |

**成功响应**:

```json
{
  "code": 200,
  "message": "success",
  "data": { "success": true, "message": "补卡申请已审批" }
}
```

---

### 3.8 任命班委

> **POST** `/api/teacher/monitor/appoint`

**请求体** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| student_id | string | 是 | 学生学号 |

**成功响应**:

```json
{
  "code": 200,
  "message": "success",
  "data": { "success": true, "message": "班委任命成功" }
}
```

---

### 3.9 撤销班委

> **DELETE** `/api/teacher/monitor/remove`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| student_id | string | 是 | 学生学号（Query 参数） |

**成功响应**:

```json
{
  "code": 200,
  "message": "success",
  "data": { "success": true, "message": "班委已撤销" }
}
```

---

### 3.10 获取班级班委列表

> **GET** `/api/teacher/monitors`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| class_name | string | 否 | 教师所属班级 | 班级名称 |
| page | int | 否 | 1 | 页码 |
| size | int | 否 | 50 | 每页条数 |

**成功响应**: 分页格式，包含班委信息（user_id, username, real_name 等）。

---

## 4. 通用接口

> 前缀 `/api` | 权限: 所有已登录用户（操作日志额外要求 `admin` / `teacher`）

### 4.1 获取通知列表

> **GET** `/api/notifications`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| type | string | 否 | - | 通知类型：`SYSTEM`/`PUNCH`/`LEAVE`/`MAKEUP`/`APPROVAL`/`REMINDER`/`ANNOUNCEMENT` |
| unread_only | bool | 否 | false | 仅显示未读 |
| page | int | 否 | 1 | 页码 |
| size | int | 否 | 50 | 每页条数 |

**成功响应**: 分页格式，`items` 中每项结构：

```json
{
  "id": 1,
  "receiver_id": "2021001",
  "sender_id": null,
  "title": "请假审批结果",
  "content": "您的请假申请已通过",
  "type": "APPROVAL",
  "is_read": false,
  "related_id": "10",
  "created_at": "2026-05-10T08:30:00"
}
```

---

### 4.2 标记通知已读

> **POST** `/api/notifications/mark-read`

**请求体** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| notification_id | int | 是 | 通知 ID |

**成功响应**:

```json
{ "code": 200, "message": "success", "data": { "marked": true } }
```

---

### 4.3 获取未读通知数量

> **GET** `/api/notifications/unread-count`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| type | string | 否 | - | 通知类型（同上） |

**成功响应**:

```json
{ "code": 200, "message": "success", "data": { "count": 3 } }
```

---

### 4.4 获取操作日志

> **GET** `/api/operation-logs`

**权限**: `admin` / `teacher`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| target_type | string | 否 | - | 目标类型 |
| target_id | string | 否 | - | 目标 ID |
| operator_id | string | 否 | - | 操作人 ID |
| operation_type | string | 否 | - | 操作类型 |
| start_date | string | 否 | - | 开始日期 (YYYY-MM-DD) |
| end_date | string | 否 | - | 结束日期 (YYYY-MM-DD) |
| page | int | 否 | 1 | 页码 |
| size | int | 否 | 50 | 每页条数 |

**成功响应**: 分页格式，`items` 中每项结构：

```json
{
  "id": 1,
  "operator_id": "admin001",
  "operation_type": "CREATE",
  "target_type": "USER",
  "target_id": "2021001",
  "before_data": null,
  "after_data": "{...}",
  "ip_address": "127.0.0.1",
  "created_at": "2026-05-10T08:30:00"
}
```

---

## 5. 管理后台

> 前缀 `/api/admin` | 权限: `admin` | 支持 Cookie 认证 (`allow_cookie=True`)

### 5.1 用户管理

#### 5.1.1 获取用户列表

> **GET** `/api/admin/users`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| class_name | string | 否 | - | 按班级筛选 |
| role | string | 否 | - | 按角色筛选 |
| page | int | 否 | 1 | 页码 |
| size | int | 否 | 50 | 每页条数 |

**成功响应**: 分页格式，每项包含 user_id, username, real_name, role, class_name 等。

---

#### 5.1.2 创建用户

> **POST** `/api/admin/users`

**请求体** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| user_id | string | 是 | 学号/工号 |
| password | string | 是 | 密码 |
| role | string | 是 | 角色 |
| class | string | 是 | 班级名称 |
| real_name | string | 否 | 真实姓名 |
| student_id | string | 否 | 学生编号 |

**成功响应**:

```json
{ "code": 200, "message": "success", "data": { "success": true, "message": "用户创建成功", "user_id": "2021001" } }
```

---

#### 5.1.3 更新用户

> **PUT** `/api/admin/users/<user_id>`

**请求体** (JSON): 同创建用户，密码留空则不修改。

---

#### 5.1.4 删除用户

> **DELETE** `/api/admin/users/<user_id>`

**成功响应**:

```json
{ "code": 200, "message": "success", "data": { "success": true, "message": "用户删除成功" } }
```

---

#### 5.1.5 重置用户密码

> **POST** `/api/admin/users/reset-password`

**请求体** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 用户 ID |

**成功响应**:

```json
{ "code": 200, "message": "success", "data": { "success": true, "new_password": "abc123" } }
```

---

### 5.2 组织架构管理

#### 5.2.1 校区

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/org/campuses` | 列表（参数: `page`, `size`, `name`） |
| POST | `/api/admin/org/campuses` | 创建（body: `name`, `address`） |
| PUT | `/api/admin/org/campuses/<id>` | 更新（body: `name`, `address`） |
| DELETE | `/api/admin/org/campuses/<id>` | 删除 |

---

#### 5.2.2 院系

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/org/departments` | 列表（参数: `page`, `size`, `campus_id`, `name`） |
| POST | `/api/admin/org/departments` | 创建（body: `campus_id`, `name`, `code`） |
| PUT | `/api/admin/org/departments/<id>` | 更新（body: `campus_id`, `name`, `code`） |
| DELETE | `/api/admin/org/departments/<id>` | 删除 |

---

#### 5.2.3 专业

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/org/majors` | 列表（参数: `page`, `size`, `department_id`, `name`） |
| POST | `/api/admin/org/majors` | 创建（body: `department_id`, `name`, `code`） |
| PUT | `/api/admin/org/majors/<id>` | 更新（body: `department_id`, `name`, `code`） |
| DELETE | `/api/admin/org/majors/<id>` | 删除 |

---

#### 5.2.4 年级

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/org/grades` | 列表（参数: `page`, `size`, `major_id`, `year`） |
| POST | `/api/admin/org/grades` | 创建（body: `major_id`, `year`, `name`） |
| PUT | `/api/admin/org/grades/<id>` | 更新（body: `major_id`, `year`, `name`） |
| DELETE | `/api/admin/org/grades/<id>` | 删除 |

---

#### 5.2.5 班级

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/org/classes` | 列表（参数: `page`, `size`, `grade_id`, `class_name`, `include_deleted`） |
| POST | `/api/admin/org/classes` | 创建（body: `class_name`, `grade_id`） |
| PUT | `/api/admin/org/classes/<class_name>` | 更新（body: `class_name`(新名), `grade_id`） |
| DELETE | `/api/admin/org/classes/<class_name>` | 软删除 |

---

### 5.3 教学任务管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/teaching/assignments` | 列表（参数: `page`, `size`, `class_name`, `teacher_id`, `semester`, `include_deleted`） |
| POST | `/api/admin/teaching/assignments` | 创建（body: `class_name`, `teacher_id`, `semester`） |
| PUT | `/api/admin/teaching/assignments` | 更新（body: `class_name`, `teacher_id`, `semester`） |
| DELETE | `/api/admin/teaching/assignments` | 删除（参数: `class_name`, `teacher_id`） |

---

### 5.4 打卡规则管理

#### 5.4.1 时间段

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/rules/time-slots` | 列表（参数: `page`, `size`, `name`, `enabled`, `include_deleted`） |
| POST | `/api/admin/rules/time-slots` | 创建（body: `name`, `start_time`, `end_time`, `enabled`） |
| PUT | `/api/admin/rules/time-slots/<id>` | 更新（body: `name`, `start_time`, `end_time`, `enabled`） |
| DELETE | `/api/admin/rules/time-slots/<id>` | 软删除 |

---

#### 5.4.2 打卡围栏

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/rules/punch-geofences` | 列表（参数: `page`, `size`, `name`, `enabled`, `fence_type`, `include_deleted`） |
| POST | `/api/admin/rules/punch-geofences` | 创建（body: `name`, `fence_type`, `latitude`, `longitude`, `radius`, `polygon_coords`, `enabled`） |
| PUT | `/api/admin/rules/punch-geofences/<id>` | 更新（body 同上） |
| DELETE | `/api/admin/rules/punch-geofences/<id>` | 软删除 |

围栏类型 `fence_type`: `circle`（圆形，需 latitude/longitude/radius）或 `polygon`（多边形，需 polygon_coords）。

---

#### 5.4.3 打卡规则

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/admin/rules/punch-rules` | 列表（参数: `page`, `size`, `enabled`, `time_slot_id`, `geofence_id`, `include_deleted`） |
| POST | `/api/admin/rules/punch-rules` | 创建（body: `time_slot_id`, `geofence_id`, `priority`, `time_enabled`, `location_enabled`, `enabled`） |
| PUT | `/api/admin/rules/punch-rules/<id>` | 更新（body 同上） |
| DELETE | `/api/admin/rules/punch-rules/<id>` | 软删除 |

规则将时间段与围栏绑定，`time_enabled` 与 `location_enabled` 分别控制是否校验时间/位置。

---

### 5.5 考勤管理

#### 5.5.1 获取考勤记录（综合查询）

> **GET** `/api/admin/attendance-records`

同时返回打卡和请假记录，按日期排序。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 否 | 按用户名模糊搜索 |
| user_id | string | 否 | 按用户 ID 精确筛选 |
| start_date | string | 否 | 开始日期 (YYYY-MM-DD) |
| end_date | string | 否 | 结束日期 (YYYY-MM-DD) |
| leave_status | string | 否 | 按请假状态筛选 |
| page | int | 否 | 页码（默认 1） |
| size | int | 否 | 每页条数（默认 10） |

**成功响应**: 分页格式，每项结构：

```json
{
  "id": 1,
  "username": "张三",
  "user_id": "2021001",
  "punch_date": "2026-05-10",
  "leave_start_date": null,
  "leave_end_date": null,
  "leave_status": null
}
```

---

#### 5.5.2 导出考勤 CSV

> **GET** `/api/admin/attendance/csv`

参数同 5.5.1（不含分页）。返回 CSV 文件下载（UTF-8 BOM 编码，Excel 兼容）。

---

#### 5.5.3 打卡记录 CRUD

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/attendance/punch-records` | 新增打卡记录 |
| PUT | `/api/admin/attendance/punch-records/<id>` | 编辑打卡记录 |
| DELETE | `/api/admin/attendance/punch-records/<id>` | 删除打卡记录 |

**请求体** (POST/PUT):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 用户 ID |
| punch_date | string | 是 | 打卡日期 (YYYY-MM-DD) |
| punch_time | string | 是 | 打卡时间 (HH:MM:SS) |
| latitude | number | 是 | 纬度 |
| longitude | number | 是 | 经度 |

---

#### 5.5.4 请假记录 CRUD

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/attendance/leave-records` | 新增请假记录 |
| PUT | `/api/admin/attendance/leave-records/<id>` | 编辑请假记录（仅修改状态） |
| DELETE | `/api/admin/attendance/leave-records/<id>` | 删除请假记录 |

**请求体** (POST):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 用户 ID |
| leave_start_date | string | 是 | 开始日期 (YYYY-MM-DD) |
| leave_end_date | string | 是 | 结束日期 (YYYY-MM-DD) |
| leave_status | string | 是 | 状态 (`pending`/`approved`/`rejected`) |
| leave_type | string | 是 | 请假类型 |
| leave_reason | string | 否 | 请假原因 |

**请求体** (PUT):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| leave_status | string | 是 | 状态 (`pending`/`approved`/`rejected`) |

---

### 5.6 仪表盘

#### 5.6.1 仪表盘统计

> **GET** `/api/admin/dashboard/stats`

**成功响应**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_students": 120,
    "present_today": 100,
    "on_leave_today": 5,
    "absent_today": 15,
    "pending_leaves": 3,
    "geofence": {
      "id": 1,
      "name": "教学楼A",
      "latitude": 30.123,
      "longitude": 120.456,
      "radius": 200,
      "enabled": 1
    }
  }
}
```

---

#### 5.6.2 考勤趋势

> **GET** `/api/admin/dashboard/trend`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| class_name | string | 否 | - | 班级名称（不传则为全校） |
| days | int | 否 | 7 | 最近天数 |

**成功响应**:

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "class_name": null,
    "start_date": "2026-05-04",
    "end_date": "2026-05-10",
    "days": 7,
    "daily_data": [
      { "date": "2026-05-10", "present_count": 100, "leave_count": 5, "absent_count": 15, "attendance_rate": 0.875 }
    ]
  }
}
```

---

### 5.7 系统配置

#### 5.7.1 获取打卡配置

> **GET** `/api/admin/config`

**成功响应**:

```json
{
  "code": 200,
  "message": "success",
  "data": { "punch_mode": "time_and_location", "allow_makeup": true, "makeup_days": 3 }
}
```

---

#### 5.7.2 更新打卡配置

> **PUT** `/api/admin/config`

**请求体** (JSON): 配置项键值对（如 `punch_mode`, `allow_makeup`, `makeup_days` 等）。

**成功响应**:

```json
{ "code": 200, "message": "success", "data": { "success": true } }
```

---

## 附录 A: 通用错误码

| code | HTTP 状态 | 说明 |
|------|-----------|------|
| 200 | 200 | 成功 |
| 400 | 400 | 请求参数错误 |
| 401 | 401 | 未认证（Token 缺失/无效/过期） |
| 403 | 403 | 权限不足 |
| 404 | 404 | 资源不存在 |
| 1001 | 400 | 凭证缺失 |
| 1002 | 401 | 凭证无效 |
| 1003 | 403 | Web 端非管理员登录 |
| 6001 | 400 | JSON 格式无效 |
| 6002 | 404 | 用户不存在 |
| 7001 | 400 | 用户信息不完整 |
| 7002 | 404 | 班级不存在 |
| 7003 | 400 | 校区名称不能为空 |
| 7004 | 404 | 校区不存在 |

---

## 附录 B: 认证头传递方式

| 客户端 | 方式 |
|------|------|
| 微信小程序 | `Authorization: Bearer <token>` |
| Web 管理后台 | `Authorization: Bearer <token>` 或 Cookie (`token=<token>`) |
| 调试 | 可在 Query 中传 `?token=<token>` |
