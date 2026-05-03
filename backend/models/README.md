# models/ — 数据模型层

纯 `@dataclass` 类，与数据库表字段一一映射。不含任何业务逻辑，仅作为各层间传递数据的结构化载体。

## 文件说明

### `__init__.py`
集中导出全部 16 个 Model 类。

### 组织架构模型

| 文件 | 类 | 对应表 | 字段 |
|------|-----|--------|------|
| `campus.py` | `Campus` | `campuses` | id, name, address, created_at |
| `department.py` | `Department` | `departments` | id, campus_id, name, code, created_at |
| `major.py` | `Major` | `majors` | id, department_id, name, code, created_at |
| `grade.py` | `Grade` | `grades` | id, major_id, year, name, created_at |
| `class_model.py` | `Class` | `classes` | class_name, grade_id, created_at, deleted_at |

层级关系：**校区 → 院系 → 专业 → 年级 → 班级**

### 用户与权限模型

| 文件 | 类 | 对应表 | 字段 |
|------|-----|--------|------|
| `user.py` | `User` | `users` | user_id, username, password, real_name, role, class_name, student_id, phone, email, is_first_login, last_punch_time, login_fail_count, lock_until, last_login_time, last_login_ip, created_at, deleted_at |
| `class_teacher.py` | `ClassTeacher` | `class_teachers` | class_name, teacher_id, semester, created_at, deleted_at |

`User.role` 可选值：`admin`、`teacher`、`monitor`（班委）、`student`。

### 打卡相关模型

| 文件 | 类 | 对应表 | 字段 |
|------|-----|--------|------|
| `punch.py` | `Punch` | `punches` | id, user_id, punch_date, punch_time, latitude, longitude, matched_rule_id, is_makeup, device_id, created_at |
| `punch_geofence.py` | `PunchGeofence` | `punch_geofences` | id, name, fence_type, latitude, longitude, radius, polygon_coords, enabled, created_at, deleted_at |
| `punch_time_slot.py` | `PunchTimeSlot` | `punch_time_slots` | id, name, start_time, end_time, enabled, created_at, deleted_at |
| `punch_rule.py` | `PunchRule` | `punch_rules` | id, time_slot_id, geofence_id, priority, time_enabled, location_enabled, enabled, created_at, deleted_at |
| `punch_config.py` | `PunchConfig` | `punch_config` | id, global_time_check_enabled, global_location_check_enabled, allow_multi_punch, allow_makeup, holiday_ranges, updated_at |

`punch_rules` 通过 `time_slot_id` 和 `geofence_id` 将时段与围栏绑定，`priority` 决定匹配优先级。

### 请假与补签模型

| 文件 | 类 | 对应表 | 字段 |
|------|-----|--------|------|
| `leave.py` | `Leave` | `leaves` | id, user_id, leave_start_date, leave_end_date, leave_type, leave_reason, leave_status, approved_by, approved_at, created_at, deleted_at |
| `makeup_request.py` | `MakeupRequest` | `makeup_requests` | id, user_id, target_date, reason, status, approved_by, approved_at, created_at, deleted_at |

`status` 字段共同值：`pending`（待审批）、`approved`（已通过）、`rejected`（已拒绝）。

### 系统辅助模型

| 文件 | 类 | 对应表 | 字段 |
|------|-----|--------|------|
| `operation_log.py` | `OperationLog` | `operation_logs` | id, operator_id, operation_type, target_type, target_id, before_data, after_data, ip_address, created_at |
| `notification.py` | `Notification` | `notifications` | id, receiver_id, sender_id, title, content, type, is_read, related_id, created_at |
