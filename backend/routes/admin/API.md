# Admin API 接口文档

> Base URL: `/api/admin`
> 鉴权: 所有接口需 `Authorization: Bearer <token>`，角色为 `admin`

---

## 一、用户管理

### `GET /api/admin/users`

用户列表（分页、筛选）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| class_name | string | 否 | 班级名称 |
| role | string | 否 | 角色：student / teacher / monitor / admin |
| page | int | 否 | 页码，默认 1 |
| size | int | 否 | 每页条数，默认 50 |

```json
// 响应
{ "code": 200, "message": "success", "data": { "items": [...], "total": 14 } }
```

---

### `POST /api/admin/users`

创建用户。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 姓名 |
| user_id | string | 是 | 学号/工号，6-12 位 |
| password | string | 是 | 密码，6-20 位 |
| role | string | 是 | 角色：student / teacher / monitor / admin |
| class | string | 否 | 班级名称 |

---

### `PUT /api/admin/users/<user_id>`

编辑用户。参数同创建（`user_id` 来自路径）。

---

### `DELETE /api/admin/users/<user_id>`

删除用户（软删除）。

---

### `POST /api/admin/users/reset-password`

重置用户密码。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 学号/工号 |

```json
// 响应
{ "code": 200, "message": "success", "data": { "new_password": "abc123" } }
```

---

## 二、组织架构

### 校区 — `GET/POST /api/admin/org/campuses`

`GET`: 查询参数 `name`、`page`、`size`
`POST`: 请求体 `name`（必填）、`address`

### 校区 — `PUT/DELETE /api/admin/org/campuses/<campus_id>`

---

### 院系 — `GET/POST /api/admin/org/departments`

`GET`: 查询参数 `campus_id`、`name`、`page`、`size`
`POST`: 请求体 `campus_id`（必填）、`name`（必填）、`code`

### 院系 — `PUT/DELETE /api/admin/org/departments/<department_id>`

---

### 专业 — `GET/POST /api/admin/org/majors`

`GET`: 查询参数 `department_id`、`name`、`page`、`size`
`POST`: 请求体 `department_id`（必填）、`name`（必填）、`code`

### 专业 — `PUT/DELETE /api/admin/org/majors/<major_id>`

---

### 年级 — `GET/POST /api/admin/org/grades`

`GET`: 查询参数 `major_id`、`year`、`page`、`size`
`POST`: 请求体 `major_id`（必填）、`year`（必填）、`name`

### 年级 — `PUT/DELETE /api/admin/org/grades/<grade_id>`

---

### 班级 — `GET/POST /api/admin/org/classes`

`GET`: 查询参数 `grade_id`、`class_name`、`include_deleted`、`page`、`size`
`POST`: 请求体 `class_name`（必填）、`grade_id`（必填）

### 班级 — `PUT/DELETE /api/admin/org/classes/<class_name>`

---

## 三、教学安排

### `GET/POST /api/admin/teaching/assignments`

`GET`: 查询参数 `class_name`、`teacher_id`、`semester`、`include_deleted`、`page`、`size`
`POST`: 请求体 `class_name`（必填）、`teacher_id`（必填）、`semester`

### `PUT/DELETE /api/admin/teaching/assignments/<class_name>/<teacher_id>`

`PUT`: 请求体 `semester`

---

## 四、打卡规则

### 时间段 — `GET/POST /api/admin/rules/time-slots`

`GET`: 查询参数 `name`、`enabled`、`include_deleted`、`page`、`size`
`POST`: 请求体 `name`（必填）、`start_time`（必填，如 `08:00`）、`end_time`（必填）、`enabled`（默认 1）

### 时间段 — `PUT/DELETE /api/admin/rules/time-slots/<slot_id>`

---

### 围栏 — `GET/POST /api/admin/rules/punch-geofences`

`GET`: 查询参数 `name`、`enabled`、`fence_type`、`include_deleted`、`page`、`size`
`POST`: 请求体 `name`、`fence_type`（`circle` / `polygon`）、`latitude`、`longitude`、`radius`、`polygon_coords`、`enabled`

### 围栏 — `PUT/DELETE /api/admin/rules/punch-geofences/<geofence_id>`

---

### 打卡规则 — `GET/POST /api/admin/rules/punch-rules`

`GET`: 查询参数 `enabled`、`time_slot_id`、`geofence_id`、`include_deleted`、`page`、`size`
`POST`: 请求体 `time_slot_id`、`geofence_id`、`priority`（默认 100）、`time_enabled`、`location_enabled`、`enabled`

### 打卡规则 — `PUT/DELETE /api/admin/rules/punch-rules/<rule_id>`

---

## 五、考勤记录

### `GET /api/admin/attendance-records`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 否 | 姓名模糊搜索 |
| user_id | string | 否 | 学号精确搜索 |
| start_date | string | 否 | 开始日期 YYYY-MM-DD |
| end_date | string | 否 | 结束日期 YYYY-MM-DD |
| leave_status | string | 否 | pending / approved / rejected |
| page | int | 否 | 默认 1 |
| size | int | 否 | 默认 10 |

### `GET /api/admin/attendance/export`

导出考勤 CSV。参数同 `GET /attendance-records`，不分页。

### `POST /api/admin/attendance-records`（兼容层）

创建考勤记录。请求体 `user_id`（必填）、`punch_date`、`leave_start_date`、`leave_end_date`、`leave_status`。

### `DELETE /api/admin/attendance-records/<record_id>`

---

### 打卡记录 — `POST /api/admin/attendance/punch-records`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 学号 |
| punch_date | string | 否 | 打卡日期 YYYY-MM-DD |
| punch_time | string | 否 | 打卡时间 HH:MM:SS，默认 12:00:00 |
| latitude | float | 否 | 纬度 |
| longitude | float | 否 | 经度 |

### 打卡记录 — `PUT/DELETE /api/admin/attendance/punch-records/<record_id>`

---

### 请假记录 — `POST /api/admin/attendance/leave-records`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 学号 |
| leave_start_date | string | 否 | 请假开始日期 |
| leave_end_date | string | 否 | 请假结束日期 |
| leave_status | string | 否 | 默认 pending |
| leave_type | string | 否 | 默认 personal |
| leave_reason | string | 否 | 请假原因 |

### 请假记录 — `PUT/DELETE /api/admin/attendance/leave-records/<record_id>`

---

## 六、仪表盘 & 配置

### `GET /api/admin/dashboard/stats`

仪表盘聚合数据（总人数、今日打卡率、请假数等）。

### `GET /api/admin/dashboard/trend`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| days | int | 否 | 统计天数，默认 7 |

---

### `GET /api/admin/config`

获取全局打卡配置。

### `PUT /api/admin/config`

更新全局配置。请求体 `global_time_check_enabled`、`global_location_check_enabled` 等。

---

### `GET /api/admin/punch-location`（兼容）

获取打卡位置配置。

### `POST /api/admin/punch-location`（兼容）

设置打卡位置。请求体 `name`、`latitude`、`longitude`、`radius`、`enabled`。

---

## 通用说明

| 项 | 说明 |
|------|------|
| 鉴权 | `Authorization: Bearer <token>` |
| 响应格式 | `{ "code": 200, "message": "success", "data": {...} }` |
| 分页响应 | `{ "code": 200, "data": { "items": [...], "total": N } }` |
| 软删除 | 删除操作标记 `deleted_at`，可通过 `include_deleted=true` 查询 |
| 兼容层 | 标记 `Deprecation: true` + `Sunset: 2026-07-31` 的接口计划下线 |
