# dao/ — 数据访问层

封装所有数据库操作，每个 DAO 对应一张表。DAO 层只包含 SQL 操作，不做业务判断。

## 文件说明

### `__init__.py`
集中导出全部 16 个 DAO 类。

### `base_dao.py`
**抽象基类** — 提供通用的 CRUD 方法，其他 DAO 继承它。

通用方法：
- `get_by_id(id)` — 按主键查单条
- `get_list(where, params, order_by, limit, offset)` — 条件分页查询
- `count(where, params)` — 计数查询
- `create(data)` — 插入
- `update(id, data)` — 更新
- `soft_delete(id)` — 软删除（设 `deleted_at`）

内置防注入：表名、列名、WHERE 关键字、ORDER BY 均有白名单校验`BaseDAO(Generic[T])` 是泛型基类，子类指定对应的 Model 类型后自动获得类型安全。

### `campus_dao.py`
**校区 DAO** — 操作 `campuses` 表。继承 `BaseDAO[Campus]`，无额外自定义方法。

### `department_dao.py`
**院系 DAO** — 操作 `departments` 表。继承 `BaseDAO[Department]`。

### `major_dao.py`
**专业 DAO** — 操作 `majors` 表。继承 `BaseDAO[Major]`。

### `grade_dao.py`
**年级 DAO** — 操作 `grades` 表。继承 `BaseDAO[Grade]`。

### `class_dao.py`
**班级 DAO** — 操作 `classes` 表。继承 `BaseDAO[Class]`。

### `user_dao.py`
**用户 DAO** — 操作 `users` 表。

额外方法：
- `get_by_username(username)` — 按用户名查用户（登录用）
- `get_by_student_id(student_id)` — 按学号查用户
- `count_by_role(role)` — 按角色统计人数
- `create()` / `update()` — 重写以处理密码哈希

### `class_teacher_dao.py`
**教学分配 DAO** — 操作 `class_teachers` 关联表。继承 `BaseDAO[ClassTeacher]`。

### `punch_geofence_dao.py`
**围栏 DAO** — 操作 `punch_geofences` 表。

额外方法：
- `get_enabled_geofences()` — 获取所有启用的围栏（打卡校验时批量查询用）
- `get_first_enabled()` — 获取第一个启用的围栏

### `punch_time_slot_dao.py`
**时段 DAO** — 操作 `punch_time_slots` 表。继承 `BaseDAO[PunchTimeSlot]`。

### `punch_rule_dao.py`
**规则 DAO** — 操作 `punch_rules` 表。继承 `BaseDAO[PunchRule]`。

### `punch_dao.py`
**打卡记录 DAO** — 操作 `punches` 表。

额外方法：
- `get_punch_by_user_and_date(user_id, date)` — 查某用户某天是否已打卡
- `get_punches_by_user(user_id, start_date, end_date)` — 按时间范围查用户打卡
- `count_by_date(date)` — 统计某天打卡人数（去重）

### `leave_dao.py`
**请假 DAO** — 操作 `leaves` 表。

额外方法：
- `get_leave_records_by_user(user_id)` — 查用户请假记录
- `get_pending_leave_applications_by_class(class_name)` — 班级待审批请假
- `update_leave_status(id, status)` — 更新审批状态
- `count_approved_by_date(date)` — 统计当日已批准的请假数

### `makeup_request_dao.py`
**补签 DAO** — 操作 `makeup_requests` 表。

额外方法：
- `get_by_user_and_date(user_id, date)` — 查是否已有补签申请（防重复）
- `get_pending_by_class(class_name)` — 班级待审批补签
- `update_status(id, status)` — 更新审批状态

### `punch_config_dao.py`
**配置 DAO** — 操作 `punch_config` 表（单行配置，ID 恒为 1）。

- `get_config()` — 获取全局配置
- `update(data)` — 更新配置

### `operation_log_dao.py`
**操作日志 DAO** — 操作 `operation_logs` 表。支持传入外部数据库连接以实现事务内写入。

### `notification_dao.py`
**通知 DAO** — 操作 `notifications` 表。

额外方法：
- `mark_as_read(id)` — 标记已读
